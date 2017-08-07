import argparse
import logging
import logging.config
import os.path
import subprocess

import requests

from . import shuffle

CACHE_DIR = os.path.expanduser('~/.cache/desktopography')  # TODO(fbochu) XDG and config
GSETTINGS = {
    'cinnamon': 'org.cinnamon.desktop.background',
    'gnome': 'org.gnome.desktop.background',
}


def set_logger():
    logging.config.dictConfig({
        'version': 1,
        'formatters': {
            'simple': {
                'format': '%(asctime)s - %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
            },
        },
        'loggers': {
            'desktopography': {
                'level': 'INFO',
                'handlers': ['console'],
            },
        },
    })


def store(wallpaper_url):
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

    filename = wallpaper_url.rsplit('/')[-1]
    file_path = os.path.join(CACHE_DIR, filename)
    with open(file_path, 'wb') as fp:
        fp.write(requests.get(wallpaper_url).content)

    return file_path


def gsettings(desktop, size):
    wallpaper_url = shuffle.select_random_wallpaper(size)
    wallpaper_path = store(wallpaper_url)
    subprocess.call([
        'gsettings', 'set',
        GSETTINGS[desktop], 'picture-uri',
        'file://{}'.format(wallpaper_path),
    ])
    return wallpaper_path


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')
    subparser = subparsers.add_parser('shuffle')
    subparser.add_argument('size', nargs='?')
    subparser = subparsers.add_parser('gsettings')
    subparser.add_argument('desktop', nargs='?')
    subparser.add_argument('size', nargs='?')

    args = vars(parser.parse_args())
    set_logger()

    command = args.pop('command')
    commands = {
        None: parser.usage,
        'shuffle': shuffle.select_random_wallpaper,
        'gsettings': gsettings,
    }

    print(commands[command](**args))

if __name__ == '__main__':
    main()
