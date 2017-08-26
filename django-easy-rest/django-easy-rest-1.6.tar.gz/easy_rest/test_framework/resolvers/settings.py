from django.conf import settings as django_settings


def get_override_settings(attributes=None):
    """
    Overrides settings by attribute keys
    :param attributes: attribute = keys of dictionary
    :return: built override settings
    """
    # runtime parameters should be const
    if not attributes:
        attributes = []

    # trying to get real settings
    if not django_settings._wrapped:
        # if not real settings calling settings setup
        django_settings._setup()

    # getting real settings
    settings = django_settings._wrapped

    # building settings
    return build_str({key: val for key, val in settings.__dict__.items() if key in attributes})


def build_str(dictionary_to_build_from):
    """
    Building override string
    :param dictionary_to_build_from:  what to build from
    :return: built string
    """
    # the sting it built
    built = ''
    # iterating over dictionary
    for key, val in dictionary_to_build_from.items():
        # building current setting
        built += "{key}={val},".format(key=key, val=val)
    # returning built -1 cause of , at end
    return built[:-1]
