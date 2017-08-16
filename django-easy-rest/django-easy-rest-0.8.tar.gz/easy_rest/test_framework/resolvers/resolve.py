from django.conf import settings
import os

base_dir = settings.BASE_DIR


def get_app_path(app_name):
    return os.path.join(base_dir, app_name)


def app_exists(app_name):
    return os.path.exists(get_app_path(app_name))


def get_tests_file(app_name):
    # basic django logic
    if not app_exists(app_name):
        return
    path = os.path.join(app_name, 'tests.py')
    if not os.path.exists(path):
        with open(path, 'w+') as file:
            file.write("")
    return path
