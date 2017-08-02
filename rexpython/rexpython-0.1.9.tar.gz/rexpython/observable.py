import collections
import logging
import multiprocessing
import sys
from abc import ABCMeta, abstractmethod
from multiprocessing import queues

from singles import Single
from . import Emitter, EMPTY_ACTION, Disposable, EMPTY_CONSUMER, THROW_IF_FATAL
from .helpers import LambdaObserver
from .observers import Observer, BasicObserver, SingleObserver, BlockingObserver

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class ObservableSource(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def subscribe(self, observer):
        raise RuntimeError("unimplemented")


class ObservableEmitter(Emitter):
    __metaclass__ = ABCMeta

    @abstractmethod
    def setDisposable(self, d):
        """

        :type d: Disposable
        """
        raise RuntimeError("unimplemented")

    @abstractmethod
    def isDisposed(self):
        raise RuntimeError("unimplemented")


def acceptFull(v, observer):
    if v == BlockingObserver.COMPLETE:
        observer.onComplete()
        return True
    elif isinstance(v, Exception):
        observer.onError(v)
        return True
    observer.onNext(v)
    return False


class ObservableBlockingSubscribe(object):
    @staticmethod
    def subscribe(source, observer):
        """

        :type observer: Observer
        :type source: ObservableSource
        """
        assert isinstance(source, ObservableSource), "source must be ObservableSource but %s" % type(source)
        assert isinstance(observer, Observer), "observer must be Observer but %s" % type(observer)

        queue = queues.Queue()

        bs = BlockingObserver(queue)
        observer.onSubscribe(bs)

        source.subscribe(bs)

        while not bs.isDisposed():
            v = None
            try:
                v = queue.get(timeout=1)
            except queues.Empty:
                continue

            if v is None:
                bs.dispose()
                observer.onComplete()
                break

            if bs.isDisposed() or v == BlockingObserver.TERMINATED or acceptFull(v, observer):
                break


class DisposeTask(Disposable, multiprocessing.Process):
    def __init__(self, action):
        """
        :type action: lambda
        """
        super(DisposeTask, self).__init__()
        self.action = action
        self.__started = False

    def run(self):
        try:
            self.__started = True
            self.action()
        finally:
            self.dispose()

    def isDisposed(self):
        return not self.is_alive()

    def dispose(self):
        if self.__started and self.is_alive():
            self.terminate()
            self.__started = False


class Observable(ObservableSource):
    source = None

    def __init__(self, source):
        """
        
        :param ObservableSource source: 
        """
        assert isinstance(source, ObservableSource), "must be ObservableSource but %s" % source
        self.source = source

    @staticmethod
    def create(on_subscribe):
        return ObservableCreate(ObservableOnSubscribe.create(on_subscribe))

    @staticmethod
    def from_(iterable):
        def from_list(emitter):
            for i in iterable:
                emitter.onNext(i)
            emitter.onComplete()

        return ObservableCreate(ObservableOnSubscribe.create(from_list))

    def subscribe(self, observer):
        assert isinstance(observer, Observer)
        observer.onSubscribe(self)

    def blockingSubscribe(self, on_next=EMPTY_CONSUMER, on_error=EMPTY_CONSUMER, on_complete=EMPTY_ACTION):
        return ObservableBlockingSubscribe.subscribe(self, LambdaObserver(on_next, on_error, on_complete))

    def map(self, func):
        return ObservableMap(self, func)

    def flatMap(self, mapper_func, maxConcurrency=1, bufferSize=128):
        return ObservableFlatMap(self, mapper_func, maxConcurrency, bufferSize)

    def doOnNext(self, func):
        return self.doOnEach(on_next=func, on_error=EMPTY_CONSUMER, on_complete=EMPTY_ACTION,
                             on_after_terminate=EMPTY_ACTION)

    def doOnError(self, func):
        return self.doOnEach(on_next=EMPTY_CONSUMER, on_error=func, on_complete=EMPTY_ACTION,
                             on_after_terminate=EMPTY_ACTION)

    def doOnEach(self, on_next, on_error, on_complete, on_after_terminate):
        return ObservableOnEach(self, on_next, on_error, on_complete, on_after_terminate)

    def observeOn(self, process_constructor):
        """
        process - lambda 
        :type process_constructor: mutliprocessing.Process
        """
        return ObservableObserveOn(self, process_constructor, False, 42 * 10 * 8)

    def subscribeOn(self, process_constructor):
        """

        :type process_constructor: multiprocessing.Process
        """
        return ObservableSubscribeOn(self, process_constructor)

    def toList(self):
        return ObservableToListSingle(self)


class ObservableOnEach(Observable, ObservableSource):
    def __init__(self, source, on_next, on_error, on_complete, on_after_terminate):
        """
        
        :param ObservableSource source: 
        :param on_next: 
        :param on_error: 
        :param on_complete: 
        :param on_after_terminate: 
        """
        super(ObservableOnEach, self).__init__(source)
        self._on_next = on_next
        self._on_error = on_error
        self._on_complete = on_complete
        self._on_after_terminate = on_after_terminate

    def subscribe(self, observer):
        class DoOnEachObserver(Observer, Disposable):
            def __init__(self, actual, on_next, on_error, on_complete, on_after_terminate):
                """
                :param Observer actual: 
                :param on_next: 
                :param on_error: 
                :param on_complete: 
                :param on_after_terminate: 
                """
                self.actual = actual
                self.on_next = on_next
                self.on_error = on_error
                self.on_complete = on_complete
                self.on_after_terminate = on_after_terminate
                self.s = None

            def isDisposed(self):
                self.s.isDisposed()

            def dispose(self):
                self.s.dispose()

            def onComplete(self):
                self.on_complete()
                self.actual.onComplete()

            def onSubscribe(self, disposable):
                self.s = disposable
                self.actual.onSubscribe(self)

            def onError(self, err):
                self.on_error(err)
                self.actual.onError(err)

            def onNext(self, t):
                self.on_next(t)
                self.actual.onNext(t)

        o = DoOnEachObserver(observer, self._on_next, self._on_error, self._on_complete, self._on_after_terminate)
        self.source.subscribe(o)
        return o


class ObservableCreate(Observable):
    class CreateEmitter(ObservableEmitter, Disposable):

        def __init__(self, observer_):
            self._disposable = None
            self._observer = observer_

        def onNext(self, t):
            if not self.isDisposed():
                self._observer.onNext(t)

        def onComplete(self):
            if not self.isDisposed():
                try:
                    self._observer.onComplete()
                except Exception as err:
                    self.dispose()

        def onError(self, err):
            self._observer.onError(err)

        def setDisposable(self, disposable):
            """

            :type disposable: Disposable
            """
            assert isinstance(disposable, Disposable), "must be Disposable but %s" % disposable
            if self._disposable:
                self._disposable.dispose()

            self._disposable = disposable

        def isDisposed(self):
            return self._disposable is not None and self._disposable.isDisposed()

        def dispose(self):
            if self._disposable:
                self._disposable.dispose()

            self._disposable = None

    def __init__(self, source):
        """

        :type source: ObservableOnSubscribe
        """
        assert isinstance(source, ObservableOnSubscribe), "source must be ObservableOnSubscribe but %s" % type(source)
        super(ObservableCreate, self).__init__(source)

    def subscribe(self, observer):
        assert isinstance(observer, Observer)
        parent = ObservableCreate.CreateEmitter(observer)
        observer.onSubscribe(parent)
        try:
            self.source.subscribe(parent)
            return observer
        except Exception:
            # THROW_IF_FATAL(err)
            parent.onError(sys.exc_info())


class ObservableMap(Observable, ObservableSource):
    source = None
    func = None

    def __init__(self, source, func):
        super(ObservableMap, self).__init__(source)
        self.func = func

    def subscribe(self, observer):
        """
        :param LambdaObserver observer: 
        :return: Disposable
        """

        class MapObserver(BasicObserver):

            def __init__(self, actual, mapper):
                """

                :type mapper: callable
                :type actual: Observer
                """
                super(MapObserver, self).__init__(actual)
                self.mapper = mapper

            def onNext(self, t):
                try:
                    return self.actual.onNext(self.mapper(t))
                except Exception as err:
                    self.actual.dispose()
                    self.actual.onError(sys.exc_info())

        o = MapObserver(observer, self.func)
        self.source.subscribe(o)
        return o


class ObservableFlatMap(Observable, ObservableSource):
    class MergeObserver(Observer, Disposable):
        _canceled = True
        _done = False
        _error = None
        disposable = None
        _wip = 0

        def __init__(self, child, mapper, maxConcurrency, bufferSize):
            """

            :type mapper: callable
            :type child: Observer
            """
            assert isinstance(child, Observer), "child must be Observer but %s" % type(child)
            self._observer = None
            self.bufferSize = bufferSize
            self.maxConcurrency = maxConcurrency
            self.child = child
            self.mapper = mapper
            self._sources = collections.deque()

        def onSubscribe(self, disposable):
            self.disposable = disposable
            self.child.onSubscribe(self)

        def onError(self, err):
            self._error = err
            self.child.onError(err)

        def isDisposed(self):
            return self._canceled

        def onComplete(self):
            if self._done:
                return None
            self._done = True
            self.child.onComplete()

        def onNext(self, t):
            inner_source = self.mapper(t)
            assert isinstance(inner_source,
                              ObservableSource), "flatMap function result must be Observable but %s" % inner_source

            if self._wip == self.maxConcurrency:
                # TODO
                self._sources.append(inner_source)
                return None

            class InnerObserver(BasicObserver):
                def onComplete(self):
                    pass

                def onNext(self, _t):
                    self.actual.onNext(_t)

            o = InnerObserver(self.child)
            self._observer = o
            inner_source.subscribe(o)

        def dispose(self):
            self._canceled = True
            self.disposeAll()

        def disposeAll(self):
            self._observer.dispose()

    def __init__(self, source, mapper, maxConcurrency, bufferSize):
        """

        :type source: ObservableSource
        """
        super(ObservableFlatMap, self).__init__(source)
        self.bufferSize = bufferSize
        self.maxConcurrency = maxConcurrency
        self.mapper = mapper

    def subscribe(self, observer):
        assert isinstance(observer, Observer), "observer must be Observer type but %s" % type(observer)
        o = ObservableFlatMap.MergeObserver(observer, self.mapper, self.maxConcurrency, self.bufferSize)
        self.source.subscribe(o)
        return o.disposable


class ObservableOnSubscribe(ObservableSource):
    def __init__(self):
        self.__on_subscribe = None

    @staticmethod
    def create(on_subscribe):
        assert callable(on_subscribe), "must be a function %s" % repr(on_subscribe)
        o = ObservableOnSubscribe()
        o.__on_subscribe = on_subscribe
        return o

    def subscribe(self, observable_emitter):
        isinstance(observable_emitter, Emitter)
        self.__on_subscribe(observable_emitter)


class ObservableToListSingle(Single):
    class ToListObserver(Observer, Disposable):
        def __init__(self, actual):
            """

            :type actual: SingleObserver
            """
            self.actual = actual
            self.collection = []
            self.s = None

        def isDisposed(self):
            self.s.isDisposed()

        def dispose(self):
            self.s.dispose()

        def onComplete(self):
            self.actual.onSuccess(self.collection)

        def onSubscribe(self, disposable):
            if not self.s:
                self.s = disposable
                self.actual.onSubscribe(self)

        def onError(self, err):
            self.collection = None
            self.actual.onError(err)

        def onNext(self, t):
            self.collection.append(t)

    def __init__(self, observable_source):
        """

        :type observable_source: ObservableSource
        """
        assert isinstance(observable_source, ObservableSource), \
            "must be ObservableSource but %s" % type(observable_source)

        self.source = observable_source

    def subscribe(self, single_observer):
        """

        :type single_observer: SingleObserver
        """
        assert isinstance(single_observer, SingleObserver), \
            "`actual` must be SingleObserver type but %s" % type(single_observer)
        observer = ObservableToListSingle.ToListObserver(single_observer)
        self.source.subscribe(observer)
        return observer


class ObservableObserveOn(Observable, ObservableSource):
    class ObserveOnObserver(Observer, Disposable, multiprocessing.Process):
        def __init__(self, actual, delayError, bufferSize):
            """

            :type actual: Observer
            """
            super(ObservableObserveOn.ObserveOnObserver, self).__init__()

            self.actual = actual
            self.delayError = delayError
            self.bufferSize = bufferSize
            self.s = None
            self.queue = queues.Queue(maxsize=self.bufferSize)
            self.done = False
            self.error = None
            self.canceled = False

        def onSubscribe(self, disposable):
            self.s = disposable
            self.actual.onSubscribe(self)

        def onNext(self, t):
            if self.done:
                return
            self.queue.put(t)

        def onError(self, err):
            self.error = err
            self.done = True

        def onComplete(self):
            if self.done:
                return True
            self.done = True

        def isDisposed(self):
            return self.canceled

        def dispose(self):
            if not self.canceled:
                self.canceled = True
                self.s.dispose()

        def run(self):
            try:
                while True:
                    if self.done:
                        break

                    v = None
                    try:
                        v = self.queue.get(timeout=1)
                    except queues.Empty:
                        continue
                    except Exception as err:
                        log.error("error", exc_info=True)
                        self.actual.onError(sys.exc_info())
                        self.dispose()
                        self.queue.close()
                        return

                    if self.canceled:
                        self.queue.close()
                        return
                    if self.error:
                        self.actual.onError(self.error)
                        self.queue.close()
                        return

                    if v is None:
                        self.actual.onComplete()
                        self.queue.close()
                        return

                    self.actual.onNext(v)
            except Exception as err:
                log.error("meh", exc_info=True)
                self.error = err
                self.actual.onError(sys.exc_info())
                self.dispose()
                self.queue.close()

    def __init__(self, source, process, delayError, bufferSize):
        super(ObservableObserveOn, self).__init__(source)
        self.source = source
        self.process = process
        self.delayError = delayError
        self.bufferSize = bufferSize

    def subscribe(self, observer):
        isinstance(observer, Observer), "observer must be Observer type not %s" % type(observer)
        proc = ObservableObserveOn.ObserveOnObserver(observer, self.delayError, self.bufferSize)
        proc.start()
        self.source.subscribe(proc)


class ObservableSubscribeOn(Observable, ObservableSource):
    class SubscribeOnObserver(Observer, Disposable):
        def __init__(self, actual):
            """

            :type actual: Observer
            """
            self.actual = actual
            self.s = None

        def onError(self, err):
            self.actual.onError(err)

        def onSubscribe(self, disposable):
            self.s = disposable

        def onComplete(self):
            self.actual.onComplete()

        def onNext(self, t):
            self.actual.onNext(t)

        def isDisposed(self):
            return self.s is None

        def dispose(self):
            self.s.dispose()
            self.s = None

        def setDisposable(self, d):
            self.s = d

    def __init__(self, source, runnable):
        """

        :type source: ObservableSource
        :type runnable: multiprocessing.Process
        """

        super(ObservableSubscribeOn, self).__init__(source)
        self.source = source
        self.runnable = runnable

    def subscribe(self, observer):
        parent = ObservableSubscribeOn.SubscribeOnObserver(observer)
        observer.onSubscribe(parent)

        def subscribe_task():
            self.source.subscribe(parent)

        task = DisposeTask(subscribe_task)
        parent.setDisposable(task)
        task.start()
