#!/usr/bin/env python3

__all__ = ['lofter_download']

import sys
sys.path.append('../')

from ..utils import r0


def return_dic(p):
    title = r0(r'(?:<title>)(.*)(?:<\/title>)', p)
    title = ''.join(title)
    author = '' 
    author = ''.join(author)
    pics = r0(r'content=\"(https?:\/\/\d+\.media\.tumblr\.com\/[^/]*\/tumblr_\w+_)(\d+)(\.(jpg|jpeg|gif|png|bmp|webp))', p)
    _pics = []
    for i in pics:
        if int(i[1]) < 1280:
            link = i[0] + '1280' + i[2]
        else:
            link = i[0] + i[1] + i[2]
        _pics.append((link, link.split("/")[-1]))
    if _pics != []:
        pics = _pics[:]
    return {'title': title, 'author': author, 'pics': pics}
