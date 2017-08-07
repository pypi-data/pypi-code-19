#!/usr/bin/env python
# -*- coding: utf-8 -*-

import threading

from douban.douban_album_dl import get_album_by_id


class AlbumDownloadThread(threading.Thread):
    def __init__(self, album_id, path):
        super().__init__()
        self.album_id = album_id
        self.path = path

    def run(self):
        get_album_by_id(self.album_id, self.path)


if __name__ == '__main__':
    t1 = AlbumDownloadThread('1621828271', '/home/mi/Pictures/1')
    t2 = AlbumDownloadThread('1621828815', '/home/mi/Pictures/2')

    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("all done")
