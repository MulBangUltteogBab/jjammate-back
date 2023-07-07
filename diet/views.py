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
from rest_framework.views import APIView 
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg             import openapi
from config.settings import SECRET_KEY
from core.webparser import parsePXFood, getDiet, isValidDate, mappingFoodToNutrient, parsePXFoodPicture
from core.unit import deleteUnit, getUnitNumber
from core.recommend import recommend

from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import *

logger = logging.getLogger('mbub')


class Recommend(APIView):
    @swagger_auto_schema(tags=['About Diet'], request_body=RecommendSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_number = getUnitNumber(data['military_number'])
            user = User.objects.get(military_number = military_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
            if UserRecommendPxFood.objects.filter(key=user, date=date).exists():
                recommend = UserRecommendPxFood.objects.get(key=user, date=date)
                return JsonResponse(recommend.pxfoods, status=200)
            
            userhealth = UserHealth.objects.get(key=user)
            diet = Diet.objects.get(military_number = military_number, date = date)
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
                    total['calorie'] += int(deleteUnit(nutr.calorie))
                    total['carbohydrate'] += int(deleteUnit(nutr.carbohydrate))
                    total['protein'] += int(deleteUnit(nutr.protein))
                    total['fat'] += int(deleteUnit(nutr.fat))
            for lunch in diet.diet["lunch"]:
                nutr = Nutrition.objects.filter(name = lunch)
                if not nutr.exists():
                    total['calorie'] += 100
                else:
                    nutr = Nutrition.objects.get(name = lunch)
                    total['calorie'] += int(deleteUnit(nutr.calorie))
                    total['carbohydrate'] += int(deleteUnit(nutr.carbohydrate))
                    total['protein'] += int(deleteUnit(nutr.protein))
                    total['fat'] += int(deleteUnit(nutr.fat))
            for dinner in diet.diet["dinner"]:
                nutr = Nutrition.objects.filter(name = dinner)
                if not nutr.exists():
                    total['calorie'] += 100
                else:
                    nutr = Nutrition.objects.get(name = dinner)
                    total['calorie'] += int(deleteUnit(nutr.calorie))
                    total['carbohydrate'] += int(deleteUnit(nutr.carbohydrate))
                    total['protein'] += int(deleteUnit(nutr.protein))
                    total['fat'] += int(deleteUnit(nutr.fat))

            pxfoods = PXFood.objects.all()
            for pxfood in pxfoods:
                nutr = Nutrition.objects.filter(name = pxfood.name)
                if recommend(nutr, total, userhealth.totalkcal):
                    body['pxfoods'].append({
                            "name": pxfood.name,
                            "calorie": nutr.calorie,
                            "carbohydrate": nutr.carbohydrate,
                            "protein": nutr.protein,
                            "fat": nutr.fat,
                            "amount": nutr.amount,
                            "image": pxfood.image.url
                        })
            
            index = []
            for i in range(0, 3-len(body['pxfoods'])):
                idx = randint(0, pxfoods.count())
                while idx in index:
                    idx = randint(0, pxfoods.count())
                index.append(idx)

            for i in index:
                nutr = Nutrition.objects.filter(name = pxfood[i].name)
                body['pxfoods'].append({
                            "name": pxfood[i].name,
                            "calorie": nutr.calorie,
                            "carbohydrate": nutr.carbohydrate,
                            "protein": nutr.protein,
                            "fat": nutr.fat,
                            "amount": nutr.amount,
                            "image": pxfood[i].image.url
                        })
            UserRecommendPxFood.objects.create(
                key = user,
                date = date,
                pxfoods = body['pxfoods']
            )
                
            return JsonResponse(body, status=200)
        
        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)


class GetPXFood(APIView):
    @swagger_auto_schema(tags=['About Diet'], request_body=GetPXFoodSerializer)
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
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)

    
class GetPxFoodList(APIView):
    @swagger_auto_schema(tags=['About Diet'], request_body=GetPXFoodListSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_number = getUnitNumber(data['military_number'])
            user = User.objects.get(military_number = military_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
            begin = data["begin"]
            end = data["end"]
            recommend = UserRecommendPxFood.objects.get(key=user, date=date)
            if begin < end or begin < 0:
                JsonResponse({"message" : "begin은 0과 같거나 커야하고, end는 begin보다 커야합니다."}, status=400)
            if len(recommend.pxfoods) < end:
                end = pxfoods.count()
            if len(recommend.pxfoods) < begin:
                begin = pxfoods.count()
            return JsonResponse({"pxfoods": recommend.pxfoods[begin:end]}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)

class GetDiet(APIView):
    @swagger_auto_schema(tags=['About Diet'], request_body=GetDietSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_number = getUnitNumber(data['military_number'])
            date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
            diet = Diet.objects.get(military_number = military_number, date = date)
            body = {}
            body['breakfast'] = []
            body['lunch'] = []
            body['dinner'] = []
            for breakfast in diet.diet["breakfast"]:
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
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)
    

class GetGauge(APIView):
    @swagger_auto_schema(tags=['About Diet'], request_body=GetDietGaugeSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            userhealth = UserHealth.objects.get(key=user)
            date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
            kcalstatus = UserKcalStatus.objects.get(key=user, date=date)
            gauge = kcalstatus.taken / userhealth.totalkcal * 100
            return JsonResponse({"gauge" : gauge}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)


class StackDiet(APIView):
    @swagger_auto_schema(tags=['About Parsing'], request_body=StackDietSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_number = getUnitNumber(data['military_number'])
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
                    if datetime.date.fromisoformat(date) >= datetime.datetime.now(timezone('Asia/Seoul')):
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
                            Nutrition.objects.create(
                                name = diet,
                                calorie = "%dkcal".format(randint(70, 100)),
                                carbohydrate = "%dg".format(randint(16, 20)),
                                protein = "%d".format(randint(9, 13)),
                                fat = "%d".format(randint(1, 5)),
                                amount = ""
                            ).save()
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

            return JsonResponse({"message" : "식단표 크롤링 성공"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)


class StackPXFood(APIView):
    @swagger_auto_schema(tags=['About Parsing'])
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
                            calorie = "%dkcal".format(randint(70, 100)),
                            carbohydrate = "%dg".format(randint(16, 20)),
                            protein = "%d".format(randint(9, 13)),
                            fat = "%d".format(randint(1, 5)),
                            amount = ""
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
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)


class SetTakenFood(APIView):
    @swagger_auto_schema(tags=['About Diet'], request_body=SetTakenFoodSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            foodlist = data['foodlist']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
            if not UserTakenFood.objects.filter(key=user, date=date).exists():
                UserTakenFood.objects.create(
                    key = user,
                    date = date,
                    foodlist = {
                        "pxfood":[],
                        "diet":[]
                    }
                )
            taken = 0
            for key in foodlist:
                for foodname in foodlist[key]:
                    taken += int(deleteUnit(Nutrition.objects.get(name=foodname).calorie))
            
            UserKcalStatus.objects.get(key=user, date=date).update(taken=taken)
            UserTakenFood.objects.get(key=user, date=date).update(foodlist=foodlist)

            return JsonResponse({"message" : "먹은 음식 갱신 성공"}, status=200)
                    
        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)


class GetTakenFood(APIView):
    @swagger_auto_schema(tags=['About Diet'], request_body=GetTakenFoodSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
            if not UserTakenFood.objects.filter(key=user, date=date).exists():
                UserTakenFood.objects.create(
                    key = user,
                    date = date,
                    foodlist = {
                        "pxfood":[],
                        "diet":[]
                    }
                )
            body = UserTakenFood.objects.get(key=user, date=date).foodlist

            return JsonResponse(body, status=200)
                    
        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)
