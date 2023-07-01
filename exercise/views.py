import json
import bcrypt
import jwt
import datetime
import logging

from .serializer import *
from rest_framework.views import APIView 
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg             import openapi
from config.settings import SECRET_KEY

from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger('mbub')


class GetGauge(APIView):
    @swagger_auto_schema(tags=['not implement'], request_body=GetExerciseGaugeSerializer)
    @transaction.atomic
    @csrf_exempt
    def post(self, request):
        data = request.data
        try:
            military_serial_number = data['military_serial_number']
            return JsonResponse({"message" : "Not Implement"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "NO DATA"}, status=400)
