import threading
from glob import glob
from os import listdir, path
from sys import argv
from time import sleep
import pygame


class Player(object):
    def __init__(self, instrument_path, channel_count=60):
        self.instrument_path = instrument_path
        self.sounds = {}
        self.channel_count = channel_count
        pygame.mixer.quit()
        pygame.mixer.init(frequency=44100,size=-16,channels=2,buffer=65536)
        pygame.mixer.quit()
        pygame.mixer.init(44100, -16, 2, 4096)
        pygame.mixer.set_num_channels(channel_count)

    def load(self):
        for instrument in listdir(self.instrument_path):
            instrument_full = path.join(self.instrument_path, instrument)
            notes = glob(path.join(instrument_full, "*.ogg"))
            paths = [path.abspath(path.join(instrument_full, note)) for note in notes]
            self.sounds[instrument] = {
                path.basename(note):pygame.mixer.Sound(path.abspath(note)) for note in notes
            }

    @staticmethod
    def play(note):
        channel = None
        while channel is None:
            channel = pygame.mixer.find_channel()
        channel.queue(note)

    def delay_play(self, note, delay=1):
        threading.Timer(delay, Player.play, [note]).start()

    def scale(self, instrument, mod=1):
        for delay, note  in enumerate(instrument.values(), 1):
            self.delay_play(note, delay*mod)

if __name__ == "__main__":
    player = Player(argv[1])
    player.load()
    player.scale(player.sounds['piano'], mod=0.5)
    player.scale(player.sounds['guitar'], mod=0.3)
    sleep(10)
