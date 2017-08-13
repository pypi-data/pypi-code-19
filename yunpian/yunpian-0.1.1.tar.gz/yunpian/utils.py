# -*- coding: utf-8 -*-
from typing import Dict
from urllib.parse import urlencode


def clean_none(data: dict) -> dict:
    return {
        k: v
        for k, v in data.items()
        if v is not None
    }


def format_url(url, url_params):
    return url + '?' + urlencode(url_params)


def create_headers(api_key: str) -> Dict[str, str]:
    headers = {
        'user-agent': 'python-jubi/0.1.0',
    }
    return headers
