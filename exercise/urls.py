from django.urls import path, include
from .views import GetGauge


urlpatterns = [
    path('api/getgauge/', GetGauge.as_view())
]