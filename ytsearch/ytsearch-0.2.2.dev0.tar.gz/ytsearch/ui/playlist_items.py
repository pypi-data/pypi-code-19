#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import urwid

from ytsearch import ui, settings
from ytsearch.ui import page


class Interface(page.Page):

    """
    The interface for the playlist items.

    :page.Page: The base page to load.
    """
    mode = 'playlist_items'
    playlist_name = None
    videos = []

    def load_page(self):
        """
        Load the widgets of this page.

        :return: urwid.Pile: The pile with all of the widgets in there.
        """
        if self.description != '':
            description = " - '{}'".format(self.description)
        else:
            description = ''
        title = urwid.Filler(urwid.Text([('title', 'Playlist'),
                             '{}'.format(description)]), 'top')
        header = urwid.Columns([(title)])
        videos = self.load_videos()
        pile = urwid.Pile([(2, header), ('weight', 1, videos)])
        self.widgets = pile
        return pile

    def load_videos(self):
        """
        Load all of the videos from the playlist storage.

        :return: urwid.ItemList: The list of widgets to load.
        """
        videos = []
        for video in self.results:
            widget = self.parent.create_video_widget(video)
            videos.append(widget)
        self.walker = urwid.SimpleListWalker(videos)
        self.video_list = ui.ItemList(self.parent, self.walker, 'playlist_items')
        return self.video_list

    def event_REMOVE_PLAYLIST_ITEM(self, index):
        if self.video_list is None:
            return None
        video = self.results[index]
        name = self.playlist_name
        data = {'name': video.name, 'location': video.location,
                'resource': video._resource, 'cache': video.cache}
        if data in list(self.parent.playlists[name]):
            playlist_index = self.parent.playlists[name].index(data)
            del self.parent.playlists[name][playlist_index]
            self.parent.load_playlist(name)
        return None
