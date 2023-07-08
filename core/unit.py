from .jsonparser import getJsonValue

def deleteUnit(string):
    if 'g' in string:
        return float(string[:-1])
    else:
        return float(string[:-4])


def getUnitNumber(string):
    units = getJsonValue("unit", "unit.json")
    for unit in units:
        if unit["unique"] == string:
            return unit["common"]