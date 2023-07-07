from django.urls import path, include
from .views import *


urlpatterns = [
    path('api/register/', Register.as_view()),
    path('api/login/', Login.as_view()),
    path('api/modify/', Modify.as_view()),
    path('api/getmyinfo/', GetMyInfo.as_view()),
    path('api/getkcalstatus/', GetKcalStatus.as_view()),
    path('api/getnutritionstatus/', GetNutritionStatus.as_view()),
    path('api/getselector/', GetExerciseSelector.as_view()),
    path('api/getunitlist/', GetUnitList.as_view())
]