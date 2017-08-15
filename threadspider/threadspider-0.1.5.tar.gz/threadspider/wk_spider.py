# coding:utf-8
__author__ = 'admin'
# --------------------------------
# Created by admin  on 2016/8/25.
# ---------------------------------
from Queue import Queue
from threading import Thread
import urllib2
import time
import datetime
import random
from utils.encrypt import  md5
from selenium import  webdriver
import  os
import psutil

_queue = Queue(1000000)
_size = 0
_url_max_num = 0
_proxy_list = []

def wk_spider_init(poolsize, url_maxnum, proxy_list=None):
    print datetime.datetime.now(), "[Spider]:init...."
    global _size, _queue, _url_max_num, _proxy_list
    if proxy_list:
        _proxy_list = proxy_list
    if _size == 0:
        _size = poolsize
        _url_max_num = url_maxnum

        def run():
            for i in range(0, _size):
                _=webdriver.PhantomJS()
                def work(_=_):
                    while 1:
                        fun = _queue.get()
                        if fun:
                            fun(_)
                        _queue.task_done()
                thread = Thread(target=work)
                thread.setDaemon(True)
                thread.start()
        run()


def wk_spider_join():
    global _queue
    _queue.join()
    self_pid=os.getpid()
    process=psutil.Process(pid=self_pid)
    for _ in process.children():
        if _.name()=="phantomjs":
            _.kill()





class WkSpider(object):
    _url_buff = set()
    def __init__(self, url,  handle, timeout=3, retry_times=30,
                 retry_delta=3,force=False):
        '''
            url   目标url
            data   post的数据
            timeout  超时时间
            retry_times 重试次数
            retry_delta   重试间隔
            handle        结果处理函数
        '''
        global _queue
        _hash=md5(url)
        if not force:
            if _hash not in WkSpider._url_buff and len(WkSpider._url_buff) < _url_max_num:
                WkSpider._url_buff.add(_hash)
                self.url = url
                self.timeout = timeout
                self.retry_times = retry_times
                self.retry_delta = retry_delta
                self.handle=handle
                _queue.put(self._go)
        else:
            self.url = url
            self.timeout = timeout
            self.retry_times = retry_times
            self.retry_delta = retry_delta
            self.handle=handle
            _queue.put(self._go)

    def _go(self,brower):
        for i in range(0,self.retry_times):
            brower.set_page_load_timeout(self.timeout)
            try:
                brower.get(self.url)
                self.handle(brower)
            except Exception as e :
                print datetime.datetime.now(), "[WkSpider]:%s Exception:%s" % (self.url, e)
                time.sleep(self.retry_delta)
            else:
                print datetime.datetime.now(), "[WkSpider]:%s Success!" % self.url
                break

