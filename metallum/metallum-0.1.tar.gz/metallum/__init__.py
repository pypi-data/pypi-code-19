import os
from urllib.parse import quote_plus
import time

import dbus
import requests
from bs4 import BeautifulSoup
from colorama import init
from termcolor import colored

from .metrolyrics import get_lyrics as metrolyrics
from .metallum import get_lyrics as metallum

init()


#----------------------------------------------------------------------
def get_current_song():
    """"""
    session_bus = dbus.SessionBus()
    spotify_bus = session_bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    spotify_properties = dbus.Interface(spotify_bus, "org.freedesktop.DBus.Properties")
    metadata = spotify_properties.Get("org.mpris.MediaPlayer2.Player", "Metadata")

    try:
        artist = metadata['xesam:artist'][0].title()
        title =  metadata['xesam:title']
        album = metadata['xesam:album']
        return artist, album, title
    except:
        return None

#----------------------------------------------------------------------
def print_lyrics(artist, album, title, lyrics):
    """"""

    W = 70
    center = lambda l:l.ljust(W//2+len(l)//2, ' ').rjust(W, ' ')
    write = lambda text, color, on_color, attr: print(colored(center(text), color, on_color, attr))


    write(title, 'white', 'on_red', ['bold'])
    write('{}-{}'.format(artist, album), 'white', 'on_red', ['reverse'])
    print('\n')
    if lyrics:
        for line in  lyrics.split('\n'):
            write(line, 'white', None, [])


current_song = None
while True:
    if current_song != get_current_song():
        current_song = get_current_song()

        lyrics = metallum(*current_song)
        if not lyrics:
            lyrics = metrolyrics(*current_song)

        #print(lyrics)
        os.system('clear')
        print_lyrics(*current_song, lyrics)
    time.sleep(5)