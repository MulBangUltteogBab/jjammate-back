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
            date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
            kcalstatus = UserKcalStatus.objects.get(key=user, date=date)
            gauge = kcalstatus.burned / 6
            return JsonResponse({"gauge" : gauge}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)


class GetExercise(APIView):
    @swagger_auto_schema(tags=['About Exercise'], request_body=GetExerciseSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
            if not UserKcalStatus.objects.filter(key=user, date=date).exists():
                UserKcalStatus.objects.create(
                    key = user,
                    burned = 0,
                    taken = 0,
                    date = date
                ).save
            if ExerciseMission.objects.filter(key=user, date=date).exists():
                mission = ExerciseMission.objects.get(key=user, date=date)
                exercise = mission.exercise
                return JsonResponse(exercise, status=200)

            exercise = getJsonValue("exercise", "exercise.json")
            for part in exercise:
                options = exercise[part]["options"].keys()
                idx = randint(0, len(options))
                selected = exercise[part]["options"][options[idx]]
                exercise[part]["options"] = {}
                exercise[part]["options"][options[idx]] = selected

            setcount = {}
            for part in exercise:
                setcount[part] = 0

            mission = ExerciseMission.objects.create(
                key = user,
                date = date,
                exercise = exercise,
                setcount = setcount,
            ).save()

            selector = UserExerciseSelector.objects.get(key=user)
            selector.number += 1
            selector.save()

            return JsonResponse(exercise, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)


class GetRecordTime(APIView):
    @swagger_auto_schema(tags=['About Exercise'], request_body=GetRecordTimeSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
            user = User.objects.get(military_serial_number = military_serial_number)
            record = SpecialAgentRecord.objects.filter(key=user, date=date).order_by('-id')
            body = {
                "run": record[0].run,
                "runresult": record[0].runresult,
                "pushup": record[0].pushup,
                "pushupresult": record[0].pushupresult,
                "situp": record[0].situp,
                "situpresult": record[0].situpresult
            }
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)


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
            date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
            mission = ExerciseMission.objects.get(key = user, date = date)
            return JsonResponse(mission.setcount, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)


class SetRecordTime(APIView):
    @swagger_auto_schema(tags=['About Exercise'], request_body=SetRecordTimeSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            useradd = UserAdd.objects.get(key=user)
            date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
            SpecialAgentRecord.objects.create(
                date = date,
                run = data['run'],
                runresult = ratingOfRun(data['run'], useradd.age),
                pushup = data['pushup'],
                pushupresult = ratingOfPushup(data['pushup'], useradd.age),
                situp = data['situp'],
                situpresult = ratingOfSitup(data['situp'], useradd.age)
            )
            return JsonResponse({"message" : "새로운 기록 갱신 성공"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)


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
            date = datetime.datetime.now(timezone('Asia/Seoul')).strftime('%Y-%m-%d')
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
            total = 0
            for done in setcount:
                for part in exercise:
                    for option in exercise[part]["options"]:
                        if option == done:
                            total += exercise[part]["burned"] * setcount[done]
            kcalstatus.burned = total
            kcalstatus.save()
            return JsonResponse({"message" : "세트 수행 횟수 갱신 완료"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)


class GetWeekRecordTime(APIView):
    @swagger_auto_schema(tags=['About Exercise'], request_body=GetWeekRecordTimeSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            user = User.objects.get(military_serial_number = military_serial_number)
            today = datetime.datetime.now(timezone('Asia/Seoul'))
            body = {
                "record": {}
            }
            for i in range(0, 7):
                totalpushup = 0
                totalsitup = 0
                totalrun = 0
                date = today - datetime.timedelta(days=i + 1)
                date = date.strftime('%Y-%m-%d')
                records = SpecialAgentRecord.objects.filter(key=user, date=date)
                for record in records:
                    totalpushup += record.pushup
                    totalsitup += record.situp
                    time = record.run.split(':')
                    totalrun += int(time[0]) * 60
                    totalrun += int(time[1])
                totalrun = totalrun // records.count()
                body["record"][date] = {
                    "pushup": totalpushup / records.count(),
                    "situp": totalsitup / records.count(),
                    "run": "%d:%d".format(totalrun//60, totalrun%60)
                }
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "받지 못한 데이터가 존재합니다."}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message" : "데이터가 존재하지 않습니다."}, status=400)
