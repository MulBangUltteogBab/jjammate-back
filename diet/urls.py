from django.urls import path, include
from .views import *


urlpatterns = [
    path('api/getpxfood/', GetPXFood.as_view()),
    path('api/getdiet/', GetDiet.as_view()),
    path('api/recommend/', Recommend.as_view()),
    path('api/stackdiet/', StackDiet.as_view()),
    path('api/stackpxfood/', StackPXFood.as_view()),
    path('api/getgauge/', GetGauge.as_view()),
    path('api/gettakenfood/', GetTakenFood.as_view()),
    path('api/settakenfood/', SetTakenFood.as_view()),
    path('api/getpxfoodlist/', GetPxFoodList.as_view()),
]