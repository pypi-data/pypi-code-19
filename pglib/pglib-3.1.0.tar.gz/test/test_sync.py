
# Run with pytest.

import sys, threading
from os.path import join, dirname, exists
from decimal import Decimal
from datetime import date, time, datetime, timedelta
import pytest

from .import testutils
testutils.add_to_path()

import pglib

CONNINFO = 'dbname=test'

STR_FENCEPOST_SIZES = [0, 1, 255, 256, 510, 511, 512, 1023, 1024, 2047, 2048, 4000, 4095, 4096,
                       4097, 10 * 1024, 20 * 1024]
STR_FENCEPOSTS = [testutils.generate_test_string(size) for size in STR_FENCEPOST_SIZES]


@pytest.fixture()
def cnxn():
    # Warning: If I don't manually close the connection, they are not getting deleted.  I don't
    # know if pytest saves them in some test context for each test or what.

    # Note that I'm not using "if exists" because that annoyingly prints a notice.
    cnxn = pglib.connect(CONNINFO)
    for i in range(3):
        try:
            cnxn.execute("drop table t%d" % i)
        except:
            pass
    yield cnxn
    cnxn.close()


def _test_strtype(sqltype, value, resulttype=None, colsize=None):
    assert colsize is None or isinstance(colsize, int), colsize
    assert colsize is None or (value is None or colsize >= len(value))

    cnxn = pglib.connect(CONNINFO)

    if colsize:
        sql = "create table t1(s %s(%s))" % (sqltype, colsize)
    else:
        sql = "create table t1(s %s)" % sqltype

    if resulttype is None:
        resulttype = type(value)

    cnxn.execute(sql)
    cnxn.execute("insert into t1 values($1)", value)
    v = cnxn.scalar("select * from t1")
    assert type(v) == resulttype

    if value is not None:
        assert len(v) == len(value)

    # To allow buffer --> db --> bytearray tests, always convert the input to the expected
    # result type before comparing.
    if type(value) is not resulttype:
        value = resulttype(value)

    assert v == value


def _test_type(type, values, round_to=None):
    """
    A generic function for testing inserting and selecting a single data type.

    type: The data type, such as "boolean".

    values: Either a single value or a list of values to insert and select.
        A column is created or each value.
    """
    cnxn = pglib.connect(CONNINFO)

    if not isinstance(values, (tuple, list)):
        values = [values]

    cols = [chr(ord('a') + i) for i in range(len(values))]

    create = "create table t1({})".format(','.join('%s %s' % (col, type) for col in cols))
    insert = "insert into t1 values ({})".format(','.join('$%s' % i for i in range(1, len(values) + 1)))
    select = "select {} from t1".format(','.join(cols))

    cnxn.execute(create)
    cnxn.execute(insert, *values)
    rset = cnxn.execute(select)
    row = rset[0]
    for (expected, value) in zip(values, row):
        if round_to:
            value = round(value, round_to)
        assert value == expected


def test_execute_ddl(cnxn):
    """
    Ensure we can execute a DDL command and that it returns None.
    """
    r = cnxn.execute("create table t1(a int, b int)")
    assert r is None


def test_iter(cnxn):
    cnxn.execute("create table t1(a varchar(20))")
    cnxn.execute("insert into t1 values ('abc')")
    rset = cnxn.execute("select * from t1")
    for row in rset:
        assert row.a == 'abc'
        assert row[0] == 'abc'


def test_iter_twice(cnxn):
    "Ensure results can be iterated over multiple times"
    cnxn.execute("create table t1(a varchar(20))")
    cnxn.execute("insert into t1 values ('abc')")
    rset = cnxn.execute("select * from t1")
    for row in rset:
        assert row.a == 'abc'
        assert row[0] == 'abc'
    count = 0
    for row in rset:
        count += 1
    assert count == 1


def test_script(cnxn):
    """
    Ensure a script (multiple statements) can be executed.
    """
    sql = """
    select 1;
    select 2;
    select 3;
    """
    cnxn.script(sql)


#
# copy
#

def _datapath(filename):
    path = join(dirname(__file__), filename)
    assert exists(path)
    return path


