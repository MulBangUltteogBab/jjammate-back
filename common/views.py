import json
import bcrypt
import jwt
import logging
import datetime

from .models import *
from exercise.models import *
from diet.models import *

from config.settings import SECRET_KEY
from rest_framework.views import APIView 
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg             import openapi
from .serializer import *

from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt


class Register(APIView):
    @swagger_auto_schema(tags=['User'], request_body=RegisterSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            if User.objects.filter(military_serial_number = data['military_serial_number']).exists():
                return JsonResponse({"message" : "EXISTS_MILITARY_SERIAL_NUMBER"}, status=400)
            # if UserAdd.objects.filter(nickname = data['nickname']).exists():
            #     return JsonResponse({"message" : "EXISTS_NICKNAME"}, status=400)
            
            date = datetime.date.today().strftime('%Y-%m-%d')
            user = User.objects.create(
                military_serial_number 	 = data['military_serial_number'], 
                password = bcrypt.hashpw(
                    data["password"].encode("UTF-8"), 
                    bcrypt.gensalt()
                ).decode("UTF-8"),
            )
            add = UserAdd.objects.create(
                key = user,
                # nickname = data['nickname'],
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
                bmi = data['weight']/((data['height']/100)**2)
            )
            selector = ExerciseSelector.objects.create(
                key = user,
                number = 0
            )
            maximum = SpecialAgentMaximum.objects.create(
                key = user,
                run = "00:00",
                pushup = "0",
                situp = "0"
            )
            kcalstatus = UserKcalStatus.objects.create(
                key = user,
                burned = 0,
                taken = 0,
                date = date
            )
            user.save()
            add.save()
            health.save()
            selector.save()
            maximum.save()

            return HttpResponse(status=200)
            
        except KeyError:
            return JsonResponse({"message" : "INVALID_KEYS"}, status=400)


class Login(APIView):
    @swagger_auto_schema(tags=['User'], request_body=LoginSerializer)
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
                return HttpResponse(status=401)
            return HttpResponse(status=400)
        
        except KeyError:
            return JsonResponse({'message' : "INVALID_KEYS"}, status=400)


class Modify(APIView):
    @swagger_auto_schema(tags=['User'], request_body=ModifySerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            if not User.objects.filter(military_serial_number = data['military_serial_number']).exists():
                return JsonResponse({"message" : "NOT_EXISTS_MILITARY_SERIAL_NUMBER"}, status=400)
            
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            
            if "password" in data:
                user.password = bcrypt.hashpw(
                    data["password"].encode("UTF-8"), 
                    bcrypt.gensalt()
                ).decode("UTF-8")
                user.save()
            if "username" in data:
                UserAdd.objects.get(key=user).update(
                    username = data['username']
                )
            if "department" in data:
                UserAdd.objects.get(key=user).update(
                    department = data['department']
                )
            if ("height" in data) or ("weight" in data):
                health = UserHealth.objects.get(key=user)
                if "height" in data:
                    health.height = data['height']
                    health.bmi = health.weight/((data['height']/100)**2)
                if "weight" in data:
                    health.weight = data['weight']
                    health.bmi = data['weight']/((health.height/100)**2)
                health.save()

            return HttpResponse(status=200)
            
        except KeyError:
            return JsonResponse({"message" : "INVALID_KEYS"}, status=400)
        

class GetMyInfo(APIView):
    @swagger_auto_schema(tags=['User'], request_body=GetMyInfoSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            date = datetime.date.today().strftime('%Y-%m-%d')
            user = User.objects.get(military_serial_number = military_serial_number)
            add = UserAdd.objects.get(key=user)
            health = UserHealth.objects.get(key=user)
            status = UserKcalStatus.objects.get(key=user, date=date)
            body = {
                "military_serial_number": military_serial_number,
                # "nickname": add.nickname,
                "username": add.username,
                "department": add.department,
                "sex": add.sex,
                "age": add.age,
                "height": health.height,
                "weight": health.weight,
                "bmi": health.bmi,
                "taken": status.taken,
                "burned": status.burned
            }
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "INVALID_KEYS"}, status=400)