import urllib.request
import logging
import json
from .jsonparser import getJsonValue

CLIENTID = getJsonValue("PAPAGO-ID")
CLIENTSECRET = getJsonValue("PAPAGO-SECRET")
logger = logging.getLogger('mbub')

def korToEng(text):
    encText = urllib.parse.quote(text)
    data = "source=ko&target=en&text=" + encText
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", CLIENTID)
    request.add_header("X-Naver-Client-Secret", CLIENTSECRET)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()

    if(rescode==200):
        response_body = response.read()
        res = json.loads(response_body.decode('utf-8'))
        return res["message"]["result"]["translatedText"]
    else:
        logger.info("Error Code:" + rescode)
        raise
