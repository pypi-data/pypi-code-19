# -*-: coding utf-8 -*-
""" Sound service for playing various state sounds. """

from .audio_player import AudioPlayer


SOUND_DIR = "data/sounds"

class SoundService:

    class State:
        none, welcome, goodbye, hotword_detected, asr_text_captured, error = range(6)

    @staticmethod
    def play(state):
        filename = None
        if state == SoundService.State.welcome:
            filename = "pad_glow_welcome1.wav"
        elif state == SoundService.State.goodbye:
            filename = "pad_glow_power_off.wav"
        elif state == SoundService.State.hotword_detected:
            filename = "pad_soft_on.wav"
        elif state == SoundService.State.asr_text_captured:
            filename = "pad_soft_off.wav"
        elif state == SoundService.State.error:
            filename = "music_marimba_error_chord_2x.wav"

        if filename is not None:
            AudioPlayer.play("{}/{}".format(SOUND_DIR, filename))
