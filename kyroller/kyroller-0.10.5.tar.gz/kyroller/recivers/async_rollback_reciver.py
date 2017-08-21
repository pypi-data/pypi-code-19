# from multiprocessing import Queue, Process
from queue import Queue
from threading import Thread
import time
import logging
import os
import codecs
import hashlib
import requests
from ..apis import kyd_api
from ..types import Tick, Bar, MarketEvent, IncorrectDataException
from ..types import Tick, Bar, MarketEvent


log = logging.getLogger('AsyncRollbackReciver')


def download(file_url, cache_file_name, queue):
    res = requests.get(file_url, stream=True)
    tmp_file = cache_file_name + '.tmp'
    with codecs.open(tmp_file, 'w', 'utf-8') as f:
        for line_bytes in res.iter_lines(decode_unicode=True):
            line = line_bytes.decode('utf-8').strip()
            f.write(line + '\n')
            queue.put(line)
    os.rename(tmp_file, cache_file_name)
    queue.put(None)


class AsyncRollbackReciver:

    def __init__(self, url, subs, begin, end):
        self.url = url
        self.subs = subs
        self.begin = begin
        self.end = end
        self.runing = False

    def get_download_url(self):
        return "%s/inday-range?subs=%s&begin=%s&end=%s" % (
            self.url, self.subs, self.begin, self.end)

    def get_cache_filename(self):
        url = self.get_download_url()
        if not os.path.exists('./cache'):
            os.mkdir('./cache')
        cache_file_name = hashlib.md5(url.encode('utf_8')).hexdigest()
        return './cache/' + cache_file_name + '.txt'

    def isCached(self):
        return os.path.exists(self.get_cache_filename())

    def get_pre_close(self, date, symbol):
        if '_cache_bars' not in self.__dict__:
            self._cache_bars = {}
        if date not in self._cache_bars:
            api = kyd_api.Api('http://data-api.kuaiyutech.com/rpc2')
            bars = api.get_bars_of_date(date)
            self._cache_bars[date] = {}
            for b in bars:
                self._cache_bars[date][b['symbol']] = b
        if symbol in self._cache_bars[date]:
            return float(self._cache_bars[date][symbol]['preClosePrice'])
        else:
            return 0

    def generate_events_from_cache(self):
        print('xxxx')
        with codecs.open(self.get_cache_filename(), 'r', 'utf-8') as stream:
            for line in stream:
                try:
                    yield self.parse_line_to_event(line)
                except IncorrectDataException as e:
                    print(line)
                    print(e)
                except ValueError as e:
                    print(line)
                    print(e)
        return

    def parse_line_to_event(self, line):
        (evt, msg) = line.strip().split('|')
        if evt == 'market':
            sp = msg.split(',')
            e = MarketEvent(sp[0], int(sp[1]), sp[2])
            return (evt, e)
        elif evt == 'tick':
            tick = Tick(msg)
            # 补全 date
            tick.preclose_backadj = self.get_pre_close(
                tick.date, tick.symbol)
            return (evt, tick)
        elif evt == 'bar':
            bar = Bar(msg)
            bar.preclose_backadj = self.get_pre_close(
                bar.date, bar.symbol)
            return (evt, bar)

    def generate_events(self):
        if self.isCached():
            for x in self.generate_events_from_cache():
                yield x
            return

        queue = Queue()

        url = self.get_download_url()
        cache_file_name = self.get_cache_filename()

        p = Thread(target=download, args=(
            url, cache_file_name, queue), daemon=True)
        p.start()

        while True:
            while not queue.empty():
                line = queue.get()
                if line is None:
                    return
                yield self.parse_line_to_event(line)
            time.sleep(0.01)
