import asyncio
import collections
import concurrent
import functools
import math
import os
import threading
import sys
import time

DEFAULT_TIMEOUT=30

if sys.version_info >= (3, 4, 4):
    run_coroutine_threadsafe = asyncio.run_coroutine_threadsafe
else:
    def run_coroutine_threadsafe(coroutine, loop):
        future = concurrent.futures.Future()

        def callback():
            try:
                chain_futures( asyncio.async(coroutine, loop=loop), future )
            except Exception as exc:
                if future.set_running_or_notify_cancel():
                    future.set_exception(exc)
                raise

        loop.call_soon_threadsafe(callback)
        return future

def rad2deg(rad):
    return rad*180/math.pi

def deg2rad(deg):
    return deg*math.pi/180

def chain_futures(fut1, fut2, conv=lambda x: x):
    def done(fut2, conv, fut1):
        if fut1.cancelled():
            fut2.cancel()
        else:
            try:
                fut2.set_result( conv(fut1.result()) )
            except Exception as e:
                fut2.set_exception(e)

    fut1.add_done_callback(
            functools.partial(
                done,
                fut2,
                conv)
            )

def run_linkbot_coroutine(coro, loop):
    my_config = Config()
    fut = run_coroutine_threadsafe(coro, loop)
    fut2 = fut.result(timeout=my_config.timeout)
    result = run_coroutine_threadsafe(
            asyncio.wait_for(fut2, timeout=my_config.timeout), loop)
    return result.result()

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Config(metaclass=Singleton):
    def __init__(self):
        if os.environ.get('LINKBOT_USE_SFP'):
            self._use_websockets = False
        else:
            self._use_websockets = True

        try:
            self._daemon_host = os.environ['LINKBOT_DAEMON_HOSTPORT'].split(':')
        except:
            self._daemon_host = 'localhost:42000'.split(':')

        self._linkbot_ids_index = 0
        try:
            self._linkbot_ids = os.environ['ROBOTMANAGER_IDS'].split(',')[:-1]
        except KeyError:
            self._linkbot_ids = []

        self._timeout = DEFAULT_TIMEOUT

    @property
    def use_websockets(self):
        return self._use_websockets

    @use_websockets.setter
    def use_websockets(self, value):
        self._use_websockets = value

    @property
    def daemon_host(self):
        return self._daemon_host

    @daemon_host.setter
    def daemon_host(self, value):
        self._daemon_host = value.split(':')

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value

    @property
    def linkbot(self):
        '''Returns the next ROBOTMANAGER ID or throws exception'''
        try:
            serial_id = self._linkbot_ids[self._linkbot_ids_index]
            self._linkbot_ids_index += 1
            return serial_id
        except IndexError:
            raise Exception("Insufficient robots connected in Robot Manager")
            

class IoCore(metaclass=Singleton):
    def __init__(self):
        self._initializing = True
        self._initializing_sig = threading.Condition()
        self.loop = None
        self._thread = threading.Thread(target=self._work)
        self._thread.daemon = True
        self.start_work()

    def start_work(self):
        if self._thread.is_alive():
            return
        self._thread.start()

        self._initializing_sig.acquire()
        while self._initializing:
            self._initializing_sig.wait(timeout=1)
        self._initializing_sig.release()

    def stop_work(self):
        self.loop.stop()

    def get_event_loop(self):
        return self.loop

    def _work(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._initializing_sig.acquire()
        self._initializing = False
        self._initializing_sig.notify_all()
        self._initializing_sig.release()
        self.loop.run_forever()

class SortedList():
    def __init__(self, key=None):
        self._members = []
        self._key = key
        self._waiters = collections.deque()

    @asyncio.coroutine
    def add(self, item):
        self._members.append(item)
        self._members.sort(key=self._key)
        if len(self._waiters) > 0:
            waiter = self._waiters.popleft()
            waiter.set_result(None)

    @asyncio.coroutine
    def popleft(self):
        while len(self._members) == 0:
            fut = asyncio.Future()
            self._waiters.append(fut)
            yield from fut
            if fut.cancelled():
                raise asyncio.QueueEmpty()
        return self._members.pop(0)

    @asyncio.coroutine
    def close(self):
        for w in self._waiters:
            w.cancel()

class TimeoutCore(metaclass=Singleton):
    def __init__(self, loop):
        self._event = asyncio.Event()
        self._cancelled = False
        # Each timeout object will be a (timestamp, asyncio.Future()) object.
        self._timeouts = SortedList(key=lambda x: x[0])
        loop.create_task(self._work())

    @asyncio.coroutine
    def add(self, fut, timeout):
        timestamp = time.time() + timeout
        yield from self._timeouts.add( (timestamp, fut) )
        self._event.set()

    @asyncio.coroutine
    def cancel(self):
        self._cancelled = True
        self._event.set()
   
    @asyncio.coroutine 
    def chain_futures(self, fut1, fut2, callback, timeout=DEFAULT_TIMEOUT):
        # Execute 'callback' when fut1 completes. fut2's result will be set to the
        # return value of 'callback'. If timeout is specified, fut2 will be
        # cancelled after the time specified by 'timeout' has lapsed.
        # Signature of callback should be callback(future) -> result

        def __handle_chain_futures(fut2, cb, fut1):
            if fut1.cancelled() and not fut2.done():
                fut2.cancel()
            else:
                fut2.set_result(cb(fut1))

        fut1.add_done_callback(
                functools.partial(__handle_chain_futures,
                                  fut2,
                                  callback
                                  )
                )
        if timeout:
            yield from self.add(fut2, timeout)

    @asyncio.coroutine
    def _work(self):
        while True:
            next_timeout = yield from self._timeouts.popleft()
            if next_timeout[0] > time.time():
                self._event.clear()
                try:
                    yield from asyncio.wait_for( self._event.wait(), 
                                            next_timeout[0]-time.time() )
                    # If we get here, the event was signalled. Check the
                    # cancellation flag
                    if self._cancelled:
                        break
                    else:
                        continue
                except asyncio.TimeoutError:
                    # Cancel the future if it is not done
                    if not next_timeout[1].done():
                        next_timeout[1].set_exception(
                                asyncio.TimeoutError('Future timeout out waiting for result.')
                                )

