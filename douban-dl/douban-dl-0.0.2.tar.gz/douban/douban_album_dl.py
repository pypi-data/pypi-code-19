#!/usr/bin/env python

import os

from douban.album import Album
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
    for photo_url in album.photos():
        name = os.path.basename(photo_url)
        print("{}: saving {}".format(idx, name))
        file_utils.save_from_url(photo_url, headers, path + '/' + name)
        idx += 1
    print("saving album to {}, total {} images".format(path, idx))


def get_album_by_id(album_id, path):
    print("saving album {} to {}".format(album_id, path))
    album = Album(album_id)
    get_album(album, path)
