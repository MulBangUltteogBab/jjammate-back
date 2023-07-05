def ratingOfRun(run, age):
    timelist = run.split(':')
    m = int(timelist[0])
    s = int(timelist[1])
    total = m*60 + s
    if age <= 25:
        if total <= 750:
            return 0
        elif 751 <= total <= 782:
            return 1
        elif 783 <= total <= 874:
            return 2
        elif 875 <= total <= 936:
            return 3
        else:
            return 4
    else:
        if total >= 765:
            return 0
        elif 766 <= total <= 832:
            return 1
        elif 833 <= total <= 899:
            return 2
        elif 900 <= total <= 966:
            return 3
        else:
            return 4


def ratingOfPushup(pushup, age):
    if age <= 25:
        if pushup >= 72:
            return 0
        elif 64 <= pushup <= 71:
            return 1
        elif 56 <= pushup <= 63:
            return 2
        elif 48 <= pushup <= 55:
            return 3
        else:
            return 4
    else:
        if pushup >= 70:
            return 0
        elif 62 <= pushup <= 69:
            return 1
        elif 54 <= pushup <= 61:
            return 2
        elif 46 <= pushup <= 53:
            return 3
        else:
            return 4


def ratingOfSitup(situp, age):
    if age <= 25:
        if situp >= 86:
            return 0
        elif 78 <= situp <= 85:
            return 1
        elif 70 <= situp <= 77:
            return 2
        elif 62 <= situp <= 69:
            return 3
        else:
            return 4
    else:
        if situp >= 84:
            return 0
        elif 76 <= situp <= 83:
            return 1
        elif 68 <= situp <= 75:
            return 2
        elif 60 <= situp <= 67:
            return 3
        else:
            return 4