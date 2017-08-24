from sys import path
from os import getcwd
path.append(getcwd())
from testconfig import *
from simspider.spider import Spider


def main():
    g = Spider()
    g.setTest()
    g.setRoot(url)
    g.setDownloader(downloader)
    g.setDeep(1)
    g.setParsers([parser,])
    g.setStoragers([storager,])
    g.start()
