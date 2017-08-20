import os

import pytest

from tss.utils import get_mongo_db, _clear_all


class IntegrationConfig:
    MONGO_SERVER = os.getenv('MONGO_SERVER', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', 27017)
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'tss-test')
    
    
@pytest.fixture
def db():
    return get_mongo_db(IntegrationConfig)


@pytest.fixture
def series(db):
    return db.series


@pytest.fixture
def data(db):
    return db.data


@pytest.yield_fixture(autouse=True)
def run(db):
    _clear_all(db)
    yield
    _clear_all(db)