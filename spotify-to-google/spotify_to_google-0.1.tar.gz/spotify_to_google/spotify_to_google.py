#! /usr/bin/env python3
""" Simple python script

Imports Spotify playlists into your Google Play Music account
"""


import sys
import spotipy
import spotipy.oauth2 as oauth2
from gmusicapi import Mobileclient


# Logging stuff
from .log import setup_logger
logger = setup_logger("spotify_to_google.py")


class InvalidCredentialsException(Exception):
    pass


class ItemNotFoundException(Exception):
    pass


def generate_token():
    """ Returns token for Spotify Web API authorization """
    credentials = oauth2.SpotifyClientCredentials(
        client_id='e003d5914588476f95a135976de0ab16',
        client_secret='3c7b3f8f1ccc4a81a8f86792b6efeb3e')
    token = credentials.get_access_token()
    return token


def get_tracks(input):
    """ Returns list of tracks """
    tracks_list = []
    logger.info("Start creating tracks list")
    for i, item in enumerate(input['items']):
        track = item['track']
        tracks_list.append(track['artists'][0]['name'] + ' ' + track['name'])
    logger.info("Successfully created tracks list")
    return tracks_list


def import_all_playlists(spotify_user, google_user, goolge_password):
    """ Reads all spotify playlists and creates new playlists in Google Play Music account """
    api = Mobileclient()
    api.login(google_user, goolge_password, Mobileclient.FROM_MAC_ADDRESS)
    if not api:
        logger.error("invalid credentials!")
        logger.critical("unable to login, invalid username or password")
        raise InvalidCredentialsException("invalid credentials!")
    token = generate_token()
    spotify = spotipy.Spotify(auth=token)
    playlists = spotify.user_playlists(spotify_user)
    if playlists:
        for playlist in playlists['items']:
            if playlist['owner']['id'] == spotify_user:
                logger.info('Current playlist:',
                            playlist['name'], "total tracks:", playlist['tracks']['total'])
                results = spotify.user_playlist(
                    spotify_user, playlist['id'], fields="tracks,next")
                results_tracks = results['tracks']
                tracks = get_tracks(results_tracks)
                while results_tracks['next']:
                    results_tracks = spotify.next(results_tracks)
                    next_tracks = get_tracks(results_tracks)
                    tracks = tracks + next_tracks
                # Create new playlist in google play music
                create_google_playlist(playlist['name'], tracks,api)
    else:
        logger.critical("%ss playlists not found" % (spotify_user))
        raise ItemNotFoundException("%ss playlists not found" % (spotify_user))


def create_google_playlist(name, tracks,api):
    logger.debug("Creating new playlist %s..." % (name))
    new_playlist = api.create_playlist(name)
    tracks_ids = []
    # get tracks ids for gmusicapi.add_songs_to_playlis
    for track in tracks:
        try:
            obj = api.search(track)['song_hits'][0]['track']['storeId']
            tracks_ids.append(obj)
            logger.info("Found %s" % (track))
        except:
            logger.warning("Track %s not found" % (track))
            continue
    api.add_songs_to_playlist(new_playlist, tracks_ids)