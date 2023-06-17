from django.contrib import admin
from .models import User, UserAdd, UserHealth

# Register your models here.
admin.site.register(User)
admin.site.register(UserAdd)
admin.site.register(UserHealth)