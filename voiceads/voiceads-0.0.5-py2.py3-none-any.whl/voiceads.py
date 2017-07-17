'''
Created on May 4, 2017
Modified on July 14, 2017
@author: ajain
'''

import requests
import logging
import traceback
import json

class VoiceAdsAI:

    appToken = ''
    session = None

    def sendVAReq(self, payload, body):
        url = 'https://ads.voiceads.ai/ad'
        params = payload
        response = requests.get(url, params=params, json=body)
        return response

    def __init__ (self):
        pass

    def initialize(self, appToken, appType, session, reqBody = None):

        try: 
            if session is None or appToken is None or len(appToken.strip()) == 0:
                logging.error("Error: cannot initialize VoiceAds SDK")
                return 

            if 'appType' not in session:
                logging.error("Error: cannot initialize VoiceAds SDK. Skill Type missing")
                return

            if 'appName' not in session: 
                logging.error("Error: cannot initialize VoiceAds SDK. Skill Name missing")
                return

            if 'appId' not in session: 
                logging.error("Error: cannot initialize VoiceAds SDK. Amazon Skill Id missing")
                return

            self.appToken = appToken
            self.session = session
            self.reqBody = reqBody

            return

        except:
            logging.error("ERROR: occurred inside initalize")
            traceback.print_exc()
            return None

    def getAd(self):

        try:
            if self.session is None:
                logging.error("ERROR: VoiceAds has not been initialized. Initalize() method need to have been invoked before getAd") 
                return

            p = {}
            p['app_token'] = self.appToken
            p['app_name'] = self.session['appName']
            p['app_id'] = self.session['appId']
            p['app_type'] = self.session['appType']
            p['app_category'] = self.session['appCategory'] if 'appCategory' in self.session else ''
            p['output'] = self.session['output'] if 'output' in self.session else 'json'
            p['keywords'] = self.session['keywords'] if 'keywords' in self.session else ''
            p['locale'] = self.session['locale'] if 'locale' in self.session else 'en-US'

            resp = self.sendVAReq(p, self.reqBody)
            if p['output'] == 'json' :
                return resp.json()
            else: 
                return resp.text

        except:
            logging.error("ERROR: occurred inside getAd method")
            traceback.print_exc()
            return None

    def trackAd(self, reqBody = None):
        try:
            if self.session is None: 
                logging.error("ERROR: VoiceAds has not been initialized. Initalize() method need to have been invoked before trackAd")

            if reqBody is not None:
                token = reqBody['request']['token']
                token = token.split(':')
                if token[0] == "VoiceAds":
                    reqt = token[1]

                    p = {}
                    p['app_token'] = self.appToken
                    p['app_name'] = self.session['appName']
                    p['app_id'] = self.session['appId']
                    p['app_type'] = self.session['appType']
                    p['app_category'] = self.session['appCategory'] if 'appCategory' in self.session else ''
                    p['output'] = self.session['output'] if 'output' in self.session else 'json'
                    p['keywords'] = self.session['keywords'] if 'keywords' in self.session else ''
                    p['locale'] = self.session['locale'] if 'locale' in self.session else 'en-US'
                    p['reqt'] = reqt

                    url = 'https://ads.voiceads.ai/track'
                    params = p
                    body = reqBody
                    response = requests.get(url, params=params, json=body)
                    return response

            return

        except:
            return

