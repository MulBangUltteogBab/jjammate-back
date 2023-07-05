from django.db import models
from common.models import User


class ExerciseMission(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    date = models.DateField()
    exercise = models.CharField(max_length=60)
    setcount = models.JSONField()
    # {
    #     "운동A": 0,
    #     "운동B": 1
    # }


class SpecialAgentRecord(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    date = models.DateField()
    run = models.CharField(max_length=10)
    runresult = models.CharField(max_length=1)
    pushup = models.SmallIntegerField()
    pushupresult = models.CharField(max_length=1)
    situp = models.SmallIntegerField()
    situpresult = models.CharField(max_length=1)
