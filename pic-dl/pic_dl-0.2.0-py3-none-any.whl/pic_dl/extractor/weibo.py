#!/usr/bin/env python3

__all__ = ['lofter_download']

import sys
sys.path.append('../')

from ..utils import r0


def return_dic(p):
    title = r0(r'(?:"status_title": ")(.*)(?:")', p)
    title = ''.join(title)
    author = ''
    author = ''.join(author)
    pics = r0(r'(?:"url": ")(.*)(?:")', p)
    _pics = []
    for i in pics:
        if 'thumbnail' in i:
            continue
        link = "http://wx1.sinaimg.cn/large/" + i.split("/")[-1]
        _pics.append((link, link.split("/")[-1]))
    if _pics != []:
        pics = _pics[:]
    return {'title': title, 'author': author, 'pics': pics}
