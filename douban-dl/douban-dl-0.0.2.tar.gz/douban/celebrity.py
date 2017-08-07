#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import requests
from bs4 import BeautifulSoup


class Celebrity:
    BASE_URL = "https://movie.douban.com/celebrity/{}/photos/"

    def __init__(self, celebrity_id):
        self.url = Celebrity.BASE_URL.format(celebrity_id)

    def photos(self):
        start = 0
        while True:
            next_photos = self.__photos(start)
            step = len(next_photos)
            if 0 == step:
                break
            for photo in next_photos:
                # https://img3.doubanio.com/view/photo/thumb/public/p2156276775.jpg
                # https://img3.doubanio.com/view/photo/raw/public/p2156276775.jpg
                # https://img3.doubanio.com/view/photo/photo/public/p2156276775.webp
                yield photo.a['href'], photo.img['src'].replace("photo/thumb", "photo/raw")
            start += step

    def __photos(self, start):
        params = {
            "type": "C",
            "start": start,
            "sortby": "vote",
            "size": "a",
            "subtype": "a"
        }
        r = requests.get(self.url, params=params)
        soup = BeautifulSoup(r.text, "html.parser")
        return soup.find_all("div", class_="cover")
