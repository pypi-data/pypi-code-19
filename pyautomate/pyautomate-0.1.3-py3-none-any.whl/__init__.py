# coding: utf-8
import os
import shutil
import subprocess
from datetime import datetime


class PathExistsWarning(UserWarning):
    def __init__(self, path, extra_msg=None):
        super().__init__(self)
        self.path = path
        self.extra_msg = extra_msg

    def __str__(self):
        msg = '{} exists.'.format(self.path)
        if self.extra_msg:
            msg = '{} {}'.format(msg, self.extra_msg)
        return msg


def get_timestamp(date_time=None, include_time=False):
    if not date_time:
        date_time = datetime.now()

    if include_time:
        format_str = '%Y-%m-%dT%H%M'
    else:
        format_str = '%Y-%m-%d'
    return date_time.strftime(format_str)


def prompt_user(message):
    prompt = input('{} (y/n) '.format(message))
    return True if prompt.lower().startswith('y') else False


def print_file(path, nlines=5, encoding='utf-8'):
    with open(path, encoding=encoding) as file:
        for line in file:
            print(line.rstrip())
