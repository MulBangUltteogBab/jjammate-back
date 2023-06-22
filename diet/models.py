from django.db import models


class PXFood(models.Model):
    name = models.CharField(max_length=60, primary_key=True)
    price = models.SmallIntegerField()
    manufacturer = models.CharField(max_length=60)
    image = models.ImageField()
    amount = models.CharField(max_length=10)


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


class Nutrition(models.Model):
    name = models.CharField(max_length=60, primary_key=True)
    calorie = models.CharField(max_length=10)
    # kcal is unit
    carbohydrate = models.CharField(max_length=10)
    protein = models.CharField(max_length=10)
    fat = models.CharField(max_length=10)
    amount = models.CharField(max_length=10)