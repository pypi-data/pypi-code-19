#!/usr/bin/env python3

__all__ = ['tuchong_download']

import sys
sys.path.append('../')

from ..utils import r0, LibError


def return_dic(p):
    title = r0(r'<meta name=\"title\" content=\"(.*)\"', p)
    title = ''.join(title)
    author = r0(r'<meta name=\"author\" content=\"(.*)\"', p)
    author = ''.join(author)
    _pics = r0(r'https:\/\/photo\.tuchong\.com\/\d+\/f\/\d+\.jpg', p)
    pics = []
    for i in _pics:
        pics.append((i, i.split("/")[-1]))
    return {'title': title, 'author': author, 'pics': pics}
