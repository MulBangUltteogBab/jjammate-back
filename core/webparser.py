import re
import os
import json
import logging
import requests as req

from fatsecret import Fatsecret
from bs4 import BeautifulSoup

from .jsonparser import getJsonValue
from .papago import korToEng

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import quote_plus
from urllib.request import urlretrieve
from time import sleep


# print(json.dumps(json, indent=3, ensure_ascii=False))

url = 'https://tsar1004.blogspot.com/2020/05/px.html'
picture = 'https://search.naver.com/search.naver?where=image&query='

consumer_key = getJsonValue("FATSECRET_CONSUMER_KEY")
consumer_secret = getJsonValue("FATSECRET_CONSUMER_SECRET")
manufacturer = getJsonValue("MANUFACTURER")

logger = logging.getLogger('mbub')
KEY = getJsonValue('DIET-KEY')
TYPE = 'json'
START_INDEX = '1'
END_INDEX = '1'
imagedir = 'image/'

options = webdriver.ChromeOptions()
options.add_argument('--headless')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.implicitly_wait(5)


def makeDir(path):
    if not os.path.exists(path):
        os.makedirs(path)


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
        


def parsePXFoodPicture(pxfoodname):
    makeDir('image')
    try:
        logger.info("{} in parsePXFoodPicture".format(pxfoodname))
        query = quote_plus(pxfoodname, safe='')
        naverurl = picture + query
        for i in range(0, 7):
            if checkandsaveImgTag(i, pxfoodname, naverurl):
                return pxfoodname + ".jpg"
        return ''

    except Exception as e:
        logger.info("parsePXFoodPicture error")
        raise


def checkandsaveImgTag(n, pxfoodname, naverurl):
    try:
        driver.get(naverurl)
        img = driver.find_element(By.XPATH, '/html/body/div[3]/div[2]/div/div[1]/section['+ str(n) +']/div/div[1]/div[1]/div[1]/div/div[1]/a/img')
        imgUrl = img.get_attribute('src')
        urlretrieve(imgUrl, imagedir + pxfoodname + ".jpg")
        return True
    except NoSuchElementException:
        return False
