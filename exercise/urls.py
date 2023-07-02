from django.urls import path, include
from .views import GetGauge, GetExercise, SetSetCount, GetMaximumTime, SetMaximumTime


urlpatterns = [
    path('api/getgauge/', GetGauge.as_view()),
    path('api/getexercise/', GetExercise.as_view()),
    path('api/getmaximumtime/', GetMaximumTime.as_view()),
    path('api/setmaximumtime/', SetMaximumTime.as_view()),
    path('api/setsetcount/', SetSetCount.as_view())
]