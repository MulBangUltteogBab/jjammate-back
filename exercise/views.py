import json
import bcrypt
import jwt
import datetime
import logging
from random import *
from pytz import timezone

from .models import *
from common.models import *

from .serializer import *
from common.serializer import *
from rest_framework.views import APIView 
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg             import openapi
from config.settings import SECRET_KEY
from core.jsonparser import getJsonValue
from core.exercise import *
from core.decorator import modelsInit

from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import *

logger = logging.getLogger('mbub')


class GetExercise(APIView):
    @swagger_auto_schema(
        tags=['About Exercise'], 
        request_body=GetExerciseSerializer,
        responses={
            "200": GetExerciseSuccessSerializer,
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
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            if ExerciseMission.objects.filter(key=user, date=date).exists():
                mission = ExerciseMission.objects.get(key=user, date=date)
                exercise = mission.exercise
                return JsonResponse(exercise, status=200)

            body = {
                "data": [
                    
                ] 
            }

            exercise = getJsonValue("exercise", "exercise.json")
            index = 0
            for tag in exercise:
                data = {
                    'title': '',
                    'tag': '',
                    'part': "",
                    'explains': [],
                }
                data['id'] = index
                data['tag'] = tag
                data['part'] = exercise[tag]['part']
                data['done'] = False
                data['burned'] = exercise[tag]['burned']
                options = exercise[tag]["options"]
                idx = randint(0, len(options) - 1)
                count = 0
                for key in options.keys():
                    if count == idx:
                        data['title'] = key
                        data['explains'] = options[key]
                    count += 1
                body["data"].append(data)
                index += 1

            mission = ExerciseMission.objects.create(
                key = user,
                date = date,
                exercise = body,
            ).save()

            selector = UserExerciseSelector.objects.get(key=user)
            selector.number += 1
            selector.save()

            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class SetExercise(APIView):
    @swagger_auto_schema(
        tags=['About Exercise'], 
        request_body=SetExerciseSerializer)
    @transaction.atomic
    @csrf_exempt
    @modelsInit
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            index = data['id']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            mission = ExerciseMission.objects.get(key = user, date = date)
            for option in mission.exercise['data']:
                if option['id'] == index:
                    option['done'] == True
                    kcalstatus = UserKcalStatus.objects.get(key=user, date=date)
                    kcalstatus.burned += option['burned'] * 4
                    kcalstatus.save()
            mission.save()
            return JsonResponse({"message" : "세트 수행 업로드 완료"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


# changeSet
class GetSetCount(APIView):
    @swagger_auto_schema(
        tags=['About Exercise'], 
        request_body=GetSetCountSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            records = ExerciseRecord.objects.filter(key = user, date = date)
            body = {
                "data": []
            }
            for record in records:
                body["data"].append(record.name)

            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class SetSetCount(APIView):
    @swagger_auto_schema(
        tags=['About Exercise'], 
        request_body=SetSetCountSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            name = data['name']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
            ExerciseRecord.objects.create(
                key = user,
                date = date,
                name = name
            ).save()
            return JsonResponse({"message" : "세트 수행 업로드 완료"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class GetWeekRecordTime(APIView):
    @swagger_auto_schema(
        tags=['About Exercise'], 
        request_body=GetWeekRecordTimeSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            today = datetime.datetime.now(timezone('Asia/Seoul')).date()
            body = {
                "record": {}
            }
            for i in range(0, 7):
                totalpushup = 0
                totalsitup = 0
                totalrun = 0
                date = today - datetime.timedelta(days=i + 1)
                date = date.strftime('%Y-%m-%d')
                body["record"][date] = {}
                if not RunRecord.objects.filter(key=user, date=date).exists():
                    body["record"][date]['run'] = "00:00"
                else:
                    records = RunRecord.objects.filter(key=user, date=date)
                    for record in records:
                        time = record.run.split(':')
                        totalrun += int(time[0]) * 60
                        totalrun += int(time[1])
                        aver = int(totalrun / records.count())
                    body["record"][date]['run'] = str(aver // 60) + ":" + str(aver % 60)
                if not PushupRecord.objects.filter(key=user, date=date).exists():
                    body["record"][date]['pushup'] = 0
                else:
                    records = PushupRecord.objects.filter(key=user, date=date)
                    for record in records:
                        totalpushup += record.pushup
                    body["record"][date]['pushup'] = totalpushup / records.count()  
                if not SitupRecord.objects.filter(key=user, date=date).exists():
                    body["record"][date]['situp'] = 0
                else:
                    records = SitupRecord.objects.filter(key=user, date=date)
                    for record in records:
                        totalsitup += record.situp
                    body["record"][date]['situp'] = totalsitup / records.count()  

            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class SetRunCount(APIView):
    @swagger_auto_schema(
        tags=['About Exercise'], 
        request_body=SetRunCountSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            add = UserAdd.objects.get(key=user)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date()
            RunRecord.objects.create(
                key = user,
                date = date,
                run = data['run'],
                runresult = ratingOfRun(data['run'], add.age)
            ).save()
            return JsonResponse({"message" : "저장 완료"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class GetRunCount(APIView):
    @swagger_auto_schema(
        tags=['About Exercise'], 
        request_body=GetCountSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date()
            if not RunRecord.objects.filter(key=user, date=date).exists():
                body = {
                    "run": "00:00",
                    "runresult": 4
                }
            else:
                record = RunRecord.objects.filter(key=user, date=date).last()
                body = {
                    "run": record.run,
                    "runresult": record.runresult
                }
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class SetPushupCount(APIView):
    @swagger_auto_schema(
        tags=['About Exercise'], 
        request_body=SetPushupCountSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            add = UserAdd.objects.get(key=user)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date()
            PushupRecord.objects.create(
                key = user,
                date = date,
                pushup = data['pushup'],
                pushupresult = ratingOfPushup(data['pushup'], add.age)
            ).save()
            return JsonResponse({"message" : "저장 완료"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class GetPushupCount(APIView):
    @swagger_auto_schema(
        tags=['About Exercise'], 
        request_body=GetCountSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date()
            if not PushupRecord.objects.filter(key=user, date=date).exists():
                body = {
                    "pushup": 0,
                    "pushupresult": 4
                }
            else:
                record = PushupRecord.objects.filter(key=user, date=date).last()
                body = {
                    "pushup": record.pushup,
                    "pushupresult": record.pushupresult
                }
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class SetSitupCount(APIView):
    @swagger_auto_schema(
        tags=['About Exercise'], 
        request_body=SetSitupCountSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            add = UserAdd.objects.get(key=user)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date()
            SitupRecord.objects.create(
                key = user,
                date = date,
                situp = data['situp'],
                situpresult = ratingOfSitup(data['situp'], add.age)
            ).save()
            return JsonResponse({"message" : "저장 완료"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)


class GetSitupCount(APIView):
    @swagger_auto_schema(
        tags=['About Exercise'], 
        request_body=GetCountSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).date()
            if not SitupRecord.objects.filter(key=user, date=date).exists():
                body = {
                    "situp": 0,
                    "situpresult": 4
                }
            else:
                record = SitupRecord.objects.filter(key=user, date=date).last()
                body = {
                    "situp": record.situp,
                    "situpresult": record.situpresult
                }
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=401)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=402)
