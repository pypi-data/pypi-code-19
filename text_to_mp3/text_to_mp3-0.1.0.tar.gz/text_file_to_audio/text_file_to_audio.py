# -*- coding: utf-8 -*-

"""Main module."""
from gtts import gTTS


def audio(path):
    """Convert text file to audio."""
    f = open(path, "r")
    audio_string = f.read()
    tts = gTTS(text=audio_string, lang='en')
    tts.save("audio.mp3")
    return False
