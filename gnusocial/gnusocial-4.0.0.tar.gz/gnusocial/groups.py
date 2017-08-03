import sys

import requests

from .utils import make_get_json, make_post_json, _resource_url


def _resource_path(resource_path, group):
    return '{}/{}.json'.format(resource_path, group)


def make_path(path):
    return 'statusnet/groups/{}'.format(path)


create = make_post_json('create', make_path('create.json'))

for name, path in (
        ('local_groups', 'list_all.json'),
        ('user_groups', 'list.json'),
):
    setattr(sys.modules[__name__], name, make_get_json(name, make_path(path)))


def make_get_group(name, resource_path):
    def func(server_url, group, *args, **kwargs):
        url = _resource_url(server_url, _resource_path(resource_path, group))
        return requests.get(url, *args, **kwargs).json()
    func.__name__ = name
    return func


def make_post_group(name, resource_path):
    def func(server_url, group, *args, **kwargs):
        url = _resource_url(server_url, _resource_path(resource_path, group))
        return requests.post(url, *args, **kwargs).json()
    func.__name__ = name
    return func


for name, path in (
        ('timeline', 'timeline'),
        ('show', 'show'),
        ('is_member', 'is_member'),
        ('admins', 'admins'),
        ('members', 'membership')
):
    setattr(sys.modules[__name__], name, make_get_group(name, make_path(path)))


for name in ('leave', 'join'):
    setattr(sys.modules[__name__], name, make_post_group(name, make_path(name)))
