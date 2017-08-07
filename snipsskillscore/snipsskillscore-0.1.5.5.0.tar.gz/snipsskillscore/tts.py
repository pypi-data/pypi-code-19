# -*-: coding utf-8 -*-
""" Wrapper for various TTS services (currently only Google). """

import json
import os

from gtts import gTTS

from .logging import debug_log

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
        snips_dir = ".snips"
        filename = "gtts.mp3"
        file_path = "{}/{}".format(snips_dir, filename)

        if not os.path.exists(snips_dir):
            os.makedirs(snips_dir)

        def delete_file():
            try:
                os.remove(file_path)
                if not os.listdir(snips_dir):
                    try:
                        os.rmdir(snips_dir)
                    except OSError:
                        pass
            except:
                pass

        debug_log("Speak: {}".format(sentence))
        tts = gTTS(text=sentence, lang=self.locale)
        tts.save(file_path)
        AudioPlayer.play_async(file_path, delete_file)
