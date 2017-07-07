SECRET_KEY = 'fake-key'
INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    "tests",
    "accounts",
]
AUTH_USER_MODEL = 'accounts.User'
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
}
