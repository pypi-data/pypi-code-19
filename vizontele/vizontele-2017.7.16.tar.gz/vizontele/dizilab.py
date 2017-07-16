import copy
import json

import requests
from pyquery import PyQuery as pq

from .base import BaseDiziCrawler


class DizilabCrawler(BaseDiziCrawler):
    def __init__(self):
        BaseDiziCrawler.__init__(self)

    def generate_episode_page_url(self):
        return "http://dizilab.net/" + self.episode['dizi_url'] + "/sezon-" + \
               str(self.episode['season']) + "/bolum-" + str(self.episode['episode'])

    def after_body_loaded(self, text):
        ajax_headers = copy.copy(BaseDiziCrawler.headers)
        ajax_headers['X-Requested-With'] = 'XMLHttpRequest'
        ajax_headers['Referer'] = self.generate_episode_page_url()

        page_dom = pq(text)
        kaynak = page_dom('.language.alternative').find('a').eq(0).attr('onclick')
        vid = kaynak[11:23]

        result = requests.post("http://dizilab.net/request/php/",
                               data={"vid": vid, "tip": "1", "type": "loadVideo"},
                               headers=ajax_headers)

        if result.status_code == 200:
            self.after_sources_loaded(result.text)

        self.episode['site'] = 'dizilab'

    def after_sources_loaded(self, text):
        sources = json.loads(text)['sources']
        for source in sources:
            video_link = {"res": source['label'], "url": source['file']}
            self.episode['video_links'].append(video_link)
