import asyncio
import concurrent

class CoroQueue(object):
    """
    A queue of coroutines to be called sequentially.
    """
    def __init__(self, loop):
        self.loop = loop
        self.__queue = asyncio.Queue()
        self.__waiter = None
        self.__cancelled = False

    def schedule_run_forever(self):
        """
        Schedule asyncio to run the consumer loop.
        """
        self.__task_run_forever = self.loop.create_task(self.__run_forever())

    async def __run_one(self):
        coro, future = await self.__queue.get()

        try:
            res = await coro
        except Exception as e:
            future.set_exception(e)
        else:
            future.set_result(res)

    async def __run_forever(self):
        """
        The consumer loop.
        Loop forever getting the next coroutine in the queue and awaiting it.
        """
        while True:
            if self.__waiter:
                if self.__queue.empty():
                    self.__waiter.set_result(None)
            
            await self.__run_one()

    def put_nowait(self, f, *args, **kwargs):
        """
        Put a coroutine onto the queue.

        :param f: a coroutine function
        :param args: arguments to be passed to the coroutine
        """

        future = self.loop.create_future()
        coro = f(*args, **kwargs)
        
        if not asyncio.iscoroutine(coro):
            raise RuntimeError('{} is not a coroutine'.format(f))
        
        self.__queue.put_nowait((coro, future))

        return future

    async def close(self):
        """
        Cancel all pending coroutines.
        """
        self.__cancelled = True
        self.__task_run_forever.cancel()
        try:
            await self.__task_run_forever
        except concurrent.futures.CancelledError as e: pass
        
        while not self.__queue.empty():
            item = self.__queue.get_nowait()
            coro, future = item
            
            task = self.loop.create_task(coro)

            ret = task.cancel()
            
            try:
                res = await task
            except concurrent.futures.CancelledError as e:
                pass

    async def join(self):
        """
        Wait for all coroutines to finish.
        Await the underlying :py:class:`asyncio.Queue` object's join method.
        """
        if self.__queue.empty():
            return
        
        assert self.__waiter is None
        self.__waiter = self.loop.create_future()
        await self.__waiter
        self.__waiter = None

class CoroQueueClass:
    _coro_queue = None

    @classmethod
    def wrap(cls, f):
        def wrapped(self, *args, **kwargs):
            return self.coro_queue.put_nowait(f, *args, **kwargs)
        return wrapped

    @property
    def coro_queue(self):
        if self._coro_queue is None:
            self._coro_queue = CoroQueue(self._loop)
            self._coro_queue.schedule_run_forever()
        return self._coro_queue






