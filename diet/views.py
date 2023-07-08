import json
import bcrypt
import jwt
import datetime
import logging
from random import *
from pytz import timezone
from random import randint

from .models import *
from common.models import *

from .serializer import *
from common.serializer import *
from rest_framework.views import APIView 
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg             import openapi
from config.settings import SECRET_KEY
from core.webparser import parsePXFood, getDiet, isValidDate, mappingFoodToNutrient, parsePXFoodPicture
from core.unit import deleteUnit, getUnitNumber
from core.recommend import recommendFunc
from core.decorator import modelsInit

from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import *

logger = logging.getLogger('mbub')


class Recommend(APIView):
    @swagger_auto_schema(
        tags=['About Diet'], 
        request_body=RecommendSerializer,
        responses={
            "200": RecommendSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer
        })
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            useradd = UserAdd.objects.get(key=user)
            military_number = getUnitNumber(useradd.department)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            if UserRecommendPXFood.objects.filter(key=user, date=date).exists():
                recommend = UserRecommendPXFood.objects.get(key=user, date=date)
                return JsonResponse(recommend.pxfoods, status=200)
            
            userhealth = UserHealth.objects.get(key=user)
            diet = Diet.objects.get(military_number = int(military_number), date = date)
            body = {
                "pxfoods": []
            }
            total = {
                "calorie": 0,
                "carbohydrate": 0,
                "protein": 0,
                "fat": 0,
            }
            for breakfast in diet.diet["breakfast"]:
                nutr = Nutrition.objects.filter(name = breakfast)
                if not nutr.exists():
                    total['calorie'] += 100
                else:
                    nutr = Nutrition.objects.get(name = breakfast)
                    total['calorie'] += deleteUnit(nutr.calorie)
                    total['carbohydrate'] += deleteUnit(nutr.carbohydrate)
                    total['protein'] += deleteUnit(nutr.protein)
                    total['fat'] += deleteUnit(nutr.fat)
            for lunch in diet.diet["lunch"]:
                nutr = Nutrition.objects.filter(name = lunch)
                if not nutr.exists():
                    total['calorie'] += 100
                else:
                    nutr = Nutrition.objects.get(name = lunch)
                    total['calorie'] += deleteUnit(nutr.calorie)
                    total['carbohydrate'] += deleteUnit(nutr.carbohydrate)
                    total['protein'] += deleteUnit(nutr.protein)
                    total['fat'] += deleteUnit(nutr.fat)
            for dinner in diet.diet["dinner"]:
                nutr = Nutrition.objects.filter(name = dinner)
                if not nutr.exists():
                    total['calorie'] += 100
                else:
                    nutr = Nutrition.objects.get(name = dinner)
                    total['calorie'] += deleteUnit(nutr.calorie)
                    total['carbohydrate'] += deleteUnit(nutr.carbohydrate)
                    total['protein'] += deleteUnit(nutr.protein)
                    total['fat'] += deleteUnit(nutr.fat)

            pxfoods = PXFood.objects.all()
            for pxfood in pxfoods:
                nutr = Nutrition.objects.get(name = pxfood.name)
                if recommendFunc(nutr, total, userhealth.totalkcal):
                    body['pxfoods'].append({
                            "name": pxfood.name,
                            "calorie": deleteUnit(nutr.calorie),
                            "carbohydrate": deleteUnit(nutr.carbohydrate),
                            "protein": deleteUnit(nutr.protein),
                            "fat": deleteUnit(nutr.fat),
                            "amount": deleteUnit(nutr.amount),
                            "image": pxfood.image.url
                        })
            
            index = []
            for i in range(0, 5-len(body['pxfoods'])):
                idx = randint(0, pxfoods.count() - 1)
                while idx in index:
                    idx = randint(0, pxfoods.count() - 1)
                index.append(idx)

            for i in index:
                nutr = Nutrition.objects.get(name = pxfoods[i].name)
                body['pxfoods'].append({
                    "name": pxfoods[i].name,
                    "calorie": deleteUnit(nutr.calorie),
                    "carbohydrate": deleteUnit(nutr.carbohydrate),
                    "protein": deleteUnit(nutr.protein),
                    "fat": deleteUnit(nutr.fat),
                    "amount": deleteUnit(nutr.amount),
                    "image": pxfoods[i].image.url
                })
            UserRecommendPXFood.objects.create(
                key = user,
                date = date,
                pxfoods = body
            )
                
            return JsonResponse(body, status=200)
        
        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class GetPXFood(APIView):
    @swagger_auto_schema(
        tags=['About Diet'], 
        request_body=GetPXFoodSerializer,
        responses={
            "200": GetPXFoodSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer
        })
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
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)

    
class GetRecommendPXFoodList(APIView):
    @swagger_auto_schema(
        tags=['About Diet'], 
        request_body=GetRecommendPXFoodListSerializer,
        responses={
            "200": GetRecommendPXFoodListSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer
        })
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            begin = data["begin"]
            end = data["end"]
            recommend = UserRecommendPXFood.objects.get(key=user, date=date)
            if begin < end or begin < 0:
                JsonResponse({"message" : "begin은 0과 같거나 커야하고, end는 begin보다 커야합니다."}, status=400)
            if len(recommend.pxfoods) < end:
                end = len(recommend.pxfoods)
            if len(recommend.pxfoods) < begin:
                begin = len(recommend.pxfoods)
            return JsonResponse({"pxfoods": recommend.pxfoods[begin:end]}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class GetPXFoodList(APIView):
    @swagger_auto_schema(
        tags=['About Diet'], 
        request_body=GetPXFoodListSerializer,
        responses={
            "200": GetPXFoodListSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer
        })
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            body = {"pxfoods": []}
            pxfoods = PXFood.objects.all().order_by('id')
            begin = 0
            end = pxfoods.count()
            if ("begin" in data) and ("end" in data):
                begin = data["begin"]
                end = data["end"]
                pxfoods = PXFood.objects.all().order_by('id')
                if begin < end or begin < 0:
                    JsonResponse({"message" : "begin은 0과 같거나 커야하고, end는 begin보다 커야합니다."}, status=400)
                if pxfoods.count() < end:
                    end = pxfoods.count()
                if pxfoods.count() < begin:
                    begin = pxfoods.count()

            pxfoods = pxfoods[begin:end]
            for pxfood in pxfoods:
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
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class GetDiet(APIView):
    @swagger_auto_schema(
        tags=['About Diet'], 
        request_body=GetDietSerializer,
        responses={
            "200": GetDietSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer
        })
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            add = UserAdd.objects.get(key=user)
            military_number = getUnitNumber(add.department)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            diet = Diet.objects.get(military_number = int(military_number), date = date)
            kcalstatus = UserKcalStatus.objects.get(key=user, date=date)
            body = {}
            body['breakfast'] = []
            body['lunch'] = []
            body['dinner'] = []
            for breakfast in diet.diet["breakfast"]:
                if breakfast == "":
                    continue
                nutr = Nutrition.objects.get(name = breakfast)
                if not kcalstatus.isdiet:
                    kcalstatus.taken += deleteUnit(nutr.calorie)
                body['breakfast'].append({
                    "name": breakfast,
                    "calorie": deleteUnit(nutr.calorie),
                    "carbohydrate": deleteUnit(nutr.carbohydrate),
                    "protein": deleteUnit(nutr.protein),
                    "fat": deleteUnit(nutr.fat),
                    "amount": deleteUnit(nutr.amount)
                })
            for lunch in diet.diet["lunch"]:
                if lunch == "":
                    continue
                nutr = Nutrition.objects.get(name = lunch)
                if not kcalstatus.isdiet:
                    kcalstatus.taken += deleteUnit(nutr.calorie)
                body['lunch'].append({
                    "name": lunch,
                    "calorie": deleteUnit(nutr.calorie),
                    "carbohydrate": deleteUnit(nutr.carbohydrate),
                    "protein": deleteUnit(nutr.protein),
                    "fat": deleteUnit(nutr.fat),
                    "amount": deleteUnit(nutr.amount)
                })
            for dinner in diet.diet["dinner"]:
                if dinner == "":
                    continue
                nutr = Nutrition.objects.get(name = dinner)
                if not kcalstatus.isdiet:
                    kcalstatus.taken += deleteUnit(nutr.calorie)
                body['dinner'].append({
                    "name": dinner,
                    "calorie": deleteUnit(nutr.calorie),
                    "carbohydrate": deleteUnit(nutr.carbohydrate),
                    "protein": deleteUnit(nutr.protein),
                    "fat": deleteUnit(nutr.fat),
                    "amount": deleteUnit(nutr.amount)
                })
            kcalstatus.isdiet = True
            kcalstatus.save()
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)
    

