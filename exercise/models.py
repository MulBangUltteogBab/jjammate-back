from django.db import models
from common.models import User


class ExerciseMission(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    option = models.CharField(max_length=60)
    setcount = models.JSONField()
    # {
    #     "운동A": 0,
    #     "운동B": 1
    # }
    date = models.DateField()


class ExerciseSelector(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    number = models.SmallIntegerField()


class SpecialAgentMaximum(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    run = models.CharField(max_length=10)
    pushup = models.CharField(max_length=10)
    situp = models.CharField(max_length=10)
