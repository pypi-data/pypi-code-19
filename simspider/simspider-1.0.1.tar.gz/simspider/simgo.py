'''
    爬行从这里开始
'''
from sys import path
from os import getcwd
path.append(getcwd())
from simspider.spider import Spider
from config import *

def main():
    g = Spider()
    g.setRoot(root)
    g.setDownloader(downloader)
    g.setDeep(deep)
    g.setParsers(parsers)
    g.setStoragers(storagers)
    g.start()
