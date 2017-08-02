from abc import ABCMeta, abstractmethod
from .observers import BlockingMultiObserver


class SingleSource(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def subscribe(self, single_observer):
        raise RuntimeError("unimplemented")


class Single(SingleSource):
    def subscribe(self, single_observer):
        raise RuntimeError("unimplemented")

    def blockingGet(self):
        o = BlockingMultiObserver()
        self.subscribe(o)
        return o.blockingGet()
