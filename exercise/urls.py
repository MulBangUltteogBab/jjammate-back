from django.urls import path, include
from .views import *


urlpatterns = [
    path('api/getgauge/', GetGauge.as_view()),
    path('api/getexercise/', GetExercise.as_view()),
    path('api/getrecordtime/', GetRecordTime.as_view()),
    path('api/setrecordtime/', SetRecordTime.as_view()),
    path('api/setsetcount/', SetSetCount.as_view()),
    path('api/getsetcount/', GetSetCount.as_view()),
    path('api/getweekrecordtime/', GetWeekRecordTime.as_view()),
]