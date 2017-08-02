#!/usr/bin/env python3

__all__ = ['163_download']

import sys
sys.path.append('../')

from ..utils import r0, LibError


def return_dic(p):
    title = r0(r',picSetTitle:\'(.*)\'', p)
    title = ''.join(title)
    author = r0(r'profile:{nickName : \'(.*)\'', p)
    author = ''.join(author)
    _pics = r0(r'pictureId:\d+,url:\'([^\']*)\'', p)
    pics = []
    for i in _pics:
        pics.append((i, i))
    return {'title': title, 'author': author, 'pics': pics}
