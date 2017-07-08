# title_find.py
import requests
from bs4 import BeautifulSoup

def web_title(url):
    '''find web site title'''
    url_get = requests.get(url)
    soup = BeautifulSoup(url_get.content, 'lxml')
    print(soup.select('head > title')[0].text)

if __name__ == '__main__':
    #url = 'http://CNN.com'
    url = 'https://www.python.org/'
    web_title(url)