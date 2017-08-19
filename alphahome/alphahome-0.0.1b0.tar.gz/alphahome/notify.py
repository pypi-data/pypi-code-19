# -*- coding:utf-8 -*-
import requests
import json

home = str()


def notice(appid, token, degree, message):
    url = 'https://api.alphaho.me/home/notice/'
    requests.post(
        url,
        data={
            'appid': appid,
            'token': token,
            'home': home,
            'degree': degree,
            'message': message
        }
    )


def set_home(h):
    global home
    home = h
