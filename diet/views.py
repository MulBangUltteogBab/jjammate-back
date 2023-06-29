import json
import bcrypt
import jwt
import datetime
import logging

from .models import PXFood, Diet, Nutrition
from .serializer import *
from rest_framework.views import APIView 
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg             import openapi
from config.settings import SECRET_KEY
from core.webparser import parsePXFood, getDiet, isValidDate, mappingFoodToNutrient, parsePXFoodPicture

from django.views import View
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger('mbub')


class Recommend(APIView):
    @swagger_auto_schema(tags=['not implement'], request_body=RecommendSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        return JsonResponse({"message" : "not implement"}, status=400)


# search with name
class GetPXFood(APIView):
    @swagger_auto_schema(tags=['About PXFood'], request_body=GetPXFoodSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            name = data['name']
            pxfoods = PXFood.objects.all()
            body = {
                "pxfoods": []
            }
            for pxfood in pxfoods:
                if pxfood.name.find(data['name']) != -1:
                    nutr = Nutrition.objects.filter(name = pxfood.name)
                    if not nutr.exists():
                        body['pxfoods'].append({
                            "name": pxfood.name,
                            "calorie": "",
                            "carbohydrate": "",
                            "protein": "",
                            "fat": "",
                            "amount":"",
                            "image": ""
                        })
                    else:
                        nutr = Nutrition.objects.get(name = pxfood.name)
                        body['pxfoods'].append({
                            "name": pxfood.name,
                            "calorie": nutr.calorie,
                            "carbohydrate": nutr.carbohydrate,
                            "protein": nutr.protein,
                            "fat": nutr.fat,
                            "amount": nutr.amount,
                            "image": pxfood.image.url
                        })
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "NO DATA"}, status=400)


class GetDiet(APIView):
    @swagger_auto_schema(tags=['About Diet'], request_body=GetDietSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_number = data['military_number']
            date = datetime.date.today().strftime('%Y-%m-%d')
            diet = Diet.objects.get(military_number = military_number, date = date)
            body = {}
            body['breakfast'] = []
            body['lunch'] = []
            body['dinner'] = []
            for breakfast in diet.diet["breakfast"]:
                nutr = Nutrition.objects.filter(name = breakfast)
                if not nutr.exists():
                    body['breakfast'].append({
                        "name": breakfast,
                        "calorie": "",
                        "carbohydrate": "",
                        "protein": "",
                        "fat": "",
                        "amount":""
                    })
                else:
                    nutr = Nutrition.objects.get(name = breakfast)
                    body['breakfast'].append({
                        "name": breakfast,
                        "calorie": nutr.calorie,
                        "carbohydrate": nutr.carbohydrate,
                        "protein": nutr.protein,
                        "fat": nutr.fat,
                        "amount": nutr.amount
                    })
            for lunch in diet.diet["lunch"]:
                nutr = Nutrition.objects.filter(name = lunch)
                if not nutr.exists():
                    body['lunch'].append({
                        "name": lunch,
                        "calorie": "",
                        "carbohydrate": "",
                        "protein": "",
                        "fat": "",
                        "amount":""
                    })
                else:
                    nutr = Nutrition.objects.get(name = lunch)
                    body['lunch'].append({
                        "name": lunch,
                        "calorie": nutr.calorie,
                        "carbohydrate": nutr.carbohydrate,
                        "protein": nutr.protein,
                        "fat": nutr.fat,
                        "amount": nutr.amount
                    })
            for dinner in diet.diet["dinner"]:
                nutr = Nutrition.objects.filter(name = dinner)
                if not nutr.exists():
                    body['dinner'].append({
                        "name": dinner,
                        "calorie": "",
                        "carbohydrate": "",
                        "protein": "",
                        "fat": "",
                        "amount":""
                    })
                else:
                    nutr = Nutrition.objects.get(name = dinner)
                    body['dinner'].append({
                        "name": dinner,
                        "calorie": nutr.calorie,
                        "carbohydrate": nutr.carbohydrate,
                        "protein": nutr.protein,
                        "fat": nutr.fat,
                        "amount": nutr.amount
                    })
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "NO DATA"}, status=400)
    

class StackDiet(APIView):
    @swagger_auto_schema(tags=['About Diet'], request_body=StackDietSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_number = data['military_number']
            today = datetime.date.today()
            for n in military_number:
                logger.info("military_number: {}".format(n))
                diets = getDiet(n)
                mealbydates = {}
                for diet in diets:
                    date = diet['dates'][:-3]
                    if not isValidDate(date):
                        continue
                    if Diet.objects.filter(military_number = n, date = date).exists():
                        continue
                    if datetime.date.fromisoformat(date) >= datetime.date.today():
                        if date not in mealbydates:
                            mealbydates[date] = {
                                'breakfast': [],
                                'lunch': [],
                                'dinner': []
                            }
                        mealbydates[date]['breakfast'].append(diet['brst'])
                        mealbydates[date]['lunch'].append(diet['lunc'])
                        mealbydates[date]['dinner'].append(diet['dinr'])

                for date in mealbydates:
                    Diet.objects.create(
                        military_number = n,
                        date = date,
                        diet = mealbydates[date],
                    ).save()
            
                for meal in mealbydates[date]:
                    for diet in mealbydates[date][meal]:
                        if diet == "":
                            continue
                        if Nutrition.objects.filter(name = diet).exists():
                            continue
                        nutritiondict, isvaild = mappingFoodToNutrient(diet)
                        if not isvaild:
                            logger.info(diet + " is not vaild")
                            continue
                        logger.info("Matching nutritiondict")
                        Nutrition.objects.create(
                            name = diet,
                            calorie = nutritiondict["calorie"],
                            carbohydrate = nutritiondict["carbohydrate"],
                            protein = nutritiondict["protein"],
                            fat = nutritiondict["fat"],
                            amount = nutritiondict["amount"]
                        ).save()

            return JsonResponse({"message" : "Stack Well"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "NO DATA"}, status=400)


class StackPXFood(APIView):
    @swagger_auto_schema(tags=['About PXFood'])
    @transaction.atomic
    @csrf_exempt
    def get(self, request):
        try:
            pxfoods = parsePXFood()
            for i in range(0, len(pxfoods["name"])):
                imagepos = parsePXFoodPicture(pxfoods["name"][i])
                PXFood.objects.create(
                    name = pxfoods["name"][i],
                    price = pxfoods["price"][i],
                    manufacturer = pxfoods["manufacturer"][i],
                    amount = pxfoods["amount"][i],
                    image = imagepos
                ).save()
                logger.info("pxfood: {}".format(pxfoods["name"][i]))
                if Nutrition.objects.filter(name = pxfoods["name"][i]).exists():
                    continue
                nutritiondict, isvaild = mappingFoodToNutrient(pxfoods["name"][i])
                if not isvaild:
                    continue
                Nutrition.objects.create(
                    name = pxfoods["name"][i],
                    calorie = nutritiondict["calorie"],
                    carbohydrate = nutritiondict["carbohydrate"],
                    protein = nutritiondict["protein"],
                    fat = nutritiondict["fat"],
                    amount = nutritiondict["amount"]
                ).save()

            return JsonResponse({"message" : "Done"}, status=200)
                    
        except KeyError:
            return JsonResponse({"message" : "NO DATA"}, status=400)
