from django.db import models
from common.models import User


class ExerciseMission(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    date = models.DateField()
    exercise = models.JSONField()


class RunRecord(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    date = models.DateField()
    run = models.CharField(max_length=10)
    runresult = models.CharField(max_length=1)


class PushupRecord(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    date = models.DateField()
    pushup = models.SmallIntegerField()
    pushupresult = models.CharField(max_length=1)


class SitupRecord(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    date = models.DateField()
    situp = models.SmallIntegerField()
    situpresult = models.CharField(max_length=1)


class ExerciseRecord(models.Model):
    key = models.ForeignKey(User, on_delete=models.CASCADE, db_column='key')
    date = models.DateField()
    name = models.CharField(max_length=60)
    