
# Run with pytest.

import asyncio
import pytest

from .import testutils
testutils.add_to_path()

import pglib

CONNINFO = 'dbname=test'


@pytest.fixture(autouse=True)
def cleanup():
    """
    Called before each test (due to autouse) to drop tables t1, t2, and t3.

    Use these table names in your tests.
    """
    # Note that I'm not using "if exists" because that annoyingly prints a notice.
    cnxn = pglib.connect(CONNINFO)
    for i in range(3):
        try:
            cnxn.execute("drop table t%d" % i)
        except:
            pass
    yield cnxn
    cnxn.close()


def test_async():
    async def _t():
        cnxn = await pglib.connect_async(CONNINFO)
        await cnxn.execute("create table t1(a varchar(20), b int)")
        await cnxn.execute("insert into t1 values ('abc', 3)")
        rset = await cnxn.execute("select a, b from t1")
        for row in rset:
            assert row.a == 'abc'
            assert row[0] == 'abc'
            assert row.b == 3
            assert row[1] == 3

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_t())


def test_async_params():
    async def _t():
        cnxn = await pglib.connect_async(CONNINFO)
        await cnxn.execute("create table t1(a varchar(20), b int)")
        await cnxn.execute("insert into t1(a, b) values ($1, $2)", 'abc', 2)
        rset = await cnxn.execute("select a, b from t1")
        for row in rset:
            assert row.a == 'abc'
            assert row[0] == 'abc'
            assert row.b == 2
            assert row[1] == 2

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_t())


def test_async_notify():
    async def _t():
        cnxn = await pglib.connect_async(CONNINFO)

        await cnxn.listen('test')

        sent = [('test', ''), ('test', 'payload')]
        # Note: You can pass None as the payload, but PostgreSQL will pass it along as an empty
        # string.  (Is this documented somewhere?)

        for t in sent:
            await cnxn.notify(*t)

        # We may get 1 or we may get 2.  Keep calling until we get both.
        while sent:
            ns = await cnxn.notifications()
            for item in ns:
                assert item == sent[0]
                sent.pop(0)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_t())


def test_notify_and_command():
    "Ensure the same cnxn can be used for notifications and commands"

    async def _t():
        cnxn = await pglib.connect_async(CONNINFO)
        await cnxn.listen('test')

        await cnxn.notify('test', 'both')
        ns = await cnxn.notifications()
        assert ns is not None
        assert len(ns) == 1
        item = ns[0]
        assert item == ('test', 'both')

        value = await cnxn.fetchval("select 1")
        assert value == 1

        await cnxn.notify('test', 'both')
        ns = await cnxn.notifications()
        assert ns is not None
        assert len(ns) == 1
        item = ns[0]
        assert item == ('test', 'both')

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_t())


def test_notification_wait():
    "wait for notifications from another cnxn"

    async def _listener():
        cnxn = await pglib.connect_async(CONNINFO)
        await cnxn.listen('test')
        ns = await cnxn.notifications()
        assert ns == [('test', '')]

    async def _notifier():
        # We don't know which of these will run first (I don't know, at least), so make sure we
        # switch to the listener if this runs first.
        await asyncio.sleep(0.25)
        cnxn = await pglib.connect_async(CONNINFO)
        await cnxn.notify('test')

    both = asyncio.gather(_listener(), _notifier())
    loop = asyncio.get_event_loop()
    loop.run_until_complete(both)


def test_notification_timeout():
    async def _t():
        cnxn = await pglib.connect_async(CONNINFO)
        await cnxn.listen('test')
        ns = await cnxn.notifications(timeout=0.25)
        assert ns == []

    loop = asyncio.get_event_loop()
    loop.run_until_complete(_t())
