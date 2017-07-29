# coding: utf-8
from .base import *

FIXTURE_DIRS = [os.path.join(BASE_DIR, 'tests/djotali/fixtures/'), ]
DATABASES = {
    'default': dj_database_url.config(default='sqlite:///test.sqlite3', conn_max_age=600)
}
