#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import json
import shlex
import subprocess
import random
import time

import urwid
import pafy
from fuzzywuzzy import fuzz, process
import youtube_dl

from ytsearch.ui import (search_results, cache_items, queue_items,
                         playlist, playlist_items)
from ytsearch import settings, threads, youtube


CACHE_LOCATION = settings.CACHE_LOCATION
CONF_DIR = os.path.expanduser('~/.ytsearch')


COLOURS = [
    ('title', 'bold', ''),
    ('standout', 'standout', ''),
    ('underline', 'underline', ''),
    ('blue', 'dark blue', ''),
    ('blue_bold', 'dark blue, bold', ''),
    ('green', 'dark green', ''),
    ('green_bold', 'dark green, bold', '')
]


SETTINGS = settings.load_settings()
KEYBINDS = SETTINGS['keybindings']
PLAYER = SETTINGS['player']
HOOKS = SETTINGS.get('hooks', {})


class Hook:
    
    """
    A decorator that calls HOOK functions when the decorated function
    is run
    """

    def __init__(self, hook_name):
        """
        Create the hook

        :hook_name: str: The name of the hook to run.
        """
        self.hook_name = hook_name

    def __call__(self, function):
        """
        Runs when the decorator is created.

        :function: func: The function that activates the hook.
        :return: func: The function that runs the hook / function.
        """
        def run(*args, **kwargs):
            """
            Handles the funning of both the function and hook.

            :*args: list: A list of arguments to pass to the function.
            :**kwargs: dict: A dictionary of keyword args to pass.
            :return: ?: The output from the function.
            """
            run_hook, output = function(*args, **kwargs)
            if self.hook_name in HOOKS and run_hook:
                command_line = HOOKS[self.hook_name].format(*args, **kwargs,
                               output=output)
                command = shlex.split(command_line)
                subprocess.run(command)
            return output
        return run 


class VoidLogger:
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


class EditWidget(urwid.Edit):
    """The widget that lets the user input something."""

    def __init__(self, call, *args, **kwargs):
        self.call = call
        super().__init__(*args, **kwargs)

    def keypress(self, size, key):
        if key == 'enter':
            self.call(self.text)
        else:
            return super().keypress(size, key)


class TerminalWidget(urwid.Terminal):
    """
    The terminal widget that the user uses to interact with the
    command that is playing the video / audio
    """
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super().__init__(*args, **kwargs)

    def keypress(self, size, key):
        found = self.parent.unhandled_input(key, 'player')
        if not found:
            return super().keypress(size, key)
        return None


