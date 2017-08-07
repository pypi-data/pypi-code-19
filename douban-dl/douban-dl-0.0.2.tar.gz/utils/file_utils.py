#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

import requests


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_from_url(url, headers, name):
    r = requests.get(url, headers=headers, stream=True)
    with open(name, 'wb') as f:
        f.write(r.content)
