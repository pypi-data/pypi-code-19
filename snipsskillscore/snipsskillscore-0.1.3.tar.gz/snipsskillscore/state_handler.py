# -*-: coding utf-8 -*-
""" Handler for various states of the system. """

from snipsskillscore.constants import Constants as C


class StateHandler:
    """ Handler for various states of the system. """

    def __init__(self, threading, leds_service, sound_service):
        self.threading = threading
        self.leds_service = leds_service
        self.sound_service = sound_service
        self.state = None

    def set_state(self, state):
        if state == C.State.welcome:
            self.sound_service.play(C.State.welcome)
        elif state == C.State.goodbye:
            self.sound_service.play(C.State.goodbye)
            self.leds_service.start_animation(C.LedsAnimation.none)
        elif state == C.State.hotword_toggle_on and self.state != state:
            self.leds_service.start_animation(C.LedsAnimation.standby)
        elif state == C.State.hotword_detected:
            self.sound_service.play(C.State.hotword_detected)
        elif state == C.State.asr_toggle_on and self.state != state:
            self.leds_service.start_animation(C.LedsAnimation.listening)
        elif state == C.State.asr_text_captured:
            self.sound_service.play(C.State.asr_text_captured)
        self.state = state
