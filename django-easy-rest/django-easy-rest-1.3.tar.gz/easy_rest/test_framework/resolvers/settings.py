from django.conf import settings


def get_override_settings(attributes=[]):
    # should be more complex but for now
    return build_str({key: val for key, val in settings.__dict__.items() if key in attributes})


def build_str(dict):
    str = ''
    for key, val in dict.items():
        str += "{key}={val},".format(key=key, val=val)
    str = str[:-1]
    return str
