import json
import bcrypt
import jwt

from .models import User, UserAdd, UserHealth
from config.settings import SECRET_KEY

from django.views import View
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError


class Register(View):
    def post(request):
        data = json.loads(request.body)
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
            ).save()
            UserAdd.objects.create(
                key = user,
                nickname = data['nickname'],
                user_name = data['username'],
                department = data['department'],
                sex = data['sex'],
                age = data['age'],
            ).save()
            UserHealth.objects.create(
                key = user,
                height = data['height'],
                weight = data['weight'],
            ).save()

            return HttpResponse(status=200)
            
        except KeyError:
            return JsonResponse({"message" : "INVALID_KEYS"}, status=400)


class Login(View):
    def login(request):
        data = json.loads(request.body)

        try:
            if User.objects.filter(military_serial_number = data["military_serial_number"]).exists():
                user = User.objects.get(military_serial_number = data["military_serial_number"])

                if bcrypt.checkpw(data['password'].encode('UTF-8'), user.password.encode('UTF-8')):
                    token = jwt.encode({'user' : user.key}, SECRET_KEY, algorithm='HS256').decode('UTF-8')
                    return JsonResponse({"token" : token}, status=200)

                return HttpResponse(status=401)

            return HttpResponse(status=400)
        
        except KeyError:
            return JsonResponse({'message' : "INVALID_KEYS"}, status=400)

