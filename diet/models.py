from django.db import models

class PXFood(models.Model):
    name = models.CharField(max_length=60, primary_key=True)
    sellyear = models.SmallIntegerField()
    sellmonth = models.SmallIntegerField()
    image = models.ImageField()

class Diet(models.Model):
    military_number = models.SmallIntegerField()
    date = models.DateField()
    diet = models.JSONField()
    '''
    {
        "breakfast": [...],
        "lunch": [...],
        "dinner": [...]
    }
    '''

class DietFood(models.Model):
    name = models.CharField(max_length=60, primary_key=True)
    calorie = models.SmallIntegerField()
    carbohydrate = models.SmallIntegerField()
    protein = models.SmallIntegerField()
    fat = models.SmallIntegerField()