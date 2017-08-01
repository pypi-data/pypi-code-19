VERSION = (1, 3, 3, 2)


def get_version(tail=''):
    return ".".join(map(str, VERSION)) + tail
