import pygame
from pygame.mixer import music
import subprocess


class SoundPlayer(object):

    def __init__(self, sound):
        if not subprocess.run(['which', 'mpg321']):
            self.cmd = ['mpg321', sound]
        else:
            self.cmd = None
            pygame.init()
            self.sound = sound

    def play(self):
        if self.cmd is not None:
            subprocess.run(self.cmd)
        else:
            music.load(self.sound)
            music.play()

    def schedule(self, duration, loop):
        loop.call_later(duration, self.play)
