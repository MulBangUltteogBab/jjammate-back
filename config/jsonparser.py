import os
import json
import logging

jsonfile = os.path.join("", 'settings.json')
with open(jsonfile, 'r') as f:
    values = json.loads(f.read())
 
def getJsonValue(key):
        try:
            return values[key]
        except KeyError:
            error_msg = "Set the {} environment variable".format(key)
            raise KeyError(error_msg)

if __name__ == "__main__":
    print(getJsonValue("discordkey"))