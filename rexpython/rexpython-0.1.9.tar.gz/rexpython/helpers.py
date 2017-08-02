from observers import Observer
from . import Disposable, EMPTY_CONSUMER
from . import ON_ERROR, EMPTY_ACTION
from .observers import SingleObserver


class LambdaSingle(SingleObserver, Disposable):
    d = None

    def isDisposed(self):
        return self.d.isDisposed()

    def dispose(self):
        if self.d:
            self.d.dispose()
            self.d = None

    def __init__(self, on_success=EMPTY_CONSUMER, on_error=EMPTY_CONSUMER):
        self.on_error = on_error
        self.on_success = on_success

    def onError(self, err):
        self.on_error(err)

    def onSuccess(self, t):
        self.on_success(t)

    def onSubscribe(self, disposable):
        self.d = disposable


class LambdaObserver(Observer, Disposable):
    _on_next = None
    _on_error = None
    _on_complete = None
    _on_subscribe = None
    _on_dispose = None
    disposable = None

    def __init__(self, on_next=lambda t: None, on_error=ON_ERROR, on_complete=EMPTY_ACTION,
                 on_subscribe=EMPTY_CONSUMER, on_dispose=EMPTY_ACTION):
        self._on_dispose = on_dispose
        self._on_subscribe = on_subscribe
        self._on_complete = on_complete
        self._on_error = on_error
        self._on_next = on_next

    def onSubscribe(self, disposable):
        assert isinstance(disposable, Disposable), "must be Disposable but %s " % disposable
        self.disposable = disposable
        self._on_subscribe(disposable)

    def onNext(self, item):
        self._on_next(item)

    def onError(self, error):
        self._on_error(error)

    def onComplete(self):
        self._on_complete()

    def dispose(self):
        self._on_dispose()
        self.disposable.dispose()

    def isDisposed(self):
        self.disposable.isDisposed()
