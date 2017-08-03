#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import os

import requests

from douban.celebrity import Celebrity


def get_celebrity(celebrity, path):
    idx = 0
    if not os.path.exists(path):
        os.mkdir(path)
    os.chdir(path)
    for refer, photo_url in celebrity.photos():
        name = os.path.basename(photo_url)
        if os.path.exists(name):
            print("pic {} exist skip".format(name))
            continue
        print("{}: saving {}".format(idx, name))
        headers = {
            "Referer": refer,
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36"
        }
        r = requests.get(photo_url, headers=headers, stream=True)
        with open(name, "wb") as f:
            f.write(r.content)
        idx += 1
    print("saving celebrity photo to {}".format(path))


if __name__ == "__main__":
    celebrity_id = "1335340"
    celebrity = Celebrity(celebrity_id)
    path = os.path.expanduser("~") + "/Pictures/celebrity/" + celebrity_id
    get_celebrity(celebrity, path)
