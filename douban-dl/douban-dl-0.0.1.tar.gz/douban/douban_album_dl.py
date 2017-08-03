#!/usr/bin/env python

import os

import requests

from utils import file_utils

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36",
    "cache-control": "max-age=0"
}


def get_album(album, path):
    idx = 0
    file_utils.mkdir(path)
    os.chdir(path)
    for photo_url in album.photos():
        name = os.path.basename(photo_url)
        print("{}: saving {}".format(idx, name))
        r = requests.get(photo_url, headers=headers, stream=True)
        with open(name, "wb") as f:
            f.write(r.content)
        idx += 1
    print("saving album to {}, total {} images".format(path, idx))
