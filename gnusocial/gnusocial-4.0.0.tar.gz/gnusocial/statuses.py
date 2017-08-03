import sys

import requests

from .utils import _resource_url, make_get_json, make_post_json


def add_id(resource_path, item_id):
    return '{}/{}.json'.format(resource_path, item_id)


def favorites_path(path):
    return 'favorites/{}'.format(path)


def statuses_path(path):
    return 'statuses/{}'.format(path)


def make_get_status(name, resource_path):
    def func(server_url, status_id, *args, **kwargs):
        url = _resource_url(server_url, add_id(resource_path, status_id))
        return requests.get(url, *args, **kwargs).json()
    func.__name__ = name
    return func


def make_post_status(name, resource_path):
    def func(server_url, status_id, *args, **kwargs):
        url = _resource_url(server_url, add_id(resource_path, status_id))
        return requests.post(url, *args, **kwargs).json()
    func.__name__ = name
    return func


favorites = make_get_json('favorites', 'favorites.json')
update = make_post_json('update', statuses_path('update.json'))
show = make_get_status('show', statuses_path('show'))


for name, path in (
        ('destroy', 'destroy'),
        ('repeat', 'retweet')
):
    setattr(sys.modules[__name__], name, make_post_status(name, statuses_path(path)))


for name, path in (
        ('unfavorite', 'destroy'),
        ('favorite', 'create')
):
    setattr(sys.modules[__name__], name, make_post_status(name, favorites_path(path)))


def conversation(server_url, conversation_id, *args, **kwargs):
    url = add_id(_resource_url(server_url, 'statusnet/conversation'), conversation_id)
    return requests.get(url, *args, **kwargs).json()
