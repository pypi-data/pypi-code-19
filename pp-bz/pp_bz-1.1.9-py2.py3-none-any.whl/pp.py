#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urlparse import urlparse
import hashlib
import subprocess
import sys
import os
import platform


def getDomain(url):
    '''
    取一个url的domain
    >>> getDomain('weibo.com')
    >>> getDomain('http://follow.center/questions/1234567/blah-blah-blah-blah')
    'follow.center'
    '''
    if url.lower().find('http') == -1:
        url = 'http://' + url
    url = urlparse(url)
    hostname = url.hostname
    # 这个想取真的 domain 并不靠谱, 但没有更好的办法了
    hostname = hostname.split(".")
    hostname = ".".join(len(hostname[-2]) < 4 and hostname[-3:] or hostname[-2:])
    return hostname


def getKey():
    '''
    取到key, 没有就问
    '''
    path = os.path.dirname(os.path.realpath(__file__))
    file_name = path + '/key.cfg'
    try:
        f_key = open(file_name, 'r')
        key = f_key.read()
        if key == '':
            askKey(file_name)
            return getKey()
        else:
            return key
    except IOError:
        askKey(file_name)
        return getKey()


def askKey(file_name):
    key = raw_input('请输入key: ')
    f_key = open(file_name, 'w')
    f_key.write(key)
    f_key.close()


def encode(url):
    '''
    >>> encode("https://www.google.com.sg/search?q=python+input&oq=python+input&aqs=chrome..69i57j69i65j69i60l3j35i39.2215j0j9&sourceid=chrome&ie=UTF-8#newwindow=1&q=python+input+vs+raw_input")
    '''
    key = getKey()
    domain = getDomain(url)
    h = hashlib.new('md5')
    h.update(key + domain)
    password = h.hexdigest()
    password = password[:8]
    return password + 'Z'


def copyToClip(password):
    '''
    复制到系统剪贴板
    '''
    if platform.system() == 'Linux':
        # process = subprocess.Popen('xclip -selection clipboard', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
        os.popen('xsel', 'wb').write(password.encode('utf-8'))
    else:
        process = subprocess.Popen('pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
        process.communicate(password.encode('utf-8'))


def run(url):
    password = encode(url)
    copyToClip(password)
    print('已复制到剪贴板!')


def main():
    if len(sys.argv) != 2:
        print('请按以下格式调用:')
        print('pp https://follow.center/login.html')
    else:
        url = sys.argv[1]
        run(url)
if __name__ == '__main__':
    main()
    # import doctest
    # doctest.testmod(verbose=False, optionflags=doctest.ELLIPSIS)
