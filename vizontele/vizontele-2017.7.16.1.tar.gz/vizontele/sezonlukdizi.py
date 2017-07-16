import copy
import json
import re

import demjson
import execjs
import requests
from pyquery import PyQuery as pq

from .base import BaseDiziCrawler


class SezonlukDiziCrawler(BaseDiziCrawler):

    cookies = '__cfduid=de7076f8dbb12f98d86619822a8f26dab1495121356; sezonlukdizi=ziyaret=1; ' \
              'ASPSESSIONIDCQSSTDSQ=JHJJOJKBOMDAFICGNPIINGJM; __session:0.8629218722417047:=http:'

    def __init__(self):
        BaseDiziCrawler.__init__(self)

    def generate_episode_page_url(self):
        return "http://sezonlukdizi.net/" + self.episode['dizi_url'] + "/" + \
               str(self.episode['season']) + "-sezon-" + str(
            self.episode['episode']) + "-bolum.html"

    def after_body_loaded(self, text):
        page_dom = pq(text)
        player_address = "http:" + page_dom("iframe[height='360']").eq(0).attr("src")

        new_headers = copy.copy(BaseDiziCrawler.headers)
        new_headers['Cookie'] = SezonlukDiziCrawler.cookies
        result = requests.get(player_address, headers=new_headers)

        if result.status_code == 200:
            self.after_sources_loaded(result.text)
            for video_source in self.episode['video_links']:
                if 'http' not in video_source['url']:
                    video_source['url'] = 'http:' + video_source['url']

            for sub_source in self.episode['subtitle_links']:
                if 'http' not in sub_source['url']:
                    sub_source['url'] = 'http:' + sub_source['url']

        self.episode['site'] = 'sezonlukdizi'

    def after_sources_loaded(self, text):
        video_altyazi_test = re.search(r"(var video(?s).*.\"\}\);)", text).group(1)
        ctx = execjs.compile('function b(){\n' + video_altyazi_test + 'return [video, altyazi];}')
        [sources, subs] = ctx.call("b")

        for source in sources:
            if 'p' not in str(source['label']):
                source['label'] = str(source['label']) + 'p'

            video_link = {"res": source['label'], "url": source['file']}
            self.episode['video_links'].append(video_link)

        for source in subs:
            if source['label'][0] == 'T':
                source['label'] = 'tr'
            elif source['label'][0] == 'E':
                source['label'] = 'en'

            subtitle_link = {"lang": source['label'], "url": source['file'], "kind": "vtt"}
            self.episode['subtitle_links'].append(subtitle_link)
