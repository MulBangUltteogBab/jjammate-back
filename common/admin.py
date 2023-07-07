from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(UserAdd)
admin.site.register(UserHealth)
admin.site.register(UserKcalStatus)
admin.site.register(UserNutritionStatus)
admin.site.register(UserTakenFood)
admin.site.register(UserExerciseSelector)