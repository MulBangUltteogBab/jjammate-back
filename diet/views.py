import json
import bcrypt
import jwt
import datetime

from .models import PXFood, Diet, DietFood
from config.settings import SECRET_KEY
from rest_framework.views import APIView 
from drf_yasg.utils       import swagger_auto_schema
from drf_yasg             import openapi
from .serializer import *
from core.publicdata import getDiet, isValidDate

from django.views import View
from django.http import HttpResponse, JsonResponse
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max


class Recommend(APIView):
    @swagger_auto_schema(tags=['Recommend PXFood'], request_body=RecommendSerializer)
    @transaction.atomic
    def post(self, request):
        data = request.data
        return JsonResponse({"message" : "not implement"}, status=400)


class GetDiet(APIView):
    @swagger_auto_schema(tags=['Get Diet Data'], request_body=GetDietSerializer)
    @transaction.atomic
    def post(self, request):
        data = request.data
        try:
            military_number = data['military_number']
            date = data['date'] # just get today?
            diet = Diet.objects.filter(military_number = mili_num, date = date)
            body = {}
            body['breakfast'] = diet.breakfast
            body['lunch'] = diet.lunch
            body['dinner'] = diet.dinner
            return JsonResponse(body, status=200)

        except KeyError:
            return JsonResponse({"message" : "NO DATA"}, status=400)


# search with name
# smiliarity check is not ready...
class GetPXFood(APIView):
    @swagger_auto_schema(tags=['Get PXFood Data'], request_body=GetPXFoodSerializer)
    @transaction.atomic
    def post(self, request):
        data = request.data
        try:
            name = data['name']
            pxfood = PXFood.objects.get(name=name).values()
            return JsonResponse(pxfood, status=200)

        except KeyError:
            return JsonResponse({"message" : "NO DATA"}, status=400)


class StackDiet(APIView):
    @swagger_auto_schema(tags=['Stack Diet Data'], request_body=StackDietSerializer)
    @transaction.atomic
    def post(self, request):
        data = request.data
        try:
            military_number = data['military_number']
            today = datetime.date.today()
            for n in military_number:
                diets = getDiet(n)
                mealbydates = {}
                for diet in diets:
                    date = diet['dates'][:-3]
                    if not isValidDate(date):
                        continue
                    if Diet.objects.filter(military_number = n, date = date).exists():
                        continue
                    if datetime.date.fromisoformat(date) >= datetime.date.today():
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
                    diet = Diet.objects.create(
                        military_number = n,
                        date = date,
                        diet = mealbydates[date],
                    ).save()
            
            return JsonResponse({"message" : "Stack Well"}, status=200)

        except KeyError:
            return JsonResponse({"message" : "NO DATA"}, status=400)


# class StackPXFood(APIView):
#     @swagger_auto_schema(tags=['Stack PXFood Data'], request_body=StackDataSerializer)
#     @transaction.atomic
#     def post(self, request):
#         data = json.loads(request.body)
#         try:
#             pxfoods = getPXFood()
#             recents = []
#             if data['mod'] == 'year':
#                 today = datetime.date.today()
#                 y = int(today.year)
#                 m = int(today.month)
#                 for item in pxfoods:
#                     if int(item['sellyear']) == y-1 and int(item['sellmonth']) > m:
#                         recents.append(item)
#                     elif int(item['sellyear']) == y and int(item['sellmonth']) <= m:
#                         recents.append(item)

#             elif data['mod'] == 'continue':
#                 sellyear = YourModel.objects.aggregate(sellyear=Max('sellyear'))['sellyear']
#                 sellyear_data = YourModel.objects.filter(sellyear=sellyear)
#                 sellmonth = sellyear_data.aggregate(sellmonth=Max('sellmonth'))['sellmonth']
#                 result = sellyear_data.filter(sellmonth=sellmonth)
#                 y = int(result.sellyear)
#                 m = int(result.sellmonth)
#                 for item in pxfoods:
#                     if int(item['sellyear']) >= y and int(item['sellmonth']) >= m:
#                         recents.append(item)

#             for recent in recents:
#                 PXFood.objects.create(
#                     name = data['prdtnm'],
#                     sellyear = data['sellyear'],
#                     sellmonth = data['sellmonth'],
#                 ).save()

#             return JsonResponse({"message" : "Done"}, status=200)
                    
#         except KeyError:
#             return JsonResponse({"message" : "NO DATA: year"}, status=400)
#         except:
#             return JsonResponse({"message" : "Error in Server"}, status=400)
