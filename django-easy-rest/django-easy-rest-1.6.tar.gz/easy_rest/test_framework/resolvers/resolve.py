from django.conf import settings
import os


def get_app_path(app_name):
    """
    Returns app path from django apps
    :param app_name: the name of the app to search
    :return: app path
    """
    return os.path.join(settings.BASE_DIR, app_name)


def app_exists(app_name):
    """
    Validates if the app exists
    :param app_name: the app name to validate
    :return: True/False (Boolean)
    """
    return os.path.exists(get_app_path(app_name))


def get_tests_file(app_name, file_name, data=""):
    """
    Returns the app test file if exists else creates a new test
    file and return it path
    :param app_name: the app to search for test file in
    :param file_name: the file name
    :param data: the data of the test file
    :return: path of file (str), data (str)
    """
    # if app not exists
    if not app_exists(app_name):
        return None, None
    # building test file path
    path = os.path.join(get_app_path(app_name), file_name)
    # if test file not exists generating new
    if not os.path.exists(path):
        with open(path, 'w+') as file:
            file.write(data)
    # if test file exists reading the test file data
    else:
        with open(path, 'r') as file:
            data = file.read()
    # returns path (str), data (str)
    return path, data


def register_unitest():
    """
    Register django env to know it's under a test
    :return: None
    """
    os.environ['under_test'] = "True"


def in_test():
    """
    Check if django is under a test
    :return: True/False (boolean)
    """
    return bool(os.environ.get('under_test'))