class StackDiet(APIView):
    @swagger_auto_schema(
        tags=['About Parsing'], 
        request_body=StackDietSerializer,
        responses={
            "200": StackSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer
        })
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_number = data['military_number']
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
                    if datetime.date.fromisoformat(date) >= datetime.datetime.now(timezone('Asia/Seoul')).date():
                        if date not in mealbydates:
                            mealbydates[date] = {
                                'breakfast': [],
                                'lunch': [],
                                'dinner': []
                            }
                        if diet['brst'] not in mealbydates[date]['breakfast']:
                            mealbydates[date]['breakfast'].append(diet['brst'])
                        if diet['lunc'] not in mealbydates[date]['lunch']:
                            mealbydates[date]['lunch'].append(diet['lunc'])
                        if diet['dinr'] not in mealbydates[date]['dinner']:
                            mealbydates[date]['dinner'].append(diet['dinr'])

                for date in mealbydates:
                    Diet.objects.create(
                        military_number = n,
                        date = date,
                        diet = mealbydates[date],
                    ).save()
                    for meal in mealbydates[date]:
                        logger.info(meal)
                        for diet in mealbydates[date][meal]:
                            logger.info(diet)
                            if diet == "":
                                continue
                            if Nutrition.objects.filter(name = diet).exists():
                                continue
                            nutritiondict, isvaild = mappingFoodToNutrient(diet)
                            if not isvaild:
                                logger.info(diet + " is not vaild")
                                Nutrition.objects.create(
                                    name = diet,
                                    calorie = str(randint(70, 100)) + "kcal",
                                    carbohydrate = str(randint(16, 20)) + "g",
                                    protein = str(randint(9, 13)) + "g",
                                    fat = str(randint(1, 5)) + "g",
                                    amount = "100g"
                                ).save()
                            else:
                                logger.info("Matching nutritiondict")
                                Nutrition.objects.create(
                                    name = diet,
                                    calorie = str(deleteUnit(nutritiondict["calorie"])*(150/deleteUnit(nutritiondict["amount"])))+"kcal",
                                    carbohydrate = str(deleteUnit(nutritiondict["carbohydrate"])*(150/deleteUnit(nutritiondict["amount"])))+"g",
                                    protein = str(deleteUnit(nutritiondict["protein"])*(150/deleteUnit(nutritiondict["amount"])))+"g",
                                    fat = str(deleteUnit(nutritiondict["fat"])*(150/deleteUnit(nutritiondict["amount"])))+"g",
                                    amount = nutritiondict["amount"]
                                ).save()

            return JsonResponse({"message" : "식단표 크롤링 성공"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class StackPXFood(APIView):
    @swagger_auto_schema(
        tags=['About Parsing'],
        responses={
            "200": StackSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer
        })
    @transaction.atomic
    @csrf_exempt
    def get(self, request):
        try:
            pxfoods = parsePXFood()
            for i in range(0, len(pxfoods["name"])):
                if not PXFood.objects.filter(name = pxfoods["name"][i]).exists():
                    imagepos = parsePXFoodPicture(pxfoods["name"][i])
                    PXFood.objects.create(
                        name = pxfoods["name"][i],
                        price = pxfoods["price"][i],
                        manufacturer = pxfoods["manufacturer"][i],
                        amount = pxfoods["amount"][i],
                        image = imagepos
                    ).save()
                    logger.info("pxfood: {}".format(pxfoods["name"][i]))
                if not Nutrition.objects.filter(name = pxfoods["name"][i]).exists():
                    nutritiondict, isvaild = mappingFoodToNutrient(pxfoods["name"][i])
                    if not isvaild:
                        Nutrition.objects.create(
                            name = pxfoods["name"][i],
                            calorie = str(randint(70, 100)) + "kcal",
                            carbohydrate = str(randint(16, 20)) + "g",
                            protein = str(randint(9, 13)) + "g",
                            fat = str(randint(1, 5)) + "g",
                            amount = "100g"
                        ).save()
                        continue
                    Nutrition.objects.create(
                        name = pxfoods["name"][i],
                        calorie = nutritiondict["calorie"],
                        carbohydrate = nutritiondict["carbohydrate"],
                        protein = nutritiondict["protein"],
                        fat = nutritiondict["fat"],
                        amount = nutritiondict["amount"]
                    ).save()

            return JsonResponse({"message" : "PX 상품 크롤링 성공"}, status=200)
                    
        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class SetTakenFood(APIView):
    @swagger_auto_schema(
        tags=['About Diet'], 
        request_body=SetTakenFoodSerializer,
        responses={
            "200": SetTakenFoodSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer
        })
    @transaction.atomic
    @csrf_exempt
    @modelsInit
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            foodname = data['food']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            food = Nutrition.objects.get(name=foodname)
            UserTakenFood.objects.create(
                key = user,
                date = date,
                food = food
            )

            taken = deleteUnit(Nutrition.objects.get(name=foodname).calorie)
            kcalstatus = UserKcalStatus.objects.get(key=user, date=date)
            kcalstatus.taken += taken
            kcalstatus.save()

            return JsonResponse({"message" : "먹은 음식 갱신 성공"}, status=200)
                    
        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)
        

    @swagger_auto_schema(
        tags=['About Diet'], 
        request_body=DelTakenFoodSerializer,
        responses={
            "200": SetTakenFoodSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer
        })
    @transaction.atomic
    @csrf_exempt
    def delete(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            foodname = data['food']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            food = Nutrition.objects.get(name=foodname)
            taken = deleteUnit(Nutrition.objects.get(name=foodname).calorie)
            kcalstatus = UserKcalStatus.objects.get(key=user, date=date)
            kcalstatus.taken -= taken
            kcalstatus.save()

            taken = UserTakenFood.objects.filter(
                key = user,
                date = date,
                food = food
            ).last()
            taken.delete()

            return JsonResponse({"message" : "먹은 음식 갱신 성공"}, status=200)
                    
        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class GetTakenFood(APIView):
    @swagger_auto_schema(
        tags=['About Diet'], 
        request_body=GetTakenFoodSerializer,
        responses={
            "200": GetTakenFoodSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer
        })
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            takenfood = UserTakenFood.objects.filter(key=user, date=date)
            body = {'taken': []}
            for food in takenfood:
                pxfood = PXFood.objects.get(name=food.food.name)
                body['taken'].append({
                    "name": food.food.name,
                    "calorie": deleteUnit(food.food.calorie),
                    "carbohydrate": deleteUnit(food.food.carbohydrate),
                    "protein": deleteUnit(food.food.protein),
                    "fat": deleteUnit(food.food.fat),
                    "amount": deleteUnit(food.food.amount),
                    "image": pxfood.image.url
                })

            return JsonResponse(body, status=200)
                    
        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)
