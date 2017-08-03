# -*-: coding utf-8 -*-
""" Wrapper for various TTS services (currently only Google). """

import json
import os

from gtts import gTTS

from .audio_player import AudioPlayer


class TTS:
    """ Wrapper for TTS service. """

    class Provider:
        """ Supported providers. """
        google = range(1)

    def __init__(self, provider, locale):
        """ Initialise the service.

        :param provider: the TTS provider, e.g. TTS.Provider.google.
        :param locale: the short language locale, e.g. "fr".
        """
        self.tts = GTTS(locale)

    def speak(self, sentence):
        """ Speak a sentence.

        :param sentence: the sentence to speak.
        """
        if self.tts is None:
            return
        self.tts.speak(sentence)


class GTTS:
    """ Google TTS service. """

    def __init__(self, locale):
        """ Initialise the service.

        :param locale: the language locale, e.g. "fr" or "en_US".
        """
        self.locale = locale.split("_")[0]

    def speak(self, sentence):
        """ Speak a sentence using Google TTS.

        :param sentence: the sentence to speak.
        """
        filename = "gtts.mp3"

        def delete_file():
            try:
                os.remove(filename)
            except:
                pass

        tts = gTTS(text=sentence, lang=self.locale)
        tts.save(filename)
        AudioPlayer.play_async(filename, delete_file)
