# -*- coding: utf-8 -*-
"""
    s1acker.s1acker
    ~~~~~~~~~~~~~~

    This module provides functions that deal with s1 search interface.

    :copyright: (c) 2017 by quinoa42.
    :license: MIT, see LICENSE for more details.
"""

import logging
import os.path as op
import re
import time
from itertools import chain
from os import makedirs

import requests
from bs4 import BeautifulSoup

flaten = chain.from_iterable

_SEARCH_URL = "http://bbs.saraba1st.com/2b/search.php?mod=forum"
_SEARCH_ADV_URL = "http://bbs.saraba1st.com/2b/search.php?mod=forum&adv=yes"
_TOPIC_URL = "http://bbs.saraba1st.com/2b/thread-{0}-1-1.html"
_HOST = "bbs.saraba1st.com"
_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:54.0) "
    "Gecko/20100101 Firefox/54.0"
)
_TIME_OUT = 10
_SLEEP_TIME = 1

logger = logging.getLogger(__name__)


def _wait():
    """wait for _SLEEP_TIME seconds.

    """
    logger.info("wait for %s seconds.", _SLEEP_TIME)
    time.sleep(_SLEEP_TIME)


class S1ack(object):
    """S1ack defines a class that implement search functions."""

    def __init__(self, srchtxt, srchuname=None):
        """construct a s1ack object with given srchtxt and optional srchuname.

        :srchtxt: str that you want to search
        :srchuname: optional str that limit search topics to posts by this user

        """
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': _USER_AGENT,
            'Host': _HOST
        })
        r = self._session.get(
            _SEARCH_ADV_URL,
            timeout=_TIME_OUT,
            headers={'Referer': _SEARCH_URL}
        )
        soup = BeautifulSoup(r.text, 'lxml')
        formhash = soup.find("input", attrs={"name": "formhash"})['value']
        self._input_data = {
            "ascdesc": "desc",
            "before": "",
            "formhash": formhash,
            "orderby": "lastpost",
            "searchsubmit": "yes",
            "srchfid[]": "all",
            "srchfilter": "all",
            "srchfrom": 0,
            "srchtxt": srchtxt,
            "srchuname": srchuname if srchuname is not None else ""
        }
        logger.debug("input data: %r", self._input_data)

    def search(self):
        """Return the search result.
        :returns: list of Img object

        """
        search_result = self._get_search_urls()
        result = list(
            set(
                flaten(
                    map(
                        self._get_imgs,
                        flaten(
                            map(
                                self._get_pages,
                                flaten(
                                    map(self._get_first_page, search_result)
                                )
                            )
                        )
                    )
                )
            )
        )
        logger.debug("final result: %r", result)
        logger.info("find %d pictures", len(result))
        return result

    def _get_search_urls(self):
        """Return the urls of the pages of searching result
        :returns: a list of str, where one str represent a url of one page

        """
        logger.info("trying to search")
        r = self._session.post(
            _SEARCH_URL,
            timeout=_TIME_OUT,
            headers={"Referer": _SEARCH_ADV_URL},
            data=self._input_data
        )
        r.raise_for_status()
        result = BeautifulSoup(r.text, 'lxml').find("div", class_="pg")
        num = int(result.find_all("a")[-2].string) if result else 1

        url = re.sub("&kw=.+$", "", r.url, 1)
        urls = [r.url] + [url + "&page=" + str(i) for i in range(2, num + 1)]

        logger.debug("search result: %r", urls)
        return urls

    def _get_first_page(self, url):
        """Return the first pages of the topics in the given search result page

        :url: str, the url of search result page
        :returns: list of str, represent the list of urls of topics

        """
        _wait()
        logger.info("trying to get the topics in %s", url)

        r = self._session.get(url, timeout=_TIME_OUT)
        r.raise_for_status()
        s = BeautifulSoup(r.text, "lxml")
        topics = [
            re.findall("tid=([0-9]{1,7})", topic.a['href'])[0]
            for topic in s.find_all("h3", class_="xs3")
        ]
        urls = [_TOPIC_URL.format(topic) for topic in topics]

        logger.debug("topics in %s: %r", url, urls)
        return urls

    def _get_pages(self, url):
        """Return the urls of all pages of a topic.

        :url: str, represent the url of a topic
        :returns: list of str, represent list of urls of the pages

        """

        _wait()
        logger.info("trying to get the pages of %s", url)

        r = self._session.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        multipage = soup.find('div', class_="pg")
        num = int(multipage.find_all("a")[-2].string) if multipage else 1
        urls = [
            re.sub("[0-9]{1,3}-1.html", str(page) + "-1.html", url)
            for page in range(1, num + 1)
        ]

        logger.debug("all pages of %s: %r", url, urls)
        return urls

    def _get_imgs(self, url):
        """Get list of imgs from the url.

        :url: str, represent the url wish to explore
        :returns: a list of Img object, represent the search result

        """

        _wait()
        logger.info("trying to get imgs on the page %s", url)

        r = self._session.get(url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'lxml')
        imgs = [
            url
            for url in [
                img.attrs.get('file') or img.attrs.get('src') for post in
                soup.find_all("td", id=re.compile("postmessage_[0-9]{1,8}"))
                for img in post.find_all("img")
            ]
            if not re.match("http://static.saraba1st.com/image/smiley/", url)
            and re.search("\.(png|jpg)$", url)
            and not re.search("\.photobucket\.", url)
        ]
        result = [
            Img(img, str(index), url) for index, img in enumerate(set(imgs))
        ]

        logger.debug("Imgs in %s: %r", url, result)
        return result


class Img(object):
    """Img defines an object that can be downloaded."""

    def __init__(self, url, name, origin=""):
        """construct an Img object with url, name, and optional origin

        :url: str represent the url of the Img
        :name: the name given to this Img when downloading
        :origin: str represent the origin of the Img,i.e. the url of the topic

        """
        self._url = url
        self._origin = origin
        self._topic = re.findall("thread-([0-9]{1,9})",
                                 origin)[0] if origin else ""
        self._name = name
        self._fmt = re.findall("(\.jpg|\.png)$", url)[0]

    def download(self, dest):
        """download this Img to the dest directory.
        :returns: None

        """
        _wait()
        logger.info("trying to get img at %s", self._url)
        try:
            img = requests.get(
                self._url,
                headers={"User-Agent": _USER_AGENT,
                         "Referer": self._origin},
                timeout=_TIME_OUT
            )
            img.raise_for_status()
        except Exception as e:
            logger.error("Failed when trying to get %s : %s", self._url, e)
        else:
            dir_path = op.join(dest, self._topic)
            if not op.exists(dir_path):
                logger.info("%s not exist, making the directory", dir_path)
                makedirs(dir_path)

            path = op.join(dir_path, self._name + self._fmt)
            logger.info("downloading img to %s", path)
            with open(path, 'wb') as f:
                f.write(img.content)

    def __eq__(self, other):
        return self._url == other._url

    def __ne__(self, other):
        return not self._url == other._url

    def __repr__(self):
        return "![{_name}{_fmt}]({_url})".format(**self.__dict__)

    def __hash__(self):
        return repr(self).__hash__()

    __str__ = __unicode__ = __repr__
