def deleteUnit(string):
    if 'g' in string:
        return string[:-1]
    else:
        return string[:-4]
