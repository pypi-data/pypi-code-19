import pygame
from pygame.mixer import music


class SoundPlayer(object):

    def __init__(self, sound):
        pygame.init()
        self.sound = sound

    def play(self):
        music.load(self.sound)
        music.play()

    def schedule(self, duration, loop):
        loop.call_later(duration, self.play)
