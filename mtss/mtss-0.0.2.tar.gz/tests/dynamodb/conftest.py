import pytest

from tss.config import Config

import tss.utils_aws as utils
from tss.models_aws import SERIES_SCHEMA, DATA_SCHEMA


@pytest.fixture(scope="session", autouse=True)
def db():
    config = Config
    config.DYNAMO_DB_AWS_ACCESS_KEY_ID = ''
    config.DYNAMO_DB_AWS_SECRET_ACCESS_KEY = ''
    config.DYNAMO_DB_REGION_NAME = ''
    config.DYNAMO_DB_ENDPOINT_URL = 'http://localhost:8000'
    return utils.get_dynamodb(config)


@pytest.fixture
def series(db):
    return db.Table(SERIES_SCHEMA['TableName'])


@pytest.fixture
def data(db):
    return db.Table(DATA_SCHEMA['TableName'])


@pytest.fixture(scope="session", autouse=True)
def create_table(db):
    utils.create_table(db)
