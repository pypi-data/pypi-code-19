#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib

import os


class File_Downloader(object):
    @staticmethod
    def download(path, file_name, url):
        try:
            local = os.path.join(path, file_name)
            if os.path.isdir(path):
                pass
            else:
                os.makedirs(path)
            urllib.urlretrieve(url, local)
        except Exception, e:
            print(e)
