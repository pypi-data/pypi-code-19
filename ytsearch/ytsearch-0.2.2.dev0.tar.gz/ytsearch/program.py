#!/usr/bin/env python
# -*- coding: utf-8 -*-


import argparse
import os
import time
import json
import subprocess

import urwid
import yaml
import requests

from ytsearch import youtube, ui, settings


CONF_DIR = settings.CONF_DIR
CACHE_LOCATION = settings.CACHE_LOCATION


def mkdir_recursive(directory):
    """Iterates through the directories and makes them if they don't exist.
    The same as mkdir -p
    
    :directory: The fullpath to make.
    :returns: None

    """
    split = directory.split('/')
    for index, item in enumerate(split):
        path = '/'.join(split[:index])
        if path == '':
            continue
        if not os.path.exists(path):
            os.mkdir(path)
    return None


def command_cache(_, *params):
    '''Show the cache UI'''
    with ui.Interface() as interface:
        interface.main('cache')
    return None


def command_search(_, *params):
    '''Load videos from a search result.'''
    if len(params) == 0:
        print('You must specify a search term.')
        return None
    video_name = ' '.join(params)
    results = youtube.search(video_name)
    with ui.Interface() as interface:
        widget = ui.search_results.Interface(interface)
        widget.description = video_name
        widget.results = results
        interface.saved_pages['search'] = widget
        interface.current_page = widget
        interface.main('search', widget.load_page())
    return None


def command_import(_, url, *params):
    print('Retrieving playlist')
    videos, info = youtube.get_playlist(url)
    playlist_name = info['snippet']['title']
    channel_name = info['snippet']['channelTitle']
    title = '{} - {}'.format(channel_name, playlist_name)
    playlist = {title: []}
    print('Parsing videos from {}'.format(title))
    for video in videos:
        data = {'name': video['snippet']['title'], 
                'location': video['contentDetails']['videoId'],
                'resource': 'youtube', 'cache': None}
        playlist[title].append(data)
    playlist_file = '{}/playlists.json'.format(CONF_DIR)
    if os.path.exists(playlist_file):
        with open(playlist_file, 'r') as f:
            playlists = json.loads(f.read())
    else:
        playlists = {}
    playlists.update(playlist)
    with open(playlist_file, 'w') as f:
        f.write(json.dumps(playlists))
    print('Saved playlist {}'.format(title))
    return None


def check_default_files():
    if not os.path.exists(CACHE_LOCATION):
        mkdir_recursive(CACHE_LOCATION)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', help='The command to run.', nargs='?')
    parser.add_argument('args', nargs='*',
                        help='The arguments to pass to the command.')
    args = parser.parse_args()
    commands = {c[8:]:globals()[c] for c in globals()
                if c.startswith('command_')}
    command = commands.get(args.command, None)
    if command is None:
        command = command_cache
        arguments = [args.command] + args.args
    else:
        if args.args is None:
            arguments = []
        else:
            arguments = args.args
    command(args, *arguments) 
    return None


if __name__ == "__main__":
    main()
