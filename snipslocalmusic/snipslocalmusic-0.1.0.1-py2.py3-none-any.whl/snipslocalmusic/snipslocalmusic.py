# -*-: coding utf-8 -*-
""" Local music player skill for Snips. """

import itertools
import json
import pygame
import random


class SnipsLocalMusic:

    def __init__(self, db_file_path):
        """ Initialisation.

        :param db: the json music database.
        """
        with open(db_file_path, 'r') as f:
            db = json.loads(f.read().replace('\n', ''))
            if db:
                self.songs = db["songs"]
                self.genres = list(set(itertools.chain.from_iterable(
                    map(lambda s: s["genres"], self.songs))))

    def play(self,
             sourceCollectionOwnerName=None,
             sourceCollectionName=None,
             musicCreativeWorkSelect=None,
             musicCreativeWorkArtistName=None,
             musicCreativeWorkGenre=None,
             musicCreativeWorkContentSource=None,
             musicCreativeWorkComposerName=None,
             musicCreativeWorkName=None,
             musicCreativeWorkEra=None,
             musicCreativeWorkType=None):
        """ Play a track.

        :param sourceCollectionOwnerName: collection owner name.
        :param sourceCollectionName: collection name.
        :param musicCreativeWorkSelect: unused.
        :param musicCreativeWorkArtistName: artist name.
        :param musicCreativeWorkGenre: music genre.
        :param musicCreativeWorkContentSource: content source.
        :param musicCreativeWorkComposerName: composer name.
        :param musicCreativeWorkName: song name.
        :param musicCreativeWorkEra: music era.
        :param musicCreativeWorkType: music type.
        """
        filename = None
        if musicCreativeWorkArtistName:
            filename = self.find_by_artist(musicCreativeWorkArtistName)
        elif musicCreativeWorkGenre:
            filename = self.find_by_genre(musicCreativeWorkGenre)
        elif musicCreativeWorkName:
            filename = self.find_by_genre(musicCreativeWorkName)
        else:
            filename = self.find_random()

        if filename:
            self.play_file(filename)

    def play_playlist(self,
                      musicPlaylistOwnerName,
                      musicPlaylistName,
                      playbackModeName,
                      musicPlaylistSelect):
        """ Play songs from a playlist.

        :param musicPlaylistOwnerName: playlist owner name.
        :param musicPlaylistName: playlist name.
        :param playbackModeName: mode name.
        :param musicPlaylistSelect: unused.
        """
        pass

    def stop(self):
        """ Stop the music. """
        AudioPlayer.stop()

    def pause(self):
        """ Pause the music. """
        AudioPlayer.pause()

    def resume(self):
        """ Resume the music. """
        AudioPlayer.resume()

    def play_file(self, filename):
        """ Play a file.

        :param filename: the path to the audio file to play.
        """
        if not filename:
            return

        AudioPlayer.play(filename, None)

    def find_random(self):
        """ Get a random song from the db. """
        if not self.songs:
            return None
        return random.choice(self.songs)["filename"]

    def find_by_artist(self, artist):
        """ Find song by artist name.

        :param artist: the artist name to look for.
        :return: a song matching the artist name, or None.
        """
        if not self.songs:
            return None
        results = []
        for song in self.songs:
            if song["artist"].lower() == artist.lower():
                results.append(song["filename"])
        if not results:
            return None
        return random.choice(results)

    def find_by_genre(self, genre):
        """ Find song by genre.

        :param genre: the genre to look for.
        :return: a song matching the genre, or None.
        """

        # Normalize the genre, e.g. map "jazzy" to the
        # "jazz" genre.

        def normalize_genre(freetext_genre):
            for valid_genre in self.genres:
                if valid_genre in freetext_genre:
                    return valid_genre
            return freetext_genre

        genre = normalize_genre(genre)

        if not self.songs:
            return None

        results = []
        for song in self.songs:
            if genre in song["genres"]:
                results.append(song["filename"])
        if not results:
            return None
        return random.choice(results)

    def find_by_playlist(self, playlist):
        """ Find songs in a given playlist.

        :param playlist: the playlist to look for.
        :return: a random song from the provided playlist, or None.
        """
        if not self.songs:
            return None

        results = []
        for song in self.songs:
            if playlist in song["playlists"]:
                results.append(song["filename"])
        if not results:
            return None
        return random.choice(results)


class AudioPlayer:
    """ A simple audio player."""

    @staticmethod
    def play(filename, on_done):
        """ Play a file.

        :param filename: the path to the audio file to play.
        :param on_done: callback to execute when playing is done.
        """
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
        if on_done:
            on_done()

    @staticmethod
    def stop():
        """ Stop the player. """
        pygame.mixer.init()
        pygame.mixer.music.stop()

    @staticmethod
    def pause():
        """ Pause the player. """
        pygame.mixer.init()
        pygame.mixer.music.pause()

    @staticmethod
    def resume():
        """ Resume the player. """
        pygame.mixer.init()
        pygame.mixer.music.unpause()
