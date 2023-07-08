from django.urls import path, include
from .views import *


urlpatterns = [
    path('api/getexercise/', GetExercise.as_view()),
    path('api/setsetcount/', SetSetCount.as_view()),
    path('api/getsetcount/', GetSetCount.as_view()),
    path('api/setruncount/', SetRunCount.as_view()),
    path('api/getruncount/', GetRunCount.as_view()),
    path('api/setpushupcount/', SetPushupCount.as_view()),
    path('api/getpushupcount/', GetPushupCount.as_view()),
    path('api/setsitupcount/', SetSitupCount.as_view()),
    path('api/getsitupcount/', GetSitupCount.as_view()),
    path('api/getweekrecordtime/', GetWeekRecordTime.as_view()),
]