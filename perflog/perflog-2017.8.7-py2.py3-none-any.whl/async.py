import asyncio
import functools
import psutil
import typing
from perflog import PerfSection, single_pass, logger


if typing.TYPE_CHECKING:
    from typing import Optional, FrozenSet


async def single_pass_async(
        process=None,  # type: Optional[psutil.Process]
        sections=frozenset(PerfSection),  # type: FrozenSet[PerfSection]
        loop=None   # type: Optional[asyncio.AbstractEventLoop]
):
    # type: (...) -> None
    """ Put an asyncio-compatible layer over the blocking call. """
    loop = loop or asyncio.get_event_loop()
    fn = functools.partial(single_pass, process, sections)
    await loop.run_in_executor(None, fn)


async def multi_pass_async(
        process=None,  # type: Optional[psutil.Process]
        sections=frozenset(PerfSection),  # type: FrozenSet[PerfSection]
        interval=60.0,  # type: int
        loop=None  # type: Optional[asyncio.AbstractEventLoop]
):
    # type: (...) -> None
    process = process or psutil.Process()
    while True:
        try:
            await single_pass_async(process, sections, loop=loop)
        except:  # pragma: no cover
            logger.exception('Problem logging perf stats:')
        finally:
            await asyncio.sleep(interval, loop=loop)
