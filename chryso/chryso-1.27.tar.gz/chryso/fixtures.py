import logging

import pytest

import chryso.connection

LOGGER = logging.getLogger(__name__)

def pytest_addoption(parser):
    parser.addoption(
        '--chryso-debug',
        default=False,
        action='store_true',
        help="Debug chryso's database interactions by echoing everything"
    )

@pytest.yield_fixture(scope="session")
def db_connection(db_connection_uri, pytestconfig, tables): # pylint: disable=redefined-outer-name
    """
    A connection to the database. This fixture requires that you supply a db_connection_uri fixture and tables fixture
    that provide the information for how to connect to the test database and the tables defined in the database respectively.
    It's recommended you not use this fixture directly, but instead use db. If you need to test something outside a transaction
    us db_raw which will correctly clean up after it is used, though it is expensive
    """
    engine = chryso.connection.Engine(
        db_connection_uri,
        tables,
        echo=pytestconfig.option.chryso_debug,
        track_queries=True,
    )
    engine.drop_all()
    LOGGER.info("Setting up database")
    engine.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')
    engine.create_all()
    yield engine

@pytest.yield_fixture
def db(db_connection): # pylint: disable=redefined-outer-name
    """
    A session in the database.
    This will do all work for a test in a transaction and roll it back at the end.
    This is the fixture you want to use
    """
    LOGGER.info("Setting up database transaction")
    with db_connection.atomic() as session:
        previous = chryso.connection.get()
        chryso.connection.store(db_connection)
        yield db_connection
        LOGGER.info("Rolling back database transaction")
        session.rollback()
        chryso.connection.store(previous)

@pytest.yield_fixture
def db_raw(db_connection): # pylint: disable=redefined-outer-name
    """
    A connection to the database outside of a transaction.
    It will clean up after itself but it is expensive to do so
    """
    previous = chryso.connection.get()
    chryso.connection.store(db_connection)
    db_connection.reset_queries()
    yield db_connection
    db_connection.reset()
    chryso.connection.store(previous)
