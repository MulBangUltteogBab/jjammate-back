import json
import bcrypt
import jwt
import datetime
import logging

from .models import ExerciseMission, ExerciseSelector, SpecialAgentMaximum
from common.models import User, UserKcalStatus

from .serializer import *
from rest_framework.views import APIView 
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg             import openapi
from config.settings import SECRET_KEY
from core.jsonparser import getJsonValue

from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger('mbub')


class GetGauge(APIView):
    @swagger_auto_schema(tags=['About Exercise'], request_body=GetExerciseGaugeSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.date.today().strftime('%Y-%m-%d')
            kcalstatus = UserKcalStatus.objects.get(key=user, date=date)
            gauge = kcalstatus.burned / 6
            return JsonResponse({"message" : gauge}, status=200)

        except KeyError:
            return JsonResponse({"message" : "NO DATA"}, status=400)


class GetExercise(APIView):
    @swagger_auto_schema(tags=['About Exercise'], request_body=GetExerciseSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.date.today().strftime('%Y-%m-%d')
            if ExerciseMission.objects.filter(key=user, date=date).exist():
                mission = ExerciseMission.objects.get(key=user, date=date)
                exercise = getJsonValue("exercise", "exercise.json")
                info = exercise[mission.option]
                return JsonResponse(info, status=200)

            number = ExerciseSelector.objects.get(key=user).number
            part = getJsonValue("part", "exercise.json")
            option = part[number % 6]
            mission = ExerciseMission.objects.create(
                key = user,
                option = option,
                setcount = 0,
                date = date
            ).save()
            exercise = getJsonValue("exercise", "exercise.json")
            info = exercise[option]
            return JsonResponse(info, status=200)

        except KeyError:
            return JsonResponse({"message" : "NO DATA"}, status=400)


class GetMaximumTime(APIView):
    @swagger_auto_schema(tags=['About Exercise'], request_body=GetMaximumTimeSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            body = {
                "run": 0,
                "pushup": 0,
                "situp": 0
            }
            maximum = SpecialAgentMaximum.objects.get(key=user)
            body["run"] = maximum.run
            body["pushup"] = maximum.pushup
            body["situp"] = maximum.situp
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "KeyError"}, status=400)


# changeSet
class GetSetCount(APIView):
    @swagger_auto_schema(tags=['About Exercise'], request_body=GetSetCountSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.date.today().strftime('%Y-%m-%d')
            mission = ExerciseMission.objects.get(key = user, date = date)
            return JsonResponse(mission.setcount, status=200)

        except KeyError:
            return JsonResponse({"message" : "Key Error"}, status=400)
    
        except:
            return JsonResponse({"message" : "There is no ExerciseMission"}, status=400)


class SetMaximumTime(APIView):
    @swagger_auto_schema(tags=['About Exercise'], request_body=SetMaximumTimeSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            run = data['run']
            pushup = data['pushup']
            situp = data['situp']
            SpecialAgentMaximum.objects.get(key=user).update(
                run = run,
                pushup = pushup,
                situp = situp
            )
            return JsonResponse({"message" : "Done"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "NO DATA"}, status=400)


class SetSetCount(APIView):
    @swagger_auto_schema(tags=['About Exercise'], request_body=SetSetCountSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            setcount = data['setcount']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.date.today().strftime('%Y-%m-%d')
            ExerciseMission.objects.get(key = user, date = date).update(
                setcount = setcount
            )
            if not UserKcalStatus.objects.filter(key=user, date=date).exists():
                UserKcalStatus.objects.create(
                    key = user,
                    burned = 0,
                    taken = 0,
                    date = date
                ).save
            mission = ExerciseMission.objects.get(key=user, date=date)
            exercise = getJsonValue("exercise", "exercise.json")
            kcalstatus = UserKcalStatus.objects.get(key=user, date=date)
            for count in setcount.values() :
                kcalstatus.burned = exercise[mission.option]["burned"] * count
            kcalstatus.save()
            return JsonResponse({"message" : "Done"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "NO DATA"}, status=400)

        except:
            return JsonResponse({"message" : "There is no ExerciseMission"}, status=400)
