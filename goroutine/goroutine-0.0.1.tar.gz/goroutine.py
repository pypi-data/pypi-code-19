#
# MIT License
#
# Copyright (c) 2014 goroutine project
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
import asyncio
import functools
import warnings
import greenlet


class GoroutineGreenlet(greenlet.greenlet):
    """Subclass of greenlet used by corolets."""


class GoroutineError(RuntimeError):
    """Error while running goroutine."""


class YieldFromRequest:
    """Request to yield from an asyncio.Future."""

    def __init__(self, future):
        self.future = future


def goroutine(func):
    """Decorator to create a goroutine."""

    @asyncio.coroutine
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        # Create a greenlet to keep track of the function's context.
        glet = GoroutineGreenlet(func)

        # Run the function until it switches back out.
        glet_result = glet.switch(*args, **kwargs)

        # If the greenlet isn't dead, check for a request to `yield from`.
        while not glet.dead:
            if isinstance(glet_result, YieldFromRequest):
                # Wait for the result of the future.
                try:
                    future_result = yield from glet_result.future
                except Exception as e:
                    # yield_from(future) raised an exception. Propagate it back to yield_from() to be re-raised.
                    glet_result = glet.switch(e)
                else:
                    # Send the future's result back to our function's greenlet.
                    glet_result = glet.switch(future_result)
            else:
                raise GoroutineError("unexpected result from goroutine: {!r}".format(glet_result))

        # Once the greenlet dies, return its result.
        return glet_result

    return wrapper


def in_goroutine():
    """Check if currently within a goroutine."""
    glet = greenlet.getcurrent()
    return isinstance(glet, GoroutineGreenlet)


def yield_from(future):
    """Use instead of `yield from` while within a goroutine."""
    if not in_goroutine():
        warnings.warn("yield_from should only be used within a real goroutine", RuntimeWarning, stacklevel=2)
    glet = greenlet.getcurrent()
    parent = glet.parent
    if parent is None:
        raise GoroutineError("cannot yield_from outside a goroutine or greenlet")
    call = YieldFromRequest(future)
    result = glet.parent.switch(call)
    if isinstance(result, Exception):
        raise result
    return result


def yield_from_or_block(future):
    """Within a goroutine, uses `yield_from`. Otherwise, use blocking call."""
    if in_goroutine():
        return yield_from(future)
    if asyncio.iscoroutine(future):
        future = asyncio.Task(future)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(future)
    return future.result()
