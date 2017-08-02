# -*-: coding utf-8 -*-
""" A simple audio player based on pygame. """

import pygame

from .logging import log_warning

class AudioPlayer:
    """ A simple audio player based on pygame. """

    @staticmethod
    def play(file_path, on_done=None):
        """ Play an audio file.

        :param file_path: the path to the file to play.
        :param on_done: callback when audio playback completes.
        """
        pygame.mixer.init()
        try:
            pygame.mixer.music.load(file_path)
        except pygame.error as e:
            log_warning(str(e))
            return

        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
        if on_done:
            on_done()

    @staticmethod
    def stop():
        """ Stop the audio. """
        pygame.mixer.init()
        pygame.mixer.music.stop()

    @staticmethod
    def pause():
        """ Pause the audio. """
        pygame.mixer.init()
        pygame.mixer.music.pause()

    @staticmethod
    def resume():
        """ Resume the audio. """
        pygame.mixer.init()
        pygame.mixer.music.unpause()
