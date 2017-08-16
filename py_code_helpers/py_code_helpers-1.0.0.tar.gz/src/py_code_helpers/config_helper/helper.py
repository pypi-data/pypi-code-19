try:
    import ConfigParser as configparser
except:
    import configparser
import os


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
    def decorate(function):
        def wrapper(*args, **kwargs):
            configuration = read_env(config_file)
            function(configuration, *args, **kwargs)
        return wrapper
    return decorate
