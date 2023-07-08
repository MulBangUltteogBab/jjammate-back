import json
import bcrypt
import jwt
import logging
import datetime
from pytz import timezone
from difflib import SequenceMatcher

from .models import *
from exercise.models import *
from diet.models import *

from config.settings import SECRET_KEY
from rest_framework.views import APIView 
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg             import openapi
from .serializer import *
from core.jsonparser import getJsonValue
from core.decorator import modelsInit

from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import *

logger = logging.getLogger('mbub')


class Register(APIView):
    @swagger_auto_schema(
        tags=['User'], 
        request_body=RegisterSerializer, 
        responses={
            "200": RegisterSuccessResponseSerializer,
            "400": RegisterFail1ResponseSerializer,
            "401": KeyErrorResponseSerializer
        })
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            if User.objects.filter(military_serial_number = data['military_serial_number']).exists():
                return JsonResponse({"message" : "이미 존재하는 회원입니다."}, status=400)
            
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            bmi = data['weight']/((data['height']/100)**2)
            user = User.objects.create(
                military_serial_number 	 = data['military_serial_number'], 
                password = bcrypt.hashpw(
                    data["password"].encode("UTF-8"), 
                    bcrypt.gensalt()
                ).decode("UTF-8"),
            )
            add = UserAdd.objects.create(
                key = user,
                username = data['username'],
                department = data['department'],
                sex = data['sex'],
                age = data['age'],
                agreement = data["agreement"]
            )
            health = UserHealth.objects.create(
                key = user,
                height = data['height'],
                weight = data['weight'],
                bmi = bmi,
                totalkcal = 3100 - (bmi - 20.75) * 43.3
            )
            selector = UserExerciseSelector.objects.create(
                key = user,
                number = 0
            )
            kcalstatus = UserKcalStatus.objects.create(
                key = user,
                burned = 0,
                taken = 0,
                isdiet = False,
                date = date
            )
            nutritionstatus = UserNutritionStatus.objects.create(
                key = user,
                date = date,
                isdiet = False,
                carbohydrate = 0,
                protein = 0,
                fat = 0
            )
            user.save()
            add.save()
            health.save()
            selector.save()
            kcalstatus.save()
            nutritionstatus.save()
            return JsonResponse({"message" : "회원가입에 성공하셨습니다."}, status=200)
            
        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ZeroDivisionError:
            return JsonResponse({"message" : "키나 몸무게 중 0인 값이 있습니다."}, status=402)


class Login(APIView):
    @swagger_auto_schema(
        tags=['User'], 
        request_body=LoginSerializer,
        responses={
            "200": LoginSuccessResponseSerializer,
            "400": LoginErrorSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer
        })
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            if User.objects.filter(military_serial_number = data["military_serial_number"]).exists():
                user = User.objects.get(military_serial_number = data["military_serial_number"])
                useradd = UserAdd.objects.get(key=user)
                userhealth = UserHealth.objects.get(key=user)
                if bcrypt.checkpw(data['password'].encode('UTF-8'), user.password.encode('UTF-8')):
                    token = jwt.encode({
                        'key': user.key,
                        'military_serial_number': user.military_serial_number,
                        'username': useradd.username,
                        'department': useradd.department,
                        'sex': useradd.sex,
                        'age': useradd.age,
                        'height': userhealth.height,
                        'weight': userhealth.weight,
                        'bmi': userhealth.bmi
                    }, SECRET_KEY, algorithm='HS256')
                    return JsonResponse({"token" : token}, status=200)
            return JsonResponse({'message' : "회원 정보가 존재하지 않거나 비밀번호가 틀렸습니다."}, status=400)
        
        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)
        
        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class Modify(APIView):
    @swagger_auto_schema(
        tags=['User'], 
        request_body=ModifySerializer,
        responses={
            "200": ModifySuccessSerializer,
            "400": LoginErrorSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer,
            "403": ZeroDivisionErrorSerializer
        })
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            if not User.objects.filter(military_serial_number = data['military_serial_number']).exists():
                return JsonResponse({"message" : "회원 정보가 존재하지 않거나 비밀번호가 틀렸습니다."}, status=400)
            
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            add = UserAdd.objects.get(key=user)
            
            if "password" in data:
                user.password = bcrypt.hashpw(
                    data["password"].encode("UTF-8"), 
                    bcrypt.gensalt()
                ).decode("UTF-8")
                user.save()
            if "username" in data:
                add.username = data['username']
            if "department" in data:
                add.department = data['department']
            if ("height" in data) or ("weight" in data):
                health = UserHealth.objects.get(key=user)
                if "height" in data and "weight" in data:
                    health.height = data['height']
                    bmi = data['weight']/((data['height']/100)**2)
                    health.bmi = bmi
                    health.totalkcal = 3100 - (bmi - 20.75) * 43.3
                if "height" in data and "weight" not in data:
                    health.height = data['height']
                    bmi = health.weight/((data['height']/100)**2)
                    health.bmi = bmi
                    health.totalkcal = 3100 - (bmi - 20.75) * 43.3
                if "weight" in data and "height" not in data:
                    health.weight = data['weight']
                    bmi = data['weight']/((health.height/100)**2)
                    health.bmi = bmi
                    health.totalkcal = 3100 - (bmi - 20.75) * 43.3
                health.save()
            add.save()

            return JsonResponse({"message" : "수정 완료"}, status=200)
            
        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ZeroDivisionError:
            return JsonResponse({"message" : "키나 몸무게 중 0인 값이 있습니다."}, status=403)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)
        

