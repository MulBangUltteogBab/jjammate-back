from django.urls import path, include
from .views import *


urlpatterns = [
    path('api/register/', Register.as_view()),
    path('api/login/', Login.as_view()),
    path('api/modify/', Modify.as_view()),
    path('api/getmyinfo/', GetMyInfo.as_view())
]