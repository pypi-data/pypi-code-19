""" Performance stats logger """
import sys
import time
import logging
import json
import functools
from collections import Counter
import threading
import typing
import enum
import psutil


__version__ = '2017.8.2'


PY_VERSION = (sys.version_info.major, sys.version_info.minor)
ASYNCIO_ALLOWED = PY_VERSION >= (3, 5)
if ASYNCIO_ALLOWED:
    import asyncio


if typing.TYPE_CHECKING:
    from typing import NamedTuple, FrozenSet, Optional


logger = logging.getLogger('perflog')


@enum.unique
class PerfSection(enum.IntEnum):
    CPU = 1
    MEM = 2
    NET = 3
    NET_DETAIL = 4


def _perf_log(message, nt, level=logging.INFO, field_prefix=''):
    # type: (str, NamedTuple, int, str) -> None
    # Use a field prefix to avoid collisions with the logrecord fields.
    d = {field_prefix + k: v for k, v in nt._asdict().items()}
    logger.log(level, message, json.dumps(d, indent=2), extra=d)


def single_pass(process=None, sections=frozenset(PerfSection)):
    # type: (psutil.Process, FrozenSet[PerfSection]) -> None
    process = process or psutil.Process()

    if PerfSection.CPU in sections:
        cpu_times = process.cpu_times()
        _perf_log('CPU times = %s', cpu_times, field_prefix='cpu_')

        cpu_percent = process.cpu_percent(interval=1)
        logger.info(
            'CPU Percent = %s',
            cpu_percent,
            extra=dict(cpu_percent=cpu_percent)
        )

    if PerfSection.MEM in sections:
        vmem = psutil.virtual_memory()
        _perf_log('Virtual memory = %s', vmem, field_prefix='vmem_')
        mem_info = process.memory_full_info()
        _perf_log('Proc memory info = %s', mem_info, field_prefix='mem_')

    if PerfSection.NET in sections:
        net_info = psutil.net_io_counters()
        _perf_log('Network info = %s', net_info, field_prefix='net_')

        conn_info = process.connections()
        logger.info(
            'Total Network connections = %d', len(conn_info),
            extra=dict(tot_connections=len(conn_info))
        )

    if PerfSection.NET_DETAIL in sections:
        # Counter on remote address & port tuples
        counter = Counter(c.raddr for c in conn_info)
        logger.info(
            'Connections to remote addresses = %s',
            counter
        )
        if len(conn_info) <= 10:
            for conn in conn_info:
                _perf_log(
                    'Detailed connection info = %s',
                    conn,
                    field_prefix='conn_'
                )


def multi_pass_blocking(process=None, sections=frozenset(PerfSection), interval=60.0):
    # type: (psutil.Process, FrozenSet[PerfSection], float) -> None
    process = process or psutil.Process()
    while True:
        try:
            single_pass(process, sections)
        except:
            logger.exception('Problem logging perf stats:')
        finally:
            time.sleep()


def set_and_forget(process=None, sections=frozenset(PerfSection), interval=60.0):
    # type: (psutil.Process, FrozenSet[PerfSection], float) -> None
    """ Creates a daemon thread that simply logs perf stats forever. This is
    obviously also compatible with asyncio, since it runs in a thread. """
    process = process or psutil.Process()
    thread = threading.Thread(
        target=multi_pass_blocking,
        name='perflog',
        args=(),
        kwargs=dict(process=process, sections=sections),
    )
    thread.daemon = True
    thread.start()


################################################################################


if ASYNCIO_ALLOWED:
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
            except:
                logger.exception('Problem logging perf stats:')
            finally:
                await asyncio.sleep(interval, loop=loop)