class GetMyInfo(APIView):
    @swagger_auto_schema(
        tags=['User'], 
        request_body=GetMyInfoSerializer,
        responses={
            "200": GetMyInfoSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer,
        })
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            logger.info(data)
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            add = UserAdd.objects.get(key=user)
            health = UserHealth.objects.get(key=user)
            body = {
                "military_serial_number": military_serial_number,
                "username": add.username,
                "department": add.department,
                "sex": add.sex,
                "age": add.age,
                "height": health.height,
                "weight": health.weight,
                "bmi": health.bmi
            }
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class GetKcalStatus(APIView):
    @swagger_auto_schema(
        tags=['User'], 
        request_body=GetKcalStatusSerializer,
        responses={
            "200": GetKcalStatusSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer,
        })
    @transaction.atomic
    @csrf_exempt
    @modelsInit
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            user = User.objects.get(military_serial_number = military_serial_number)
            status = UserKcalStatus.objects.get(key=user, date=date)
            userhealth = UserHealth.objects.get(key=user)
            
            body = {
                "taken": int(status.taken),
                "burned": int(status.burned),
                "remain": int(userhealth.totalkcal - status.taken),
                "total": int(userhealth.totalkcal)
            }
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class GetNutritionStatus(APIView):
    @swagger_auto_schema(
        tags=['User'], 
        request_body=GetNutritionStatusSerializer,
        responses={
            "200": GetNutritionStatusSuccessSerializer,
            "401": KeyErrorResponseSerializer,
            "402": NoDBErrorSerializer,
            "403": ZeroDivisionErrorSerializer
        })
    @transaction.atomic
    @csrf_exempt
    @modelsInit
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            user = User.objects.get(military_serial_number = military_serial_number)
            nutritionstatus = UserNutritionStatus.objects.get(key=user, date=date)
            total = getJsonValue('total', 'nutrition.json')
            
            body = {
                "taken": {
                    "carbohydrate": int(nutritionstatus.carbohydrate),
                    "protein": int(nutritionstatus.protein),
                    "fat": int(nutritionstatus.fat),
                },
                "percent": {
                    "carbohydrate": int(nutritionstatus.carbohydrate/total['carbohydrate']*100),
                    "protein": int(nutritionstatus.protein/total['protein']*100),
                    "fat": int(nutritionstatus.fat/total['fat']*100),
                },
                "total": {
                    "carbohydrate": int(total['carbohydrate']),
                    "protein": int(total['protein']),
                    "fat": int(total['fat']),
                }
            }
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)

        except ZeroDivisionError:
            return JsonResponse({"message" : "키나 몸무게 중 0인 값이 있습니다."}, status=403)


class GetExerciseSelector(APIView):
    @swagger_auto_schema(
        tags=['User'], 
        request_body=GetExerciseSelectorSerializer,
        responses={
            "200": GetExerciseSelectorSuccessSerializer,
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
            selector = UserExerciseSelector.objects.get(key=user)
            return JsonResponse({"days": selector.number}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)
    

class GetUnitList(APIView):
    @swagger_auto_schema(
        tags=['User'], 
        request_body=GetUnitListSerializer,
        responses={
            "200": GetUnitListSuccessSerializer,
            "401": KeyErrorResponseSerializer,
        })
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            name = data["unique"]
            unitlist = getJsonValue("unit", 'unit.json')
            units = []
            for unit in unitlist:
                ratio = SequenceMatcher(None, name, unit["unique"]).ratio()
                if ratio >= 0.5:
                    units.append(unit["unique"])
            body = {
                "unit": units
            }
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)
