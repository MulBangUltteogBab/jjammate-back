from .unit import deleteUnit

def recommendFunc(pxfood, total, totalkcal):
    if (total['calorie'] + float(deleteUnit(pxfood.calorie)) >= totalkcal) and nutrientRatio(pxfood, total):
        return True
    return False


def nutrientRatio(pxfood, total):
    sumofnutr = total['carbohydrate'] + float(deleteUnit(pxfood.carbohydrate)) + total['protein'] + float(deleteUnit(pxfood.protein)) + total['fat'] + float(deleteUnit(pxfood.fat))
    ratiocar = (total['carbohydrate'] + float(deleteUnit(pxfood.carbohydrate))) / sumofnutr * 100 
    ratiopro = (total['protein'] + float(deleteUnit(pxfood.protein))) / sumofnutr * 100 
    ratiofat = (total['fat'] + float(deleteUnit(pxfood.fat))) / sumofnutr * 100 
    if (35 <= ratiocar <= 60) and (5 <= ratiopro <= 30) and (20 <= ratiofat <= 45):
        return True
    return False
