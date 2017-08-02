#!/usr/bin/env python3
import os
import html
import requests
import re
import threading
import logging

logging.getLogger("requests").setLevel("WARNING")


class LibError(Exception):
    pass


def r0(pattern, text):
    _r = re.findall(pattern, text)
    return _r


def r1(pattern, text):
    _r = re.search(pattern, text)
    return _r


def escape_file_path(path):
    path = path.replace("/", "-")
    path = path.replace('"', "-")
    path = path.replace("\\", "-")
    path = path.replace("*", "-")
    path = path.replace("?", "-")
    return path


def r_get(link, headers=None, proxy=None):
    if not headers:
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "UTF-8,*;q=0.5",
            "Accept-Encoding": "gzip,deflate,sdch",
            "Accept-Language": "en-US,en;q=0.8",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:13.0) Gecko/20100101 Firefox/13.0"
        }
        res = requests.get(link,
                           proxies={"http": proxy, "https": proxy},
                           headers=headers, timeout=20)
    return res


def to_url(u):
    u = u.replace("http", "")
    u = u.replace("https", "")
    u = u.replace("://", "")
    return u


def multithre_downloader(threads=4, dic=None, **kwargs):
    logger = logging.getLogger()
    proxy = kwargs.get("proxy", None)
    mod = kwargs.get("mod", None)
    dic["author"] = html.unescape(dic["author"])
    dic["title"] = html.unescape(dic["title"])
    pic_links = list(set(dic["pics"]))
    from queue import Queue
    q = Queue()
    for i in pic_links:
        path = ""
        path = path + dic["author"] + " - " if dic["author"] != "" else path
        path = path + dic["title"] + " - " if dic["title"] != "" else path
        path += i[1]
        path = escape_file_path(path)
        q.put((i[0], path, proxy))

    def worker():
        def downloader(link, path, proxy=None):
            logger.info("{}: Downloading {}/{}".format(mod, len(pic_links)-q.qsize(), len(pic_links)))
            if os.path.isfile(path):
                logger.debug("{}: Already exists, passing {}".format(mod, path))
                return 0
            content = r_get(link, proxy=proxy).content
            if len(path) > 255:
                path = path[-255:]
            with open(path, "wb") as f:
                f.write(content)
            return 0

        nonlocal q
        while not q.empty():
            job = q.get()
            logger.debug("{}: Processing {}, {} left.".format(mod, job[0], q.qsize()))
            try:
                downloader(job[0], job[1], proxy=job[2])
            except:
                logger.warning("{}: Error {}, {} left.".format(mod, job[0], q.qsize()))
            finally:
                q.task_done()
        return 0

    for i in range(threads):
        threading.Thread(target=worker, daemon=True).start()
    q.join()
    logger.info("{}: DONE".format(mod))
