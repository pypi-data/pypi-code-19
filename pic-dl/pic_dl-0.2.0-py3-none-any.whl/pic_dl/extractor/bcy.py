#!/usr/bin/env python3

__all__ = ['bcy_download']

import sys
sys.path.append('../')

from ..utils import r0, LibError


def return_dic(p):
    title = r0(r'<title>(.*)<\/title>', p)
    title = ''.join(title)
    author = r0(r'href="/u/\d+" title="(.*)\"', p)
    author = list(set(author))
    author = ''.join(author)
    _pics = r0(r'<img class=\'detail_std detail_clickable\' src=\'(\S+)\/w650', p)
    pics = []
    for i in _pics:
        pics.append((i, i.split("/")[-1]))
    return {'title': title, 'author': author, 'pics': pics}
