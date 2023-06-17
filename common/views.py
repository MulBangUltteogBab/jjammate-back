import json
import bcrypt
import jwt

from .models import User, UserAdd, UserHealth
from config.settings import SECRET_KEY
from rest_framework.views import APIView 
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg             import openapi
from .serializer import *

from django.views import View
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.db import transaction


class Register(APIView):
    @swagger_auto_schema(tags=['User Register'], request_body=RegisterSerializer)
    @transaction.atomic
    def post(self, request):
        data = request.data
        try:
            if User.objects.filter(military_serial_number = data['military_serial_number']).exists():
                return JsonResponse({"message" : "EXISTS_MILITARY_SERIAL_NUMBER"}, status=400)
            if UserAdd.objects.filter(nickname = data['nickname']).exists():
                return JsonResponse({"message" : "EXISTS_NICKNAME"}, status=400)
            
            user = User.objects.create(
                military_serial_number 	 = data['military_serial_number'], 
                password = bcrypt.hashpw(
                    data["password"].encode("UTF-8"), 
                    bcrypt.gensalt()
                ).decode("UTF-8"),
            )
            add = UserAdd.objects.create(
                key = user,
                nickname = data['nickname'],
                username = data['username'],
                department = data['department'],
                sex = data['sex'],
                age = data['age'],
            )
            health = UserHealth.objects.create(
                key = user,
                height = data['height'],
                weight = data['weight'],
            )
            user.save()
            add.save()
            health.save()

            return HttpResponse(status=200)
            
        except KeyError:
            return JsonResponse({"message" : "INVALID_KEYS"}, status=400)


class Login(APIView):
    @swagger_auto_schema(tags=['User Login'], request_body=LoginSerializer)
    @transaction.atomic
    def post(self, request):
        data = request.data

        try:
            if User.objects.filter(military_serial_number = data["military_serial_number"]).exists():
                user = User.objects.get(military_serial_number = data["military_serial_number"])

                if bcrypt.checkpw(data['password'].encode('UTF-8'), user.password.encode('UTF-8')):
                    token = jwt.encode({'user' : user.key}, SECRET_KEY, algorithm='HS256')
                    return JsonResponse({"token" : token}, status=200)

                return HttpResponse(status=401)

            return HttpResponse(status=400)
        
        except KeyError:
            return JsonResponse({'message' : "INVALID_KEYS"}, status=400)

