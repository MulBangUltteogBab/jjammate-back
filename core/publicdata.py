import requests as req
import json
from .jsonparser import getJsonValue
import logging
import re
# print(json.dumps(json, indent=3, ensure_ascii=False))

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
    logger.info(json.dumps(jsondata, indent=3, ensure_ascii=False))
    return jsondata[service]


def sikyakchungAPI():
    params = {
        'ServiceKey': servicekey,
        'desc_kor': '홍삼보운',
        'type': 'json'
    }


def isValidDate(date) :
    regex = r'\d{4}-\d{2}-\d{2}'
    return bool(re.match(regex, date))


# def getPXFood():
#     SERVICE = 'DS_MND_PX_PARD_PRDT_INFO'
#     data = sendReq(SERVICE)
#     index = data['list_total_count']
#     data = sendReq(SERVICE, end_index=index)
#     return data[row]


# def fatSecretCrawl():
    #return 0
