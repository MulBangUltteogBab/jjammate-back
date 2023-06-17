from django.urls import path, include
from .views import StackDiet, GetPXFood, GetDiet, Recommend


urlpatterns = [
    path('api/getpxfood/', GetPXFood.as_view()),
    path('api/getdiet/', GetDiet.as_view()),
    path('api/recommend/', Recommend.as_view()),
    path('api/stackdiet/', StackDiet.as_view()),
]