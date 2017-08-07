import math
import random
import sys

from . import client


def distance_from(preferred_size):
    def distance(size):
        return math.sqrt(
            sum([
                (x - y) ** 2
                for x, y in zip(_size_tuple(preferred_size), _size_tuple(size))
            ])
        )
    return distance


def _size_tuple(string):
    x, y = string.split('x')
    return int(x), int(y)


def best_size(wallpaper_url, preferred_size):
    sizes = client.get_wallpaper_size(wallpaper_url)
    ordered_sizes = sorted(sizes, key=distance_from(preferred_size))
    return sizes[ordered_sizes[0]]


def select_random_wallpaper(size=None):
    size = size or '{0}x{0}'.format(sys.maxsize)
    wallpaper = random.choice(client.get_wallpapers())
    return best_size(wallpaper, size)
