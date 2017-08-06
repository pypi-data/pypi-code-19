from urllib.request import Request, urlopen, build_opener
from bs4 import BeautifulSoup
import execjs
import os


def get_download_link(url):
    req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')
    scripts = soup.findAll('script')
    revC = str(scripts[-2])
    the_call = revC[revC.find('revC')+6:revC.find('</')-2]
    the_exe = str(scripts[-3])[8:str(scripts[-3]).find('</')]
    ctx = execjs.compile(the_exe)

    return ctx.call('revC', the_call)


def get_redirected(url, download_link):
    opener = build_opener()
    request = Request(download_link, headers={'Referer': url,
                                              'User-Agent': 'Mozilla/5.0'})
    u = opener.open(request)
    return u.geturl()


def unshorten(url):
    return get_redirected(url, get_download_link(url))
