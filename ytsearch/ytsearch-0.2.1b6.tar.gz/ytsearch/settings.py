#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import collections

import yaml


CONF_DIR = os.path.expanduser('~/.ytsearch')


DEFAULT = '''
keybindings:
    global:
        '1': 'PAGE search'
        '2': 'PAGE cache'
        '3': 'PAGE queue'
        '4': 'PAGE playlist'
        '0': 'FOCUS_PLAYER'
        'j': 'MOVE +1'
        'k': 'MOVE -1'
        '/': 'SEARCH'
        'a': 'PLAY_AUDIO'
        'v': 'PLAY_VIDEO'
        'ZZ': 'QUIT'
        'qa': 'QUEUE_AUDIO'
        'qv': 'QUEUE_VIDEO'
        '+': 'CREATE_PLAYLIST'
        'p': 'PLAYLIST_ADD'
        'c': 'TOGGLE_CONSUME'
        'r': 'TOGGLE_REPEAT'
        'f': 'FIND_VIDEO'
        'd': 'DOWNLOAD_VIDEO'
        'n': 'NEXT_VIDEO'
        'R': 'TOGGLE_RANDOM'
        'tp': 'SEND_KEY p'
        '=': 'SEND_KEY 0'
        '-': 'SEND_KEY 9'
        'ctrl d': 'MOVE +10'
        'ctrl u': 'MOVE -10'
        'gg': 'MOVE top'
        'G': 'MOVE bottom'
    playlist:
        'P': 'TOGGLE_PLAYLIST_ADD'
        'enter': 'PLAY_AUDIO'
    playlist_items:
        'delete': 'REMOVE_PLAYLIST_ITEM'
    player:
        '1': 'FOCUS_NORMAL'

player:
    command: 'mpv'
    video_args: ['--player-operation-mode=pseudo-gui']
    audio_args: ['--no-video', '--volume', '50']
    size: 5
    quit_key: 'q'

cache: '~/videos/youtube_cache'
'''


def find_keybinding(event_name):
    '''Find the key corresponding with an event name.
    
    :event_name: str: The event name to find.
    :return: str: The key that was found.
             None if none was found.
    '''
    user_settings = load_user_settings()
    keybind = find_event_name(event_name, user_settings)
    if keybind is not None:
        return keybind
    default_settings = yaml.load(DEFAULT)
    keybind = find_event_name(event_name, default_settings)
    return keybind


def find_event_name(event_name, default_settings, level=None):
    '''Recursively find the event name,
    
    :event_name: str: the event name to find.
    :default_settings: dict: The settings to start on the first recursion.
    :level: dict: The level of iteration its on.
    :return: str: THe key that was found.
             None if none was found.
    '''
    if level is None:
        level = default_settings
    for key, name in level.items():
        if isinstance(name, collections.Mapping):
            output = find_event_name(event_name, default_settings, name)
            if output is not None:
                return output
        if name == event_name:
            return key
    return None


def load_settings():
    '''Loads the settings from disk.
    
    :return: dict: A dictionary of merged settings.
    '''
    user_settings = load_user_settings()
    default_settings = yaml.load(DEFAULT)
    merged = merge_settings(default_settings, user_settings)
    return merged


def merge_settings(default, user):
    '''Merge 2 dictionaries recursively.
    
    :default: dict: The base dictionary to add items to.
    :user: dict: The dictionary to add items from, if they exist.
    :return: dict: The merged contents.
    '''
    for key, value in user.items():
        if (key in default and isinstance(default[key], dict)
        and isinstance(value, collections.Mapping)):
            merge_settings(default[key], value)
        else:
            default[key] = value
    return default


def load_user_settings():
    '''Loads the settings.yaml file.
    
    :return: dict: The settings that were loaded.
    '''
    if not os.path.exists('{}/settings.yaml'.format(CONF_DIR)):
        return {}

    with open('{}/settings.yaml'.format(CONF_DIR)) as f:
        data = f.read() 
    settings = yaml.load(data)
    if settings is None:
        return {}
    return settings


def create_settings():
    '''Creates the settings file so there is something to load.
    
    :return: None
    '''
    with open('{}/settings.yaml'.format(CONF_DIR), 'w') as f:
        f.write(DEFAULT)
    return None


# TODO make this load only once. Right now this executes with each import.
if not os.path.exists(CONF_DIR):
    os.mkdir(CONF_DIR)

cache = load_settings().get('cache', '~/videos/youtube_cache')
if not cache.endswith('/'):
    cache += '/'

CACHE_LOCATION = os.path.expanduser(cache)
