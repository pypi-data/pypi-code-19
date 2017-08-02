# IGDB PYTHON WRAPPER

import requests
import json

class igdb:

    __api_key = ""
    __args = ""
    __api_url = "https://api-2445582011268.apicast.io/"

    def __init__(self,api_key):
        self.__api_key = api_key

    #CREATE URL FROM PARAMETERS
    def joinParameters(self,parameter="",types="",default="",prefix=""):
        if parameter in self.__args:
            default = str(prefix)
            if type(self.__args[parameter]) != types:
                default += ",".join(map(str,self.__args[parameter]))
            else:
                default += str(self.__args[parameter])
        return default

    #CALL TO THE API
    def call_api(self,endpoint,args):
        ids=order=filters=expand=limit=offset = ""
        fields  = "*"
        self.__args=args

        #If dict, convert it to komma seperated string
        if type(args) != int:
            ids     = self.joinParameters(parameter='ids',types=int)
            fields  = self.joinParameters(parameter='fields',types=str,default="*")
            expand  = self.joinParameters(parameter='expand',types=str,prefix="&expand=")
            limit   = self.joinParameters(parameter='limit',types=int,prefix="&limit=")
            offset  = self.joinParameters(parameter='offset',types=int,prefix="&offset=")
            order   = self.joinParameters(parameter='order',types=str,prefix="&order=")

            if 'filters' in args:
                for key, value in args['filters'].items():
                    filters += "&filter" + key + "=" + str(value)
        else:
            ids = args

        url = self.__api_url + endpoint + "/" + str(ids) + "?fields=" + str(fields)+ str(filters)+ str(order)+ str(limit)+ str(offset)+ str(expand)
        print(url)

        headers = {
            'user-key': self.__api_key,
            'Accept' : 'application/json'
            }
        r = requests.get(url, headers=headers)
        return r

    #GAMES
    def games(self,args=""):
        r = self.call_api("games",args)
        r = json.loads(r.text)
        return r
    #PULSE
    def pulses(self,args=""):
        r = self.call_api("pulses",args)
        r = json.loads(r.text)
        return r
    #CHARACTERS
    def characters(self,args=""):
        r = self.call_api("characters",args=args)
        r = json.loads(r.text)
        return r
    #COLLECTIONS
    def collections(self,args=""):
        r = self.call_api("collections",args=args)
        r = json.loads(r.text)
        return r
    #COMPANIES
    def companies(self,args=""):
        r = self.call_api("companies",args=args)
        r = json.loads(r.text)
        return r
    #FRANCHISES
    def franchises(self,args=""):
        r = self.call_api("franchises",args=args)
        r = json.loads(r.text)
        return r
    #FEEDS
    def feeds(self,args=""):
        r = self.call_api("feeds",args=args)
        r = json.loads(r.text)
        return r
    #PAGES
    def pages(self,args=""):
        r = self.call_api("pages",args=args)
        r = json.loads(r.text)
        return r
    #GAME_ENGINES
    def game_engines(self,args=""):
        r = self.call_api("game_engines",args=args)
        r = json.loads(r.text)
        return r
    #GAME_MODES
    def game_modes(self,args=""):
        r = self.call_api("game_modes",args=args)
        r = json.loads(r.text)
        return r
    #GENRES
    def genres(self,args=""):
        r = self.call_api("genres",args=args)
        r = json.loads(r.text)
        return r
    #KEYWORDS
    def keywords(self,args=""):
        r = self.call_api("keywords",args=args)
        r = json.loads(r.text)
        return r
    #PEOPLE
    def people(self,args=""):
        r = self.call_api("people",args=args)
        r = json.loads(r.text)
        return r
    #PLATFORMS
    def platforms(self,args=""):
        r = self.call_api("platforms",args=args)
        r = json.loads(r.text)
        return r
    #PLAYER_PERSPECTIVES
    def player_perspectives(self,args=""):
        r = self.call_api("player_perspectives",args=args)
        r = json.loads(r.text)
        return r
    #RELEASE_DATES
    def release_dates(self,args=""):
        r = self.call_api("release_dates",args=args)
        r = json.loads(r.text)
        return r
    #PULSE GROUPS
    def pulse_groups(self,args=""):
        r = self.call_api("pulse_groups",args=args)
        r = json.loads(r.text)
        return r
    #PULSE SOURCES
    def pulse_sources(self,args=""):
        r = self.call_api("pulse_sources",args=args)
        r = json.loads(r.text)
        return r
    #THEMES
    def themes(self,args=""):
        r = self.call_api("themes",args=args)
        r = json.loads(r.text)
        return r
    #REVIEWS
    def reviews(self,args=""):
        r = self.call_api("reviews",args=args)
        r = json.loads(r.text)
        return r
