import logging
import sys
import traceback
from abc import ABCMeta, abstractmethod
from multiprocessing import queues

from . import Disposable, ON_ERROR, THROW_IF_FATAL
from utils import CountDownLatch

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Observer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def onSubscribe(self, disposable):
        raise RuntimeError("unimplemented")

    @abstractmethod
    def onNext(self, t):
        raise RuntimeError("unimplemented")

    @abstractmethod
    def onError(self, err):
        raise RuntimeError("unimplemented")

    @abstractmethod
    def onComplete(self):
        raise RuntimeError("unimplemented")


class SingleObserver(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def onSubscribe(self, disposable):
        raise RuntimeError("unimplemented")

    @abstractmethod
    def onSuccess(self, t):
        raise RuntimeError("unimplemented")

    @abstractmethod
    def onError(self, err):
        raise RuntimeError("unimplemented")


class BasicObserver(Observer, Disposable):
    __metaclass__ = ABCMeta

    def __init__(self, actual):
        """

        :type actual: Observer
        """
        assert isinstance(actual, Observer), "actual must be Observer type but %s" % type(actual)
        self.actual = actual
        self.done = False
        self.s = None

    def isDisposed(self):
        return self.s.isDisposed()

    def dispose(self):
        self.s.dispose()

    def onComplete(self):
        if self.done:
            return
        self.done = True
        self.actual.onComplete()

    def onSubscribe(self, disposable):
        self.s = disposable
        self.actual.onSubscribe(self)

    def onError(self, err):
        if self.done:
            ON_ERROR(err)
            return

        self.done = True
        self.actual.onError(err)

    @abstractmethod
    def onNext(self, t):
        raise RuntimeError("unimplemented")


class BlockingMultiObserver(SingleObserver, CountDownLatch):
    def __init__(self):
        super(BlockingMultiObserver, self).__init__(count=1)
        self.d = None
        self.value = queues.Queue()
        self.error = queues.Queue()

    def onError(self, err):
        self.error.put(err)
        self.count_down()

    def onSuccess(self, t):
        self.value.put(t)
        self.count_down()

    def onComplete(self):
        log.error("COMPLETE")
        self.count_down()

    def onSubscribe(self, disposable):
        self.d = disposable

    def blockingGet(self):
        if self.count != 0:
            try:
                self.await()
            except Exception:
                exc_info = sys.exc_info()
                try:
                    self.d.dispose()
                except Exception:
                    THROW_IF_FATAL(sys.exc_info())
                ON_ERROR(exc_info)

        try:
            err = self.error.get(False)
            if err:
                ON_ERROR(err)
        except queues.Empty:
            pass

        return self.value.get(timeout=1.)


class BlockingObserver(Observer, Disposable):
    COMPLETE = "::COMPLETE"
    TERMINATED = "::TERMINATED"

    def __init__(self, queue):
        """

        :type queue: queues.Queue
        """
        self.queue = queue
        self.d = None

    def isDisposed(self):
        return self.d is None

    def onError(self, err):
        self.queue.put(err)

    def dispose(self):
        if self.d is not None:
            self.d.dispose()
            self.queue.put(BlockingObserver.TERMINATED)
            self.d = None

    def onNext(self, t):
        self.queue.put(t)

    def onSubscribe(self, disposable):
        self.d = disposable

    def onComplete(self):
        self.queue.put(BlockingObserver.COMPLETE)
