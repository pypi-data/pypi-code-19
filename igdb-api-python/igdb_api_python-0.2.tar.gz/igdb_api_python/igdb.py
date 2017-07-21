# IGDB PYTHON WRAPPER

import requests
import json

class igdb:

    __api_key = ""

    def __init__(self,api_key):
        self.__api_key = api_key
        if self.__api_key == "":
            print("Please provide your key from api.igdb.com")
            exit()

    #CALL TO THE API
    def callApi(self,endpoint,ids="",fields="*",params=""):
        url = 'https://api-2445582011268.apicast.io/' + endpoint + "/" + str(ids) + "?fields=" + str(fields) + str(params)
        headers = {
            'user-key': self.__api_key,
            'Accept' : 'application/json'
            }
        r = requests.get(url, headers=headers)
        return r

    #GAMES
    def games(self,ids="",fields="*",params=""):
        r = self.callApi("games",ids=ids,fields=fields,params=params)
        r = json.loads(r.text)
        return r

    #PULSE
    def pulses(self,ids="",fields="*",params=""):
        r = self.callApi("pulses",ids=ids,fields=fields,params=params)
        r = json.loads(r.text)
        return r
