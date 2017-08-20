import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    BASE_DIR = BASE_DIR
    MONGO_SERVER = os.getenv('MONGO_SERVER', 'localhost')
    MONGO_PORT = os.getenv('MONGO_PORT', 27017)
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'tss')
    DYNAMO_DB_AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    DYNAMO_DB_AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    DYNAMO_DB_REGION_NAME = os.getenv('DYNAMO_REGION_NAME', 'eu-west-2')
    DYNAMO_DB_ENDPOINT_URL = os.getenv('DYNAMO_ENDPOINT_URL', 'https://dynamodb.eu-west-2.amazonaws.com')