class Video:
    """
    A class to store information for each video.
    """

    selected = False
    widget = None
    terminal = None
    temporary = False
    downloading = False
    _status = ''

    def __init__(self, name, location, resource='file', cache=None):
        """
        Create a new video.
        
        :name: str: The name of the video.
        :location: str: The location of the video resource.
        :resource: str: The type of resource.
        :cache: str: A location of the cache, if any. None otherwise.
        """
        self.name = name
        self.location = location
        self._resource = resource
        self.cache = cache

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, text):
        self._status = text
        return None

    def stop(self):
        """
        Stop the video from playing by sending 'quit_key' to the process.

        :return: None
        """
        if self.terminal is None:
            return None
        kill_key = PLAYER['quit_key']
        self.terminal.respond(kill_key)
        return None
    
    def resource(self, audio=True):
        """
        Load the resource of the video.
        
        :audio: bool: True: If it should load the video as audio only.
                      False: if it should load the video too.
        :return: str: The location of the resource.
                 None: It returns None if the resource couldn't be found
        """
        if self.cache is not None:
            return self.cache
        if self._resource == 'preloaded' or self._resource == 'file':
            return self.location
        if self._resource == 'youtube':
            url = 'https://youtube.com/watch?v={}'.format(self.location)
            video = pafy.new(url)
            resource = video.getbestaudio if audio else video.getbest
            return resource().url
        return None

    @threads.AsThread()
    def preload(self, audio=True):
        """
        Preload the video resource. Used when you add a video to the queue
        
        :audio: bool: True: If the video should be loaded as audio.
                      False: If it should be audio and video.
        :return: None
        """
        resource = self.resource(audio)
        self._resource = 'preloaded'
        self.location = resource
        return None

    def send(self, string):
        """Send a string to the running terminal widget.
        
        :string: str: The string to send to the widget.
        :return: None
        """
        if self.terminal is not None:
            self.terminal.respond(string)
        return None

    def __eq__(self, video):
        """
        Check if a video is equal to another video.
        
        :video: Video: The video to check equality of.
        :return: bool: True: if the videos are the same.
                       False: If they are not the same.
        """
        if video is None:
            return False
        return self.location == video.location or self.name == video.name

    def __gt__(self, video):
        """
        Check if a video is greater than another video.
        This just uses the len() of the name.
        
        :video: Video: The video to compare sizes to.
        :return: bool: True: If the current video is larger than the param.
                       False: if the param is larger than this video."""
        if video is None:
            return False
        return self.name > video.name

    def __len__(self):
        """
        Return the length of the video name.
        
        :return: int: Length of the name.
        """
        return len(self.name)

    def __iter__(self):
        """
        Return the iter on the name of the video.
        
        :return: iterable: Iterable of the video name.
        """
        return iter(self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def __getitem__(self, attr):
        if hasattr(self, attr):
            return getattr(self, attr)
        return self.name[attr]


class ItemList(urwid.ListBox):
    def __init__(self, parent, widgets, mode):
        self.parent = parent
        self.keybuffer = []
        self.mode = mode
        super().__init__(widgets)

    def find_video(self):
        """
        Find and move the cursor to the name of the video the 
        user is inputting.
        """
        # fuzzywuzzy freaks out when certain characters are passed to it.
        # As far as I can find, the warnings it gives off cannot be stopped
        # they ruin the TUI so I strip characters here.
        find = ''.join(self.keybuffer).strip('+=\'!@#$%^&*()_+"')
        if find == '':
            return None
        videos = [x.name for x in self.parent.current_page.results]
        output = process.extractOne(find, videos,
                                    scorer=fuzz.partial_ratio)
        index = videos.index(output[0])
        self.set_focus(index)
        self.parent.set_status(find)
        self.parent.loop.draw_screen()
        return None

    def keypress(self, size, key):
        self.keybuffer.append(key)
        mode_keys = KEYBINDS.get(self.mode, {})
        keys = dict(KEYBINDS.get('global', {}))
        keys.update(mode_keys)
        possible = []
        matches = []

        if key == 'backspace':
            self.keybuffer = self.keybuffer[:-2]

        if key == 'enter' and self.parent.find_video:
            self.parent.find_video = False
            self.parent.set_status('')
            return None

        if self.parent.find_video:
            self.find_video()
            return None

        if len(self.keybuffer) > 10:
            self.keybuffer = self.keybuffer[-10:]

        for key in self.keybuffer[::-1]:
            possible.append(key)
            for index, key in sorted(enumerate(keys), key=lambda a: len(a)):
                if ''.join(possible) == str(key):
                    matches.append(str(key))

        if matches != []:
            key = sorted(matches, key=lambda x: len(x))[-1]
            event = keys[key]
            _, index = self.get_focus()
            self.parent.key_event(event, index)
            self.keybuffer = []
            return None
        return None


class Interface:

    pages = {'cache': cache_items.Interface,
             'search': search_results.Interface,
             'queue': queue_items.Interface,
             'playlist': playlist.Interface,
             'playlist_items': playlist_items.Interface}
    saved_pages = {'cache': None, 'search': None, 'queue': None,
                   'playlist': None, 'playlist_items': None}
    video_storage = []
    queue = []
    current_page = None
    page_placeholder = None
    keybuffer = []
    playing = None
    _playing_position = 0
    terminal = None
    playlists = {}
    playlist_add = None
    state = {'consume': False, 'repeat': True, 'random': False}
    find_video = False

    def __init__(self): 
        self.player_placeholder = urwid.Filler(urwid.Text(''))
        self.input_placeholder = urwid.Filler(urwid.Text(''))
        self.load_playlists()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        if self.playing is not None:
            self.playing.stop()
        self.save_playlists()
        return None

    @property
    def playing_position(self):
        """
        Return the current song index. If you have random on it
        uses a random number based on the length of the queue.
        
        :return: int: The position of the song in the queue.
        """
        if (isinstance(self._playing_position, tuple)
        and self._playing_position[0]):
            return self._playing_position[1]
        if self.state['random']:
            return random.randint(0, len(self.queue)-1)
        return self._playing_position

    @playing_position.setter
    def playing_position(self, new):
        """
        Set the playing position.
        
        :new: int: The new position to use.
              tuple: If this is a tuple, the first argument is if
                     the position should be forced.
        :return: None
        """
        self._playing_position = new
        return None

    def load_playlists(self):
        """
        Load the playlists the user has created. If there are
        any issues loading the playlists will be set to blank.
        """
        if os.path.exists('{}/playlists.json'.format(CONF_DIR)):
            with open('{}/playlists.json'.format(CONF_DIR)) as f:
                data = f.read()
            try:
                self.playlists = json.loads(data)
            except json.decoder.JSONDecodeError:
                self.playlists = {}
        return None

    def save_playlists(self):
        """Save the created playlists."""
        if self.playlists != {}:
            with open('{}/playlists.json'.format(CONF_DIR), 'w') as f:
                f.write(json.dumps(self.playlists))
        return None

    def main(self, start_page, start_widget=None):
        """
        Create all of the widgets and run the UI.
        
        :start_page: str: The name of the page to load by default.
        :start_widget: urwid.Widget: The widget to load by default.
        :return: None
        """
        self.page_placeholder = self.load_page(start_page)
        self.status = urwid.Filler(urwid.Text(''))
        self.state_widget = self.create_state()
        if start_widget is not None:
            self.page_placeholder.original_widget = start_widget
        divider = urwid.Divider(u'-', 1, 1)
        self.widgets = urwid.Pile([
            ('weight', 1, self.page_placeholder),
            (0, self.input_placeholder),
            ('pack', divider),
            (0, self.player_placeholder),
            (1, urwid.Columns([self.status, (5, self.state_widget)]))
            ])
        self.loop = urwid.MainLoop(self.widgets, COLOURS,
                                   unhandled_input=self.unhandled_input)
        self.loop.run()
        return None

    def create_state(self):
        """
        Create the state widget, based off the state dictionary.
        
        :return: urwid.Filler: A filler wrappring the text widget.
        """
        consume_char = settings.find_keybinding('TOGGLE_CONSUME')
        consume = consume_char if self.state['consume'] else '-'
        repeat_char = settings.find_keybinding('TOGGLE_REPEAT')
        repeat = repeat_char if self.state['repeat'] else '-'
        random_char = settings.find_keybinding('TOGGLE_RANDOM')
        random = random_char if self.state['random'] else '-'
        text = '[{}{}{}]'.format(consume, repeat, random)
        return urwid.Filler(urwid.Text(text, 'right'))

    def update_state(self):
        """Update the state widget. This will also re-draw the UI."""
        self.state_widget.original_widget = self.create_state().original_widget
        self.loop.draw_screen()
        return None

    def set_status(self, status):
        """
        Set the text of the status widget at the bottom.
        
        :status: str: The text to set on the status.
        :return: None
        """
        self.status.original_widget.set_text(status)
        self.loop.draw_screen()
        return None

    def create_search_widget(self, text, call):
        """
        Create the search widget for the user to input some text
        
        :text: str: The text to display next to the input.
        :call: func: The function to call when the user hits enter.
        :return: None
        """
        title = urwid.Text(text)
        edit = EditWidget(call)
        column = urwid.Columns([(len(text), title), edit])
        padding = urwid.Padding(column, left=2, right=2)
        filler = urwid.Filler(padding, 'middle')
        attrmap = urwid.AttrMap(filler, 'standout', None)
        self.widgets.contents[1] = (attrmap, ('given', 3))
        self.widgets.focus_position = 1
        self.loop.draw_screen()
        return None

    def destroy_search_widget(self):
        """Destroys the search widget and redraws the UI."""
        widget = urwid.Filler(urwid.Text(''))
        self.widgets.contents[1] = (widget, ('given', 0))
        self.widgets.focus_position = 0
        self.loop.draw_screen()
        return None

    @threads.AsThread()
    def search(self, video_name):
        """
        Search youtube for a videos, it will update the search
        results page if its active or in saved pages.
        
        :video_name: str: The name of the video to search for.
        :return: None
        """
        self.destroy_search_widget()
        results = youtube.search(video_name)
        if results is None:
            return None
        if isinstance(self.current_page, search_results.Interface):
            self.current_page.results = results
            self.current_page.load_page()
            self.load_page('search')
            self.loop.draw_screen()
        elif self.saved_pages['search'] is not None:
            self.saved_pages['search'].results = results
            self.saved_pages['search'].load_page()
        else:
            search_page = self.pages['search'](self)
            search_page.results = results
            search_page.load_page()
            self.saved_pages['search'] = search_page
        return None

    def load_page(self, name, switch_focus=False):
        """
        Load one of the pages. Optionally switch focus to the page
        section of the UI.
        
        :name: str: The name of the page to load.
        :switch_focus: bool: True if the UI focus should be switched
                                   to the page section.
                             False otherwise
        :return: urwid.WidgetPlaceholder: The new page placeholder.
        """
        saved = self.saved_pages.get(name, None)
        if saved is not None:
            page = saved
            widgets = page.widgets
        else:
            page = self.pages[name](self)
            widgets = page.load_page()
            self.saved_pages[name] = page
        self.current_page = page
        if self.page_placeholder is None:
            self.page_placeholder = widgets
        else:
            self.page_placeholder = widgets
            self.widgets.contents[0] = (self.page_placeholder, ('weight', 1))
            if switch_focus:
                self.widgets.focus_position = 0
        self.update_videos()
        return self.page_placeholder

    def update_videos(self):
        """
        Update the videos that have been placed in the video storage.
        Basically these are any videos that have been created.
        """
        for video in self.video_storage:
            if video in self.current_page.results:
                index = self.current_page.results.index(video)
                new_widget = self.create_video_widget(video)
                self.current_page.walker[index] = new_widget
        return None

    def key_event(self, event, index):
        """
        Called when the input found a key combo that has been bound.
        
        :event: str: The name of the event that was found.
        :index: int: The index of the cursor on the video list.
        :return: None
        """
        name, *params = event.split(' ')
        params.insert(0, index)
        event_name = 'event_{}'.format(name)
        call = (getattr(self.current_page, event_name, None) or
                getattr(self, event_name, None) or
                getattr(self.terminal, event_name, None))
        if call is not None:
            call(*params)
        return None

    def create_video_widget(self, video, reuse=True):
        """
        Create the widget that represents one of the videos.
        
        :video: Video: The video to create a widget for.
        :reuse: bool: True if this should re-use a video from the
                           video storage.
                      False otherwise.
        :return: urwid.AttrMap: The attrmap surrounding the video widget.
        """
        if video in self.video_storage and reuse:
            video = self.video_storage[self.video_storage.index(video)]
        else:
            self.video_storage.append(video)
        focusmap = {'': 'title'}
        video_colour = ''
        status = video.status
        name = video.name
        if video.cache is not None:
            video_colour = 'blue'
            focusmap = {'blue': 'blue_bold'}
        widget = urwid.Text((video_colour, name))
        status_widget = urwid.Text((video_colour, status), 'right')
        column = urwid.Columns([('pack', widget), status_widget])
        output = urwid.AttrMap(column, None, focusmap)
        video.widget = output
        return output

    def load_playlist(self, playlist_name):
        """
        Load a playlist and populates the playlist page.
        
        :playlist_name: str: The name of the playlist to load.
        :return: None
        """
        videos = []
        for data in self.playlists[playlist_name]:
            video = Video(data['name'], data['location'], data['resource'],
                          data['cache'])
            videos.append(video)
        page = self.pages['playlist_items'](self)
        page.results = videos
        page.description = playlist_name
        page.playlist_name = playlist_name
        page.load_page()
        self.saved_pages['playlist_items'] = page
        self.load_page('playlist_items')
        self.loop.draw_screen()
        return None

    @Hook('PLAY')
    def play(self, video, audio=False):
        """
        Play a video, optionally as audio.
        
        :video: Video: The video to play.
        :audio: bool: True if you want to only play audio.
                      False otherwise.
        :return: bool: True if the PLAY hook should run.
                       False otherwise.
                 bool: True if the cursor should move one down.
                       False otherwise.
        """
        video.audio = audio
        if video == self.playing:
            video.stop()
            return False, False
        if video not in self.queue:
            self.queue.append(video)
            self.playing_position += 1
        if self.playing is not None:
            self.set_video_status(self.playing, '')
            if video in self.queue:
                self.playing_position = (True, self.queue.index(video))
            else:
                self.queue.insert(0, video)
                self.playing_position = 0
            self.playing.stop() 
            return False, False
        
        self.playing = video
        self.run_command(video, audio)
        return True, True

    def play_finish(self, video, audio=False, force=False):
        """
        Called when the video finishes playing.
        
        :video: Video: The video that was playing.
        :audio: bool: True if the video was played as audio.
                      False otherwise.
        force: bool: True if it shold force the video to stop.
                     False otherwise.
        """
        if self.state['consume'] and video in self.queue and not force:
            index = self.queue.index(video)
            self.playing_position -= 1
            del self.queue[index]
            self.update_queue_page()
        self.set_video_status(video, '')
        self.playing = None
        if self.queue != []:
            if self.playing_position >= len(self.queue):
                if self.state['repeat'] and not force:
                    self.playing_position = 0
                else:
                    self.destroy_terminal_widget()
                    self.clear_queue()
                    self.update_queue_page()
                    return None
            next_video = self.queue[self.playing_position]
            self.playing_position += 1
            self.play(next_video, next_video.audio)
            self.update_queue(update_page=False)
        else:
            self.destroy_terminal_widget()
        return None

    def clear_queue(self):
        """Clear all of the videos in the queue."""
        for video in self.queue:
            self.set_video_status(video, '')
        self.queue = []
        return None

    @threads.AsThread()
    def queue_add(self, video):
        """
        Add a video to the queue. It will remove items if they
        are already in the queue.
        
        :video: Video: The video to add to the queue.
        :return: None
        """
        if self.playing is None:
            self.play(video, video.audio)
            return None
        if video == self.playing:
            return False
        if video in self.queue:
            index = self.queue.index(video)
            del self.queue[index]
            self.set_video_status(video, '')
            move = False
        else:
            self.queue.append(video)
            status = 'Queue #{}'.format(len(self.queue))
            self.set_video_status(video, status)
            video.resource()
            self.loop.draw_screen()
            move = True
        self.update_videos()
        self.update_queue()
        return move

    def update_queue_page(self):
        """
        Update the queue page then redraw the UI.
        
        :return: None
        """
        if isinstance(self.current_page, queue_items.Interface):
            self.current_page.load_page()
            self.load_page('queue', False)
            self.loop.draw_screen()
            return None

        if self.saved_pages['queue'] is None:
            return None
        self.saved_pages['queue'].load_page()
        return None

    def update_queue(self, start=0, update_page=True):
        """
        Update the queue, re-setting the status's and redrawing the page.

        :start: int: The video index to start at.
        :update_page: bool: True if the page should be redrawn.
                            False otherwise.
        :return: None
        """
        for index, video in enumerate(self.queue[start:]):
            if self.playing == video:
                continue
            self.set_video_status(video, 'Queue #{}'.format(index + start + 1))
        if update_page:
            self.update_queue_page()
        return None

    #TODO: Probably should re-name this to update_cache_page
    def update_cache(self):
        """Update the cache page."""
        self.update_videos()
        if isinstance(self.current_page, cache_items.Interface):
            self.current_page.load_page()
            self.load_page('cache')
            self.loop.draw_screen()
        elif self.saved_pages['cache'] is not None:
            self.saved_pages['cache'].load_page()
        return None

    def set_video_status(self, video, status):
        """
        Set the text next to a video. It will also re-draw the UI

        :video: Video: The video to change the status of.
        :status: str: The new status to change to.
        :return: None
        """
        video.status = status
        self.current_page.update_video(video)
        if video in self.video_storage:
            index = self.video_storage.index(video)
            self.video_storage[index] = video
        self.redraw()
        return None

    @threads.AsThread()
    def redraw(self):
        """
        I was experiencing some weird redraw issues when it happened
        too fast, This function aims to solve that by attempting
        the redraw 10 times in another thread.
        """
        for i in range(10):
            try:
                self.loop.redraw()
            except AttributeError:
                continue
            else:
                break
        return None

    @threads.AsThread()
    def run_command(self, video, audio=False):
        """
        Runs the user specified command for running the video / audio.

        :video: Video: The video to play.
        :audio: bool: True if it should be played as audio.
                      False otherwise.
        :return: None
        """
        command = PLAYER['command']
        arg_settings = 'audio_args' if audio else 'video_args'
        arguments = PLAYER[arg_settings]
        previous = video.status
        self.set_video_status(video, 'Loading')
        resource = video.resource(audio)
        if resource is None:
            return None
        self.set_video_status(video, 'Playing')
        full_command = [command] + arguments + [resource]
        self.create_terminal_widget(video, full_command, audio)
        return None

    @threads.AsThread()
    def download_video(self, video):
        """
        Starts a download of the video. Thanks to youtube-dl

        :video: Video: The video to download.
        :return: None
        """
        if video.downloading or video._resource != 'youtube':
            return None

        video.download = True
        video_id = video.location
        video_name = video.name

        if os.path.exists(video_id):
            return None
        
        self.set_video_status(video, 'Pending...')

        url = 'https://youtube.com/watch?v={}'.format(video_id)
        options = {
            'logger': VoidLogger(),
            'progress_hooks': [lambda i: self.download_handler(video, i)],
            'outtmpl': '{}{}.%(ext)s'.format(CACHE_LOCATION, video_name)
            }

        ydl = youtube_dl.YoutubeDL(options)
        ydl.download([url])

        cached = {os.path.splitext(v)[0]: v for v in os.listdir(CACHE_LOCATION)}
        video.cache = cached.get(video_name, None)
        self.update_cache()
        self.loop.draw_screen()
        return None

    def download_handler(self, video, info):
        """
        Handles information given to the program from youtube-dl

        :video: Video: The video that is being downloaded
        :info: dict: Information from youtube-dl
        :return: None
        """
        if info['status'] == 'downloading':
            percentage = info['downloaded_bytes'] / info['total_bytes'] * 100
            status = '{}%'.format(round(percentage))
            self.set_video_status(video, status)
        if info['status'] == 'finished':
            self.download_finished(video)
        return None

    @Hook('DOWNLOAD_FINISHED')
    def download_finished(self, video):
        """
        Called when the download finishes.

        :video: Video: The video that was downloading.
        :return: bool: True if it should run the DOWNLOAD_FINISHED hook
                       False otherwise
                 None
        """
        self.set_video_status(video, 'Finished')
        return True, None

    def add_playlist(self, playlist_name):
        """
        Add a playlist to the playlist list (yo dawg I heard you like lists)

        :playlist_name: str: The name of the playlist to add.
        :return: None
        """
        self.destroy_search_widget()
        self.playlists[playlist_name] = []
        if isinstance(self.current_page, playlist.Interface):
            self.current_page.load_page()
            self.load_page('playlist')
            self.loop.draw_screen()
        elif self.saved_pages['playlist'] is not None:
            self.saved_pages['playlist'].load_page()
        return None

    def create_terminal_widget(self, video, command, audio=False):
        """
        Creates and runs the terminal widget.

        :video: Video: The video to play.
        :command: list: The command that will be run in the terminal
        :audio: bool: True if it should be run as audio,
                      False otherwise
        :return: None
        """
        finish = lambda *args: self.play_finish(video, audio=audio)
        terminal = TerminalWidget(self, command, main_loop=self.loop)
        self.widgets.contents[3] = (terminal, ('given', PLAYER['size']))
        video.terminal = terminal
        urwid.connect_signal(terminal, 'closed', finish)
        self.loop.draw_screen()
        return None

    def destroy_terminal_widget(self):
        """Destroys the terminal widget"""
        self.widgets.contents[3] = (urwid.Filler(urwid.Text('')), ('given', 0))
        self.widgets.focus_position = 0
        return None

    def unhandled_input(self, key, mode='global'):
        """
        Gets called when the main UI recieves input that was not
        sent to any of the page widgets.

        :key: str: The key that was sent.
        :mode: str: The keybindings to use.
        :return: bool: True if there was a keybinding found.
                       False otherwise.
        """
        if isinstance(key, tuple):
            return False
        self.keybuffer.append(key)
        keys = KEYBINDS.get(mode, {})
        possible = []
        matches = []
        if key == 'backspace':
            self.keybuffer = self.keybuffer[:-2]
        for key in self.keybuffer[::-1]:
            possible.append(key)
            for index, key in sorted(enumerate(keys), key=lambda a: len(a)):
                if ''.join(possible) == str(key):
                    matches.append(str(key))
        if matches != []:
            key = sorted(matches, key=lambda x: len(x))[-1]
            event = keys[key]
            self.key_event(event, 0)
            self.keybuffer = []
            return True
        return False

    def event_PAGE(self, _, page_name):
        self.load_page(page_name)
        self.loop.draw_screen()
        return None

    def event_SEND_KEY(self, _, key):
        if self.playing is not None:
            self.playing.terminal.respond(key)
        return None

    def event_FOCUS_PLAYER(self, _):
        if self.playing is not None:
            self.widgets.focus_position = 3
        return None

    def event_FOCUS_NORMAL(self, _):
        self.widgets.focus_position = 0
        return None

    def event_SEARCH(self, _):
        self.create_search_widget('search: ', self.search)
        return None

    def event_QUIT(self, _):
        raise urwid.ExitMainLoop()

    def event_CREATE_PLAYLIST(self, _):
        self.create_search_widget('Playlist: ', self.add_playlist)
        return None

    def event_TOGGLE_CONSUME(self, _):
        self.state['consume'] = not self.state['consume']
        self.update_state()
        return None

    def event_TOGGLE_REPEAT(self, _):
        self.state['repeat'] = not self.state['repeat']
        self.update_state()
        return None

    def event_TOGGLE_RANDOM(self, _):
        self.state['random'] = not self.state['random']
        self.update_state()
        return None

    def event_FIND_VIDEO(self, _):
        self.find_video = True
        return None
