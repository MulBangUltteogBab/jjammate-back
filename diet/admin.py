from django.contrib import admin
from .models import PXFood, Diet, DietFood

# Register your models here.
admin.site.register(PXFood)
admin.site.register(Diet)
admin.site.register(DietFood)