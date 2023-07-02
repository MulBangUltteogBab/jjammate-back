from django.db import models


class User(models.Model):
    key = models.AutoField(primary_key=True)
    military_serial_number = models.CharField(max_length=15, unique=True) #id
    password = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class UserAdd(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    nickname = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=20)
    department = models.CharField(max_length=60)
    sex = models.CharField(max_length=1) #'m', 'f'
    age = models.SmallIntegerField()


class UserHealth(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    height = models.IntegerField()
    weight = models.IntegerField()
    bmi = models.FloatField()


class UserKcalStatus(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    burned = models.FloatField()
    taken = models.FloatField()
    date = models.DateField()
