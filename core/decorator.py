import logging
import datetime
from pytz import timezone

from common.models import *
from diet.models import *
from exercise.models import *

logger = logging.getLogger('mbub')

def modelsInit(func):
    logger.info("Model init Check")
    def wrapper(self, request):
        logger.info("Model Check...")
        data = request.data
        military_serial_number = data['military_serial_number']
        date = datetime.datetime.now(timezone('Asia/Seoul')).date().strftime('%Y-%m-%d')
        user = User.objects.get(military_serial_number = military_serial_number)
        if not UserKcalStatus.objects.filter(key=user, date=date).exists():
            UserKcalStatus.objects.create(
                key = user,
                burned = 0,
                taken = 0,
                date = date
            ).save()
        if not UserNutritionStatus.objects.filter(key=user, date=date).exists():
            UserNutritionStatus.objects.create(
                key = user,
                date = date,
                carbohydrate = 0,
                protein = 0,
                fat = 0
            ).save()
        return func(self, request)
    return wrapper