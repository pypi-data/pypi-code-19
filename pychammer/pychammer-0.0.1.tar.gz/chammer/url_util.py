#
#  -*- coding: utf-8 -*-

import re


def is_image_url(url):
    #根据URL后缀判断是否是图片请求
    #('.gif', '.jpg', '.png', '.webp'

    if url.endswith(('.gif', '.jpg', '.png', '.webp')):
        return True
    else:
        return False


def get_host(url):
    # 从URL中获取主机名称
    reobj = re.compile(r"""(?xi)\A
    [a-z][a-z0-9+\-.]*://                                # Scheme
    ([a-z0-9\-._~%!$&'()*+,;=]+@)?                       # User
    ([a-z0-9\-._~%]+                                     # Named or IPv4 host
    |\[[a-z0-9\-._~%!$&'()*+,;=:]+\])                    # IPv6+ host
    """)
    match = reobj.search(url)
    if match:
        return match.group(2)
    else:
        return ''