def test_copy_csv(cnxn):
    cnxn.execute("create table t1(a int, b varchar(20))")
    cnxn.copy_from_csv("t1", open(_datapath('test-noheader.csv')))
    assert 2 == cnxn.scalar("select count(*) from t1")
    row = cnxn.row("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == 'two'


def test_copy_csv_header(cnxn):
    cnxn.execute("create table t1(a int, b varchar(20))")
    cnxn.copy_from_csv("t1", open(_datapath('test-header.csv')), header=True)
    assert 2 == cnxn.scalar("select count(*) from t1")
    row = cnxn.row("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == 'two'


def test_copy_csv_gzip(cnxn):
    import gzip
    cnxn.execute("create table t1(a int, b varchar(20))")
    cnxn.copy_from_csv("t1", gzip.open(_datapath('test-header.csv.gz')), header=True)
    assert 2 == cnxn.scalar("select count(*) from t1")
    row = cnxn.row("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == 'two'


def test_copy_csv_string(cnxn):
    cnxn.execute("create table t1(a int, b varchar(20))")
    cnxn.copy_from_csv("t1", '1,"one"\n2,"two"')
    row = cnxn.row("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == 'two'


def test_copy_csv_string_cols(cnxn):
    cnxn.execute("create table t1(a int, b varchar(20))")
    cnxn.copy_from_csv("t1(b, a)", '"one",1\n"two",2')  # reverse order of cols
    row = cnxn.row("select a,b from t1 where a=2")
    assert row.a == 2
    assert row.b == 'two'


#
# row
#


def test_row_zero(cnxn):
    cnxn.execute("create table t1(a int)")
    value = cnxn.row("select a from t1")
    assert value is None


def test_row_one(cnxn):
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (2)")
    value = cnxn.row("select a from t1")
    assert value[0] == 2


def test_row_many(cnxn):
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (1), (2)")
    with pytest.raises(pglib.Error):
        cnxn.row("select a from t1")


def test_fetchrow(cnxn):
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (2)")
    value = cnxn.fetchrow("select a from t1")
    assert value[0] == 2


def test_fetchrow_none(cnxn):
    cnxn.execute("create table t1(a int)")
    value = cnxn.fetchrow("select a from t1")
    assert value is None


def test_fetchval(cnxn):
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (2)")
    value = cnxn.fetchval("select a from t1")
    assert value == 2


def test_fetchval_none(cnxn):
    cnxn.execute("create table t1(a int)")
    value = cnxn.fetchval("select a from t1")
    assert value is None


#
# resultset
#


def test_rset_length(cnxn):
    """
    Ensure the len(ResultSet) returns the number of rows.
    """
    cnxn.execute("create table t1(i int)")
    count = 4
    for i in range(count):
        cnxn.execute("insert into t1 values ($1)", i)
    rset = cnxn.execute("select * from t1")
    assert len(rset) == 4


def test_rset_index(cnxn):
    """
    Ensure we can indexing into the ResultSet returns a Row.
    """
    cnxn.execute("create table t1(i int)")
    count = 4
    for i in range(count):
        cnxn.execute("insert into t1 values ($1)", i)
    rset = cnxn.execute("select * from t1")
    row = rset[2]
    assert row[0] == 2


def test_rset_nonzero(cnxn):
    """
    Ensure a resultset with no rows is "falsey".
    """
    cnxn.execute("create table t1(i int)")
    rset = cnxn.execute("select * from t1")
    assert rset is not None
    assert not rset

    cnxn.execute("insert into t1 values (1), (2)")
    rset = cnxn.execute("select * from t1")
    assert rset is not None
    assert rset


#
# fetchval
#

def test_fetchval_zero(cnxn):
    """
    Ensure cnxn.scalar() returns None if no rows are selected.
    """
    cnxn.execute("create table t1(a int)")
    value = cnxn.fetchval("select a from t1")
    assert value is None


def test_fetchval_one(cnxn):
    """
    Ensure cnxn.fetchval() returns the first column if one row is selected.
    """
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (1)")
    value = cnxn.fetchval("select a from t1")
    assert value == 1


def test_fetchval_many(cnxn):
    """
    Ensure cnxn.fetchval() raises an exception if multiple rows are selected.
    """
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (1), (2)")
    with pytest.raises(pglib.Error):
        cnxn.fetchval("select a from t1")


#
# tuple
#


def test_row_to_tuple(cnxn):
    cnxn.execute("create table t1(a varchar(20), b int)")
    cnxn.execute("insert into t1 values ('one', 1)")
    rset = cnxn.execute("select a,b from t1")
    for row in rset:
        t = tuple(row)
        assert t == ('one', 1)

#
# boolean
#


def test_boolean(cnxn):
    _test_type('boolean', [True, False])


#
# numeric
#


def test_smallint(cnxn):
    _test_type('smallint', [-32768, -2, -1, 0, 1, 2, 32767])


def test_integer(cnxn):
    _test_type('integer', [-2147483648, -32768, -2, -1, 0, 1, 2, 32767, 2147483647])


def test_bigint(cnxn):
    _test_type('bigint',
               [-9223372036854775808, -2147483648, -32768, -2, -1, 0,
                1, 2, 32767, 2147483647, 9223372036854775807])


def test_float4(cnxn):
    # Careful.  Python doesn't have a float4 datatype, so an float8 is returned.  Unfortunately this means values
    # won't always match even though they "look" like they do when you print them.
    _test_type('float4', [1.2, -3.4], round_to=2)


def test_float8(cnxn):
    _test_type('float8', [1.2, -3.4])


def test_decimal(cnxn):
    values = [Decimal(s) for s in ['-3.0000000', '123456.7890']]
    _test_type('decimal(100,7)', values)


def test_money(cnxn):
    values = [Decimal(s) for s in ['1.23', '0.0', '123.45', '-12.34']]
    _test_type('money', values)


# Decimal objects are constructed by first making a string, which we make in
# English ("12.34").  Make sure that changing the locale to one that uses
# "," doesn't trip us up.  (I'm not sure why it doesn't.  Ideally we should
# work on using a different constructor.)  You'll notice that Decimal still
# parses the values we pass as strings before we even get to pglib.


def test_decimal_german(cnxn):
    import locale
    locale.setlocale(locale.LC_ALL, 'de_DE')
    values = [Decimal(s) for s in ['-3.0000000', '123456.7890']]
    _test_type('decimal(100,7)', values)


def test_money_german(cnxn):
    import locale
    locale.setlocale(locale.LC_ALL, 'de_DE')
    values = [Decimal(s) for s in ['1.23', '0.0', '123.45', '-12.34']]
    _test_type('money', values)


def test_decimal_nan(cnxn):
    dec = Decimal('NaN')
    cnxn.execute("create table t1(a decimal(100,7))")
    cnxn.execute("insert into t1 values($1)", dec)
    result = cnxn.fetchval("select a from t1")
    assert type(result) == Decimal
    assert result.is_nan()


def test_serial(cnxn):
    cnxn.execute("create table t1(a serial, b varchar(20))")
    cnxn.execute("insert into t1(b) values ('one')")
    cnxn.execute("insert into t1(a, b) values (2147483647, 'max')")
    for value in [1, 2147483647]:
        result = cnxn.fetchval("select a from t1 where a=$1", value)
        assert result == value


#
# varchar
#


def test_varchar_null(cnxn):
    _test_strtype('varchar', None, colsize=100)


# Generate a test for each fencepost size: test_varchar_0, etc.

def _maketest(value):
    def t(cnxn):
        _test_strtype('varchar', value, colsize=len(value))
    return t


for value in STR_FENCEPOSTS:
    locals()['test_varchar_%s' % len(value)] = _maketest(value)

#
# char
#


def test_char_null(cnxn):
    _test_strtype('char', None, colsize=100)


# Generate a test for each fencepost size: test_char_1, etc.
#
# Note: There is no test_char_0 since they are blank padded.

def _maketest(value):
    def t(cnxn):
        _test_strtype('char', value, colsize=len(value))
    return t


for value in [v for v in STR_FENCEPOSTS if len(v) > 0]:
    locals()['test_char_%s' % len(value)] = _maketest(value)


#
# bytea / bytearray
#


def test_bytea(cnxn):
    # Add a NULL byte in the middle to ensure strcpy isn't being used.
    value = b'\xde\xad\x00\xbe\xef'
    cnxn.execute("create table t1(a bytea)")
    cnxn.execute("insert into t1 values ($1)", value)
    result = cnxn.fetchval("select * from t1")
    assert value == result

# def test_bytea_wrongtype(cnxn):
#     # Add a NULL byte in the middle to ensure strcpy isn't being used.
#     value = (b'\x80\x03cmtech.cornerstone.sessions\nSession\nq\x00)\x81q\x01}q\x02(X\x07\x00\x00\x00user_idq\x03NX\t\x00\x00\x00user_nameq\x04NX\x0b\x00\x00\x00permissionsq\x05cbuiltins\nset\nq\x06]q\x07\x85q\x08Rq\tub.',)
#     cnxn.execute("create table t1(a bytea)")
#     cnxn.execute("insert into t1 values ($1)", value)
#     result = cnxn.fetchval("select * from t1")
#     assert value == result


#
# date / timestamp
#


def test_date(cnxn):
    _test_type('date', date(2001, 2, 3))


def test_time(cnxn):
    value = time(12, 34, 56)
    cnxn.execute("create table t1(a time)")
    cnxn.execute("insert into t1 values ($1)", value)
    result = cnxn.fetchval("select a from t1")
    assert result == value


def test_timestamp(cnxn):
    cnxn.execute("create table t1(a timestamp)")
    value = datetime(2001, 2, 3, 4, 5, 6, 7)
    cnxn.execute("insert into t1 values ($1)", value)
    result = cnxn.fetchval("select a from t1")
    assert result == value


def test_interval(cnxn):
    cnxn.execute("create table t1(a interval)")
    value = timedelta(days=3, hours=4, minutes=5, seconds=6)
    cnxn.execute("insert into t1 values ($1)", value)
    result = cnxn.fetchval("select a from t1")
    assert result == value


#
# Error Handling
#

# def test_error_param_count(cnxn):
#     """
#     Was seeing a segfault on OS/X when performing an update with 3 parameters
#     but supplying only 2 values.  There doesn't seem to be a way to determine this.
#     """
#     cnxn.execute("create table t1(a varchar(20), b varchar(20), c text)")
#     cnxn.execute("insert into t1(a) values ('1')")
#     with pytest.raises(pglib.Error):
#         cnxn.execute("update t1 set b=$1, c=$2 where a=$1",
#                           'xyz',
#                           # purposely leave out value for 'c'
#                           '1')

#
# array of parameters
#

def test_array_int2(cnxn):
    cnxn.execute("create table t1(id int, v int[])")
    value = [None, -32768, -2, -1, 0, 1, 2, 32767]
    cnxn.execute("insert into t1 values (1, $1)", value)
    result = cnxn.fetchval("select v from t1")
    assert result == value


def test_array_int4(cnxn):
    # Test with a 4-byte value
    cnxn.execute("create table t1(id int, v int[])")
    value = [None, -2147483648, -32768, -2, -1, 0, 1, 2, 32767, 2147483647]
    cnxn.execute("insert into t1 values (1, $1)", value)
    result = cnxn.fetchval("select v from t1")
    assert result == value


def test_array_int8(cnxn):
    # MAX_INTEGER = 2147483647
    cnxn.execute("create table t1(id int, v bigint[])")
    value = [None, -9223372036854775808, -2147483648, -32768, -2, -1, 0,
             1, 2, 32767, 2147483647, 9223372036854775807]
    cnxn.execute("insert into t1 values (1, $1)", value)
    result = cnxn.fetchval("select v from t1")
    assert result == value


def test_array_text(cnxn):
    cnxn.execute("create table t1(id int, v text[])")
    value = ['one', None, 'two']
    cnxn.execute("insert into t1 values (1, $1)", value)
    result = cnxn.fetchval("select v from t1")
    assert result == value


def test_array_empty(cnxn):
    cnxn.execute("create table t1(id int, v text[])")
    cnxn.execute("insert into t1(id, v) values (1, array[]::text[])")
    result = cnxn.fetchval("select v from t1")
    assert result == []


def test_array_int_in(cnxn):
    cnxn.execute("create table t1(id int)")
    for value in [1, 2, 3]:
        cnxn.execute("insert into t1 values ($1)", value)
    value = [1, 3]
    rset = cnxn.execute("select id from t1 where id = ANY($1)", value)
    assert len(rset) == 2


def test_array_int8_in(cnxn):
    MAX_INTEGER = 2147483647
    cnxn.execute("create table t1(id bigint)")
    for value in [1, MAX_INTEGER * 2, sys.maxsize]:
        cnxn.execute("insert into t1 values ($1)", value)
    value = [1, sys.maxsize]
    rset = cnxn.execute("select id from t1 where id = ANY($1)", value)
    assert len(rset) == 2


def test_array_text_in(cnxn):
    cnxn.execute("create table t1(id int, v text)")
    for value in ['one', 'two', 'three']:
        cnxn.execute("insert into t1 values (1, $1)", value)
    value = ['one', 'three']
    rset = cnxn.execute("select v from t1 where v = ANY($1)", value)
    assert len(rset) == 2


# I don't have a good solution for this yet.  If an array is empty or all NULLs, we don't
# know what type to choose when sending to the DB.  I've chosen text, but it doesn't
# convert as wells as I'd hoped - the backend won't accept it.  I've tried ANYARRAYOID and
# that doesn't work either.

# def test_array_none(cnxn):
#     # I've made the data type 'int[]' since we're going to try inserting as text[].  All we
#     # have is "None", so we don't know what type and will default to text.
#     cnxn.execute("create table t1(id int, v int[])")
#     value = [None, None, None]
#     cnxn.execute("insert into t1 values (1, $1)", value)
#     result = cnxn.fetchval("select v from t1")
#     assert result == value

# This looks weird, but each type must be tested like this.  Code in each type ensures the
# types are the same.  Perhaps we should fix that, but I didn't want to go through the loop
# so many times.


def test_array_int_bad(cnxn):
    cnxn.execute("create table t1(id int, v int[])")
    value = [1, 'two']
    with pytest.raises(pglib.Error):
        cnxn.execute("insert into t1 values (1, $1)", value)


#
# Miscellaneous
#


def test_scope_close(cnxn):
    "Connection should close when it goes out of scope"

    # Each connection is allocated a process on the server to handle queries.  Each process has
    # a unique PID that we can get from the connection.  When a connection is closed, the PID
    # is no longer active.
    #
    # We can see what PIDs are active from the (virtual?) pg_stat_activity table, which
    # helpfully includes a PID column.  When a connection is open, the PID is in the table.
    # When it is closed, it is no longer in the table.  (I don't know how much time we have
    # before they get reused.)

    def _t():
        other = pglib.connect(CONNINFO)
        pid = other.pid
        val = other.fetchval("select pid from pg_stat_activity where pid=$1", pid)
        assert val is not None
        return pid

    pid = _t()
    val = cnxn.fetchval("select pid from pg_stat_activity where pid=$1", pid)
    assert val is None


def test_insert_result(cnxn):
    """
    Ensure that an insert returns the row count, not a result set.
    """
    cnxn.execute("create table t1(a varchar(20), b int)")
    result = cnxn.execute("insert into t1 values ('one', 1)")
    assert result == 1


def test_repr(cnxn):
    """
    For debugging purposes, printing a row should produce the same output as a tuple.
    """
    cnxn.execute("create table t1(a varchar(20), b int)")
    cnxn.execute("insert into t1 values ('one', 1)")
    row = cnxn.row("select a,b from t1")
    t = ('one', 1)
    assert str(row) == str(t)


def test_cnxn_status(cnxn):
    # I don't know how to make a bad status, so we'll just ensure the attribute exists
    # and is true.
    assert cnxn.status


def test_txn_status(cnxn):
    assert cnxn.transaction_status == pglib.PQTRANS_IDLE
    cnxn.execute("begin")
    assert cnxn.transaction_status == pglib.PQTRANS_INTRANS
    try:
        cnxn.execute("drop table bogus")
    except:
        pass
    assert cnxn.transaction_status == pglib.PQTRANS_INERROR

    cnxn.execute("rollback")
    assert cnxn.transaction_status == pglib.PQTRANS_IDLE


def test_uuid(cnxn):
    import uuid
    value = uuid.UUID('4bfe4344-e7f2-41c3-ab88-1aecd79abd12')
    cnxn.execute("create table t1(a uuid)")
    cnxn.execute("insert into t1 values ($1)", value)
    result = cnxn.fetchval("select a from t1")
    assert result == value


def test_rset_columns(cnxn):
    cnxn.execute("create table t1(a int, b int, c int)")
    cnxn.execute("insert into t1 values (1,1,1)")
    rset = cnxn.execute("select a,b,c from t1")
    assert rset.columns == ('a', 'b', 'c')


def test_row_columns(cnxn):
    cnxn.execute("create table t1(a int, b int, c int)")
    cnxn.execute("insert into t1 values (1,1,1)")
    row = cnxn.row("select a,b,c from t1")
    assert row.columns == ('a', 'b', 'c')


def test_assignment(cnxn):
    """
    Ensure columns can be assigned to rows.
    """
    cnxn.execute("create table t1(a int)")
    cnxn.execute("insert into t1 values (1)")
    row = cnxn.row("select a from t1")
    assert row.a == 1
    row.a = 2
    assert row.a == 2


def test_row_failure(cnxn):
    """
    Calling cnxn.row() with invalid SQL used to return "SQL wasn't a
    query" because row was not detecting the error before trying to access
    results.
    """
    cnxn.execute("create table t1(a varchar(20))")
    try:
        cnxn.row("select bogus from t1")
    except pglib.Error as ex:
        msg = str(ex)
        assert '[42703]' in msg


def test_fetchval_failure(cnxn):
    """
    Calling cnxn.fetchval() with invalid SQL used to return "SQL wasn't a
    query" because row was not detecting the error before trying to access
    results.
    """
    cnxn.execute("create table t1(a varchar(20))")
    try:
        cnxn.fetchval("select bogus from t1")
    except pglib.Error as ex:
        msg = str(ex)
        assert '[42703]' in msg, "msg={!r}".format(msg)


def test_null_param(cnxn):
    # At one point, inserting a NULL parameter followed by a non-NULL parameter caused a segfault.
    #
    # A single parameter or two Nones did not crash.

    cnxn.execute("create table t1(a varchar(20), b integer)")
    cnxn.execute("insert into t1(a) values ($1)", 'testing')
    cnxn.execute("update t1 set a=$1, b=$2", None, 1)


def test_txn_commit(cnxn):
    cnxn.execute("create table t1(a int)")
    other = pglib.connect(CONNINFO)
    other.begin()
    other.execute("insert into t1 values (1)")
    other.commit()
    count = cnxn.fetchval("select count(*) from t1")
    assert count == 1


def test_txn_failure(cnxn):
    cnxn.execute("create table t1(a int)")
    other = pglib.connect(CONNINFO)
    other.begin()
    other.execute("insert into t1 values (1)")
    other = None  # should roll back
    count = cnxn.fetchval("select count(*) from t1")
    assert count == 0


def test_txn_rollback(cnxn):
    cnxn.execute("create table t1(a int)")
    other = pglib.connect(CONNINFO)
    other.begin()
    other.execute("insert into t1 values (1)")
    other.rollback()
    count = cnxn.fetchval("select count(*) from t1")
    assert count == 0


def test_txn_rollback_failure(cnxn):
    "Ensure rollback doesn't fail if the txn status is INERROR"
    try:
        cnxn.begin()
        cnxn.execute("select x from bogus")  # table does not exists
    except:
        cnxn.rollback()


def test_txn_empty_commit(cnxn):
    "Ensure commit doesn't fail if the txn status is IDLE"
    cnxn.begin()
    cnxn.commit()


def test_tmp(cnxn):
    """
    A sync version of test_async.  We're getting the results in text format
    instead of binary even though I've requested binary.
    """
    cnxn.execute("create table t1(a varchar(20), b int)")
    cnxn.execute("insert into t1 values ($1, $2)", 'abc', 3)
    rset = cnxn.execute("select a, b from t1")
    for row in rset:
        assert row.a == 'abc'
        assert row[0] == 'abc'
        assert row.b == 3
        assert row[1] == 3


def test_notifies(cnxn):
    "Ensure synchronous notifies() works."

    # We want to test two cases: (1) a notification exists before the call and (2) a
    # notification exists after we're in the select loop.
    #
    # The first is easy.  The second requires we start a thread but have it sleep a bit to
    # give us time to get into the select loop.  I've chosen to sleep for 0.1 seconds.
    #
    # Remember that ther server can de-duplicate notifications.  I don't think it matters
    # here since we're using separate connections for the notifications, but I'll use
    # different channels anyway.

    def notify(conninfo):
        import time
        time.sleep(0.1)
        other = pglib.connect(conninfo)
        other.execute("notify test2, 'testing'")

    cnxn.execute("listen test1")
    cnxn.execute("listen test2")

    cnxn.notify('test1', 'testing')
    n = cnxn.notifies(timeout=1)
    assert n == ('test1', 'testing')

    threading.Thread(target=notify, args=(CONNINFO,)).start()
    n = cnxn.notifies(timeout=1)
    assert n == ('test2', 'testing')
