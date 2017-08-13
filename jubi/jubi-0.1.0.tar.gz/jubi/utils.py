# -*- coding: utf-8 -*-
import time
from urllib.parse import urlencode


def clean_none(data: dict) -> dict:
    return {
        k: v
        for k, v in data.items()
        if v is not None
    }


def format_url(url, url_params):
    return url + '?' + urlencode(url_params)


def get_nonce() -> str:
    return str(int(time.time()))
