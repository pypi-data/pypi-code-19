import re

import demjson
import execjs
import requests
from pyquery import PyQuery as pq

from .base import BaseDiziCrawler


class DiziayCrawler(BaseDiziCrawler):
    def __init__(self):
        BaseDiziCrawler.__init__(self)

    def generate_episode_page_url(self):
        return "http://diziay.com/izle/" + self.episode['dizi_url'] + "-" + \
               str(self.episode['season']) + "-sezon-" + str(self.episode['episode']) + "-bolum/"

    def after_body_loaded(self, text):
        page_dom = pq(text)
        player_address = page_dom("iframe[height='375']").attr("src")

        result = requests.get(player_address, headers=BaseDiziCrawler.headers)

        if result.status_code == 200:
            self.after_sources_loaded(result.text)

        self.episode['site'] = 'diziay'

    def after_sources_loaded(self, text):
        eval_text = re.search(r'eval\((.*)\)', text).group(1)
        sources_text = execjs.eval('a=' + eval_text)
        sources_text = re.search(r'source=(.*)\}\]', sources_text).group(1) + '}]'
        sources = demjson.decode(sources_text)

        for source in sources:
            if 'p' not in source['label']:
                source['label'] += 'p'
            video_link = {"res": source['label'], "url": source['file']}
            if "mp4" in source['type']:
                self.episode['video_links'].append(video_link)
