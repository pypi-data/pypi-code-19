try:
    import ConfigParser as configparser
except:
    import configparser
import os

"""
.. module:: config_helper
   :platform: Unix
   :synopsis: Add configuration capabilities to a method

.. moduleauthor:: Marco Albero Albero <marco@mybi.es>
"""

def read_env(config_file=None):
    try:
        init = config_file
        config = configparser.ConfigParser()
        config.read(init)
    except:
        raise Exception("Error reading configuration")
    return config


def show_env():
    for section in sections:
        print("["+ section + "]")
        env = dict(config.items(section))
        for key in env:
            print("\t" + key + ": " + env[key])


def get_config(config_file):
    """Decorator/Wrapper for injecting the configuration object as a parameter
    of the decorated method.

    Args:
       config_file (str):  The path to the configuration file to read from.

    Returns:
       object. The decorated function

    Raises:
       Custom Exception

    Usage:
    ::
        import py_code_helpers.config_helper.helper as helper

        class TheClass:
            @helper.get_config('path/to/config/config.ini')
            def __init__(self, configuration):
                self.config = configuration

            # and use it like:
            self.config.get('section', 'param_name')
    """
    def decorate(function):
        def wrapper(*args, **kwargs):
            cfg = read_env(config_file)
            function(configuration=cfg, *args, **kwargs)
        return wrapper
    return decorate
