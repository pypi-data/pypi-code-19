# botlib/rss.py
#
#

""" rss module. """

from .db import Db
from .launcher import Launcher
from .object import Default, Object
from .register import Register
from .clock import Repeater
from .space import kernel, runtime
from .url import get_url

try:
    import feedparser
except:
    pass
import logging
import urllib
import time

def get_feed(url):
    """ fetch a feed. """
    result = []
    if not url or not "http" in url:
        logging.debug("%s is not an url." % url)
        return result
    try:
        result = feedparser.parse(get_url(url).data)
    except (ImportError, ConnectionError, urllib.error.URLError) as ex:
        logging.warn("# %s %s" % (url, str(ex)))
        return result
    if "entries" in result:
        for entry in result["entries"]:
            yield Default(entry)

class Feed(Object):

    """ Feed typed object. """

    pass

class RSS(Register, Launcher):

    """ RSS class for fetching rss feeds. """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._type = str(type(self))

    def start(self, *args, **kwargs):
        from .space import runtime
        repeater = Repeater(600, self.fetcher)
        runtime.register("RSS", self)
        return self.launch(repeater.start)

    def stop(self):
        self.kill("RSS")
       
    def fetcher(self):
        from .space import kernel, seen
        thrs = []
        nr = len(seen.urls)
        for object in kernel.find("rss"):
            if "rss" not in object:
                continue
            if not object.rss:
                continue
            thr = kernel.launch(self.fetch, object)
            thrs.append(thr)
        return thrs

    def synchronize(self):
        from .space import kernel, runtime, seen
        nr = 0
        for object in kernel.find("rss"):
            if not object.get("rss", None):
               continue
            for o in get_feed(object.rss):
                if o.link in seen.urls:
                    continue
                seen.urls.append(o.link)
                nr += 1
        logging.warn("# %s urls" % nr)
        seen.sync()
        return seen

    def fetch(self, object):
        from .utils  import file_time, to_time
        from .space import fleet, kernel, seen
        nr = 0
        for o in list(get_feed(object.rss))[::-1]:
            if o.link in seen.urls:
                continue
            seen.urls.append(o.link)
            feed = Feed(o)
            feed.services = "rss"
            for f in self.cfg.save_list:
                if f in feed.link:
                    if "published" in feed:
                        try:
                            date = file_time(to_time(feed.published))
                            feed.save(stime=date)
                        except bot.error.ENODATE as ex:
                            logging.warn("ENODATE %s" % str(ex))
                    else:
                        feed.save()
            kernel.announce(self.display(feed))
            nr += 1
        seen.sync()
        return nr 

    def display(self, object):
        result = ""
        for check in self.cfg.descriptions:
            link = object.get("link", "")
            if check in link:
                summary = object.get("summary", None)
                if summary:
                    result += "%s - " % summary
        for key in self.cfg.display_list:
            data = object.get(key, None)
            if data:
                result += "%s - " % data.rstrip()
        if result:
            return result[:-3].rstrip()

def init(event):
    rss = RSS()
    rss.start()
    return rss

def shutdown(event):
    rss = runtime.get("RSS", [])
    for item in rss:
        item.stop()
