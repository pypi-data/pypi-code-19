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
    def callApi(self,endpoint,ids="",fields="*",params="",order="",filters="",limit="",offset=""):

        #If array, convert it to komma seperated string
        if type(ids) != int:
            ids = ",".join(map(str,ids))

        all_filters = ""
        #If has multiple filters
        if type(filters) != str:
            #ids = ",".join(map(str,ids))
            for key, value in filters.items():
                all_filters = all_filters + "&filter" + key + "=" + str(value)

        #If has orders
        if order:
            order = "&order=" + str(order)
        #If has limit
        if limit:
            limit = "&limit=" + str(limit)

        #If has offset
        if offset:
            offset = "&offset=" + str(offset)

        url = 'https://api-2445582011268.apicast.io/'+ endpoint + "/" + str(ids) + "?fields=" + str(fields) + all_filters   + str(params) +str(order)+str(limit)+str(offset)

        print(url)

        headers = {
            'user-key': self.__api_key,
            'Accept' : 'application/json'
            }
        r = requests.get(url, headers=headers)
        #print(r.status_code)
        if r.status_code != 200:
            print("!- ERROR -! " + r.status_code)
        return r

    #GAMES
    def games(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("games",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #PULSE
    def pulses(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("pulses",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #CHARACTERS
    def characters(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("characters",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #COLLECTIONS
    def collections(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("collections",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #COMPANIES
    def companies(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("companies",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #FRANCHISES
    def franchises(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("franchises",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #FEEDS
    def feeds(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("feeds",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #PAGES
    def pages(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("pages",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #GAME_ENGINES
    def game_engines(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("game_engines",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #GAME_MODES
    def game_modes(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("game_modes",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #GENRES
    def genres(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("genres",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #KEYWORDS
    def keywords(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("keywords",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #PEOPLE
    def people(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("people",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #PLATFORMS
    def platforms(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("platforms",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #PLAYER_PERSPECTIVES
    def player_perspectives(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("player_perspectives",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #PULSE_GROUPS
    def keywords(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("pulse_groups",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #RELEASE_DATES
    def release_dates(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("release_dates",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #REVIEWS
    def reviews(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("reviews",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
    #THEMES
    def themes(self,ids="",fields="*",params="",order="",filters="",limit="",offset=""):
        r = self.callApi("themes",ids=ids,fields=fields,params=params,order=order,filters=filters,limit=limit,offset=offset)
        r = json.loads(r.text)
        return r
