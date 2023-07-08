from django.db import models
from diet.models import *


class User(models.Model):
    key = models.AutoField(primary_key=True)
    military_serial_number = models.CharField(max_length=15, unique=True) #id
    password = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserAdd(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    username = models.CharField(max_length=20)
    department = models.CharField(max_length=60)
    sex = models.CharField(max_length=1) #'m', 'f'
    age = models.SmallIntegerField()
    agreement = models.BooleanField()


class UserHealth(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    height = models.IntegerField()
    weight = models.IntegerField()
    bmi = models.FloatField()
    totalkcal = models.IntegerField()


class UserKcalStatus(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    date = models.DateField()
    burned = models.FloatField()
    isdiet = models.BooleanField()
    taken = models.FloatField()


class UserNutritionStatus(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    date = models.DateField()
    isdiet = models.BooleanField()
    carbohydrate = models.FloatField()
    protein = models.FloatField()
    fat = models.FloatField()


class UserTakenFood(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    date = models.DateField()
    food = models.ForeignKey(Nutrition, on_delete=models.PROTECT, db_column='nutr')


class UserExerciseSelector(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    number = models.SmallIntegerField()


class UserRecommendPXFood(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    date = models.DateField()
    pxfoods = models.JSONField()
    '''
    {
        "pxfood": []
    }
    '''