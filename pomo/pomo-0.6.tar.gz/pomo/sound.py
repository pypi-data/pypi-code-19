import pygame
from pygame.mixer import music
import os


class SoundPlayer(object):

    def __init__(self, sound):
        if not os.system('which mpg321'):
            self.cmd = 'mpg321 {}'.format(sound)
        else:
            self.cmd = None
            pygame.init()
            self.sound = sound

    def play(self):
        if self.cmd is not None:
            os.system(self.cmd)
        else:
            music.load(self.sound)
            music.play()

    def schedule(self, duration, loop):
        loop.call_later(duration, self.play)
