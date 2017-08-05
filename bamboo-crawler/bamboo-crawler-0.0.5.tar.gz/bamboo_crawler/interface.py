from abc import ABCMeta
from abc import abstractmethod
from typing import Any


class Inputter(metaclass=ABCMeta):
    @abstractmethod
    def read(self):
        ...

    def done(self):
        pass


class Outputter(metaclass=ABCMeta):
    @abstractmethod
    def write(self, value, *, context=None):
        ...


class Processor(metaclass=ABCMeta):
    @abstractmethod
    def process(self, value, *, context=None):
        yield ...


class Crawler(Processor):
    def process(self, value, *, context=None):
        for content in self.crawl(value, context=context):
            yield content

    @abstractmethod
    def crawl(self, location, *, context=None):
        yield ...


class Scraper(Processor):
    def process(self, value, *, context=None):
        for content in self.scrape(value, context=None):
            yield content

    @abstractmethod
    def scrape(self, data, *, context=None):
        yield ...


class Deserializer(metaclass=ABCMeta):

    @abstractmethod
    def deserialize(self, data: bytes):
        ...


class Serializer(metaclass=ABCMeta):

    @abstractmethod
    def serialize(self, value: Any):
        ...


class Context(object):
    def __init__(self, body, **kwargs):
        self.body = body
        self.metadata = kwargs.copy()

    def add_metadata(self, **kwargs):
        self.metadata.update(kwargs)
