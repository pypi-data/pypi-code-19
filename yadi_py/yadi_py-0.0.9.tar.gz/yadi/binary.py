import sys

DST_MAP = {
    'linux': 'yadi',
    'windows': 'yadi.exe',
    'darwin': 'yadi'
}

URI_MAP = {
    'linux': 'https://yadi.yandex-team.ru/api/v1/releases/linux/{revision}?hack=/yadi',
    'windows': 'https://yadi.yandex-team.ru/api/v1/releases/windows/{revision}?hack=/yadi.exe',
    'darwin': 'https://yadi.yandex-team.ru/api/v1/releases/darwin/{revision}?hack=/yadi'
}

def dest():
    return DST_MAP[platform()]

def uri(revision):
    return URI_MAP[platform()].format(revision=revision)

def platform():
    if sys.platform == 'linux' or sys.platform == 'linux2':
        return 'linux'
    elif sys.platform == 'darwin':
        return 'darwin'
    elif sys.platform == 'win32':
        return 'windows'
    else:
        raise Exception('Failed to determine system platform: %s' % platform)
