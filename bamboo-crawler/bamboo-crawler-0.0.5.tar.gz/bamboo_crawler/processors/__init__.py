from collections import defaultdict
from datetime import date
from datetime import datetime
from datetime import time
from urllib.parse import parse_qs
from urllib.parse import urlparse

import lxml.html
import requests
from types import MappingProxyType

from .. import interface


class HTTPCrawler(interface.Crawler):
    def crawl(self, url, *, context=None):
        resp = requests.get(url)
        yield resp.content


class XPathScraper(interface.Scraper):
    def __init__(self, xpaths):
        self.xpaths = xpaths

    def scrape(self, data, *, context=None):
        elements = lxml.html.fromstring(data)
        j = {key: elements.xpath(xpath)
             for key, xpath in self.xpaths.items()}
        yield j


class SingleXPathScraper(interface.Scraper):
    def __init__(self, xpath):
        self.xpath = xpath

    def scrape(self, data, *, context=None):
        element = lxml.html.fromstring(data)
        elements = element.xpath(self.xpath)
        k = [str(x) for x in elements]
        yield from k


class CSSSelectorScraper(interface.Scraper):
    def __init__(self, selectors):
        self.selectors = selectors

    def scrape(self, data, *, context=None):
        elements = lxml.html.fromstring(data)
        j = {key: self.__select(elements, p_selector)
             for key, p_selector in self.selectors.items()}
        yield j

    @classmethod
    def __select(cls, elements, p_selector):
        if isinstance(p_selector, (str, bytes)):
            return [e.text_content() for e in elements.cssselect(p_selector)]
        selector, attribute = p_selector
        return [e.attrib[attribute] for e in elements.cssselect(selector)]


class MixedHTMLScraper(interface.Scraper):
    def __init__(self, *,
                 targets=MappingProxyType({})):
        self.targets = targets
        xpaths = {key: target['xpath']
                  for key, target in targets.items()
                  if 'xpath' in target}
        css = {key: target['css']
               for key, target in targets.items()
               if 'css' in target}
        self.xpath_scraper = XPathScraper(xpaths=xpaths)
        self.cssselector_scraper = CSSSelectorScraper(selectors=css)

    def scrape(self, data, *, context=None):
        d1 = list(self.xpath_scraper.scrape(data))[0]
        d2 = list(self.cssselector_scraper.scrape(data))[0]
        yield self.__merge(d1, d2)

    @classmethod
    def __merge(cls, *scraped_data_list):
        d = defaultdict(list)
        for data in scraped_data_list:
            for key, values in data.items():
                d[key].extend(values)
        return dict(d)


class NullProcessor(interface.Processor):
    def process(self, data, *, context=None):
        yield data


class PythonProcessor(interface.Processor):
    def __init__(self, *, mappers):
        self.mappers = mappers

    @classmethod
    def __safe_eval(self, code, data, metadata):

        def extract_digit(data):
            return ''.join(x for x in data if x.isdigit())

        allowed_functions = {
            'int': int,
            'float': float,
            'str': str,
            'extract_digit': extract_digit,
            'urlparse': urlparse,
            'parse_qs': parse_qs,
            'date': date,
            'time': time,
            'datetime': datetime,
        }
        globals_ = {'__builtins__': allowed_functions}
        locals_ = {'_': data, 'meta': metadata}
        try:
            return eval(code, globals_, locals_)
        except Exception:
            return None

    def process(self, data, *, context=None):
        yield {key: self.__safe_eval(code, data, metadata=context.metadata)
               for key, code in self.mappers.items()}


__all__ = ['HTTPCrawler', 'XPathScraper', 'SingleXPathScraper',
           'CSSSelectorScraper', 'NullProcessor']
