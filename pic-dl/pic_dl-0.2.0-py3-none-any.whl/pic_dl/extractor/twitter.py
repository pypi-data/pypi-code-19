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
    pics = r0(r'<meta  property=\"og:image\" content=\"(https?:\/\/[^:]*)([^"]*)', p)
    _pics = []
    for i in pics:
        link = i[0] + ":orig"
        _pics.append((link, link.split("/")[-1].split(":")[0]))
    if _pics != []:
        pics = _pics[:]
    return {'title': title, 'author': author, 'pics': pics}
