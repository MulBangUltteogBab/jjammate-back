from .unit import deleteUnit

def recommand(pxfood, total):
    if (total['calorie'] + int(deleteUnit(pxfood.calorie)) >= 2800) and nutrientRatio(pxfood, total):
        return True
    return False


def nutrientRatio(pxfood, total):
    sumofnutr = total['carbohydrate'] + int(deleteUnit(pxfood.carbohydrate)) + total['protein'] + int(deleteUnit(pxfood.protein)) + total['fat'] + int(deleteUnit(pxfood.fat))
    ratiocar = (total['carbohydrate'] + int(deleteUnit(pxfood.carbohydrate))) / sumofnutr * 100 
    ratiopro = (total['protein'] + int(deleteUnit(pxfood.protein))) / sumofnutr * 100 
    ratiofat = (total['fat'] + int(deleteUnit(pxfood.fat))) / sumofnutr * 100 
    if (35 <= ratiocar <= 60) and (5 <= ratiopro <= 30) and (20 <= ratiofat <= 45):
        return True
    return False
