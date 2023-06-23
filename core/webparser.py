import re
import json
import logging
import requests as req

from fatsecret import Fatsecret
from bs4 import BeautifulSoup

from .jsonparser import getJsonValue
from .papago import korToEng

# print(json.dumps(json, indent=3, ensure_ascii=False))

url = 'https://tsar1004.blogspot.com/2020/05/px.html'

consumer_key = getJsonValue("FATSECRET_CONSUMER_KEY")
consumer_secret = getJsonValue("FATSECRET_CONSUMER_SECRET")
manufacturer = getJsonValue("MANUFACTURER")

logger = logging.getLogger('mbub')
KEY = getJsonValue('DIET-KEY')
TYPE = 'json'
START_INDEX = '1'
END_INDEX = '1'


def getDiet(military_num):
    SERVICE = 'DS_TB_MNDT_DATEBYMLSVC_' + str(military_num)
    data = sendReq(SERVICE)
    index = data['list_total_count']
    data = sendReq(SERVICE, end_index=str(index))
    return data['row']


def sendReq(service, end_index=END_INDEX):
    res = req.get('https://openapi.mnd.go.kr/' + KEY + '/' + TYPE + '/' + service + '/' + START_INDEX + '/' + end_index + '/')
    jsondata = res.json()
    return jsondata[service]


def isValidDate(date):
    regex = r'\d{4}-\d{2}-\d{2}'
    return bool(re.match(regex, date))


def parsePXFood():
    res = req.get(url)
    try:
        if res.status_code == 200:
            html = res.text
            soup = BeautifulSoup(html, 'html.parser')
            board = soup.select_one('#post-body-3744595533532631851')
            tds = board.find_all('td')
            tds = tds[2:]
            pxfooddict = {
                "manufacturer": [],
                "name": [],
                "amount": [],
                "price": []
            }
            for i in range(0, len(tds), 4):
                if tds[i].text in manufacturer:
                    pxfooddict["manufacturer"].append(tds[i].text)
                    pxfooddict["name"].append(tds[i+1].text)
                    pxfooddict["amount"].append(tds[i+2].text)
                    pxfooddict["price"].append(tds[i+3].text)
            return pxfooddict
        return None

    except:
        raise


def mappingFoodToNutrient(food):
    try:
        fs = Fatsecret(consumer_key, consumer_secret)
        engfood = korToEng(food)
        nutrition = fs.foods_search(engfood)
        logger.info("{} : {}".format(food, engfood))
        proc = re.compile('([0-9]+ ?g)|([0-9]+\.[0-9]+ ?g)|([0-9]+ ?kcal)')

        nu = proc.findall(nutrition[0]['food_description'])
        nulist = []
        for idx in nu:
            for data in idx:
                if data != '':
                    nulist.append(data)
        logger.info("Matching nutritiondict")
        return {
            "amount": nulist[0], 
            "calorie": nulist[1], 
            "fat": nulist[2], 
            "carbohydrate": nulist[3], 
            "protein": nulist[4]
        }, True
    
    except KeyError as e:
        logger.info("KeyError")
        return {}, False

    except Exception as e:
        logger.info("Exception")
        return {}, False
        


#def parsePXFoodPicture(pxfoodname):

# def getPXFood():
#     SERVICE = 'DS_MND_PX_PARD_PRDT_INFO'
#     data = sendReq(SERVICE)
#     index = data['list_total_count']
#     data = sendReq(SERVICE, end_index=index)
#     return data[row]
