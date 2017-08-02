import traceback
from abc import ABCMeta, abstractmethod

from tblib import pickling_support

pickling_support.install()
from six import reraise


def EMPTY_ACTION():
    pass


def EMPTY_CONSUMER(t):
    pass


def ON_ERROR(err):
    if isinstance(err, tuple):
        reraise(*err)
    else:
        raise err


def THROW_IF_FATAL(err):
    if isinstance(err, tuple):
        pass
        # reraise(*err)
        # traceback.print_exception(*err)
    else:
        pass
        # raise err


class Disposable(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def dispose(self):
        raise RuntimeError("unimplemented")

    @abstractmethod
    def isDisposed(self):
        raise RuntimeError("unimplemented")


class ActionDisposable(Disposable):
    on_dispose = None

    def __init__(self, on_dispose):
        self.on_dispose = on_dispose

    def dispose(self):
        if self.on_dispose:
            self.on_dispose()
            self.on_dispose = None

    def isDisposed(self):
        return self.on_dispose is None


class Emitter(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def onNext(self, t):
        raise RuntimeError("unimplemented")

    @abstractmethod
    def onError(self, err):
        raise RuntimeError("unimplemented")

    @abstractmethod
    def onComplete(self):
        raise RuntimeError("unimplemented")


from .helpers import LambdaObserver
from .helpers import LambdaSingle
from .observable import Observable, ObservableEmitter
from .observers import SingleObserver

__all__ = [ON_ERROR, Disposable, LambdaSingle, LambdaObserver, Observable, ObservableEmitter, SingleObserver]
