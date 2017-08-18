import sys
import argparse
import re
import json
from urllib.parse import urlencode
from urllib.request import urlopen

site_url = 'https://www.metal-archives.com/'
url_search_songs = 'search/ajax-advanced/searching/songs?'
url_lyrics = 'release/ajax-view-lyrics/id/'
lyrics_not_available = '(lyrics not available)'
lyric_id_re = re.compile(r'id=.+[a-z]+.(?P<id>\d+)')
band_name_re = re.compile(r'title="(?P<name>.*)\"')
tags_re = re.compile(r'<[^>]+>')

def get_songs_data(band_name, song_title):
    """Search on metal-archives for song coincidences"""
    params = dict(bandName = band_name, songTitle = song_title)
    url = site_url + url_search_songs + urlencode(params)
    return json.load(urlopen(url))['aaData']

def get_lyrics_by_song_id(song_id):
    """Search on metal-archives for lyrics based on song_id"""
    url = site_url + url_lyrics + song_id
    return tags_re.sub('', urlopen(url).read().strip().decode())

def iterate_songs_and_print(songs):
    '''Iterate over returned song matches. If the lyrics are different than\
    "(lyrics not available)" then break the loop and print them out.\
    Otherwise the last song of the list will be printed.'''
    for song in songs:
        band_name = band_name_re.search(song[0]).group("name")
        song_title = song[3]
        song_id = lyric_id_re.search(song[4]).group("id")
        lyrics = get_lyrics_by_song_id(song_id)
        if lyrics != lyrics_not_available:
            break

    return lyrics


#----------------------------------------------------------------------
def get_lyrics(artist, album, title):
    """"""
    songs_data = get_songs_data(artist, title)

    if len(songs_data):
        return iterate_songs_and_print(songs_data)
    else:
        return None

