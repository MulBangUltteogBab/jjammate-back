from django.urls import path, include
from .views import Register, Login


urlpatterns = [
    path('api/register/', Register.as_view()),
    path('api/login/', Login.as_view()),
]