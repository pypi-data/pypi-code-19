# -*-: coding utf-8 -*-
""" Handler for various states of the system. """

from .sound_service import SoundService

class State:
    none, welcome, goodbye, hotword_toggle_on, hotword_detected, asr_toggle_on, asr_text_captured, error, idle = range(
        9)

class StateHandler:
    """ Handler for various states of the system. """

    def __init__(self):
        # self.leds_service = leds_service
        self.sound_service = SoundService()
        self.state = None

    def set_state(self, state):
        if state == State.welcome:
            SoundService.play(SoundService.State.welcome)
        elif state == State.goodbye:
            SoundService.play(SoundService.State.goodbye)
            # self.leds_service.start_animation(C.LedsAnimation.none)
        elif state == State.hotword_toggle_on and self.state != state:
            pass
            # self.leds_service.start_animation(C.LedsAnimation.standby)
        elif state == State.hotword_detected:
            SoundService.play(SoundService.State.hotword_detected)
        elif state == State.asr_toggle_on and self.state != state:
            pass
            # self.leds_service.start_animation(C.LedsAnimation.listening)
        elif state == State.asr_text_captured:
            SoundService.play(SoundService.State.asr_text_captured)
        self.state = state
