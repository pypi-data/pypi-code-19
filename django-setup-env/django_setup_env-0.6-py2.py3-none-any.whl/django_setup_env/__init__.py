import os
import sys

import django

DEFAULT_DJANGO_PACKAGE_NAME = 'mysite'


def get_base_path(filename, django_package_name=DEFAULT_DJANGO_PACKAGE_NAME):
    base_path = None
    # Get module path
    path = os.path.realpath(filename)
    # Strip script name
    if os.path.isfile(path):
        path = os.path.dirname(path)
    # Add the absolute path containing the Django package
    path_list = path.split(os.sep)
    if django_package_name in path_list:
        path_list = path_list[:path_list.index(django_package_name)]
        base_path = os.sep.join(path_list)
    else:
        # filename is not in Django package or one of its subdirectories.
        # Now check whether filename's directory (or any of its parent directories) contain the Django package
        for i in xrange(1, len(path_list)):
            trial_directory = os.sep.join(path_list[:i+1])
            if os.path.isdir(os.path.join(trial_directory, django_package_name)):
                base_path = trial_directory
                break

    if base_path is not None:
        return base_path
    else:
        raise ValueError("Failed to configure Django")


def setup_django(filename, django_package_name=DEFAULT_DJANGO_PACKAGE_NAME):
    """
    Utility function that adds the Django package

     * adds the Django project to the path
     * sets the DJANGO_SETTINGS_MODULE environment variable
     * calls django.setup()
     * returns a string of the directory that has been added to the path
    """
    base_path = get_base_path(filename, django_package_name)
    sys.path.append(base_path)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings" % django_package_name)

    try:
        django.setup()
    except AttributeError:
        # django.setup does not exist in Django 1.6
        pass

    return base_path
