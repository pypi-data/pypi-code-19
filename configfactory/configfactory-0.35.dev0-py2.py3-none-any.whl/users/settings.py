from configfactory.utils import settings_val

DEFAULT_USERS = settings_val('DEFAULT_USERS', [
    {
        'username': 'admin',
        'password': 'admin'
    }
])
