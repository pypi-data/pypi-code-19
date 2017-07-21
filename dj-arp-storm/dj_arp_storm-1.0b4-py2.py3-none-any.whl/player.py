import threading
from glob import glob
from os import listdir, path
import os
import sys
from time import sleep
import pygame


# Define a context manager to suppress stdout and stderr.
class suppress_stdout_stderr(object):
    '''
    stolen from: https://stackoverflow.com/questions/11130156/suppress-stdout-stderr-print-from-python-functions
    A context manager for doing a "deep suppression" of stdout and stderr in
    Python, i.e. will suppress all print, even if the print originates in a
    compiled C/Fortran sub-function.
       This will not suppress raised exceptions, since exceptions are printed
    to stderr just before a script exits, and after the context manager has
    exited (at least, I think that is why it lets exceptions through).

    '''
    def __init__(self):
        # Open a pair of null files
        self.null_fds =  [os.open(os.devnull,os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0],1)
        os.dup2(self.null_fds[1],2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0],1)
        os.dup2(self.save_fds[1],2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])

class Player(object):
    def __init__(self, instrument_path, channel_count=60):
        self.instrument_path = instrument_path
        self.sounds = {}
        self.channel_count = channel_count
        with suppress_stdout_stderr():
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
    player = Player(sys.argv[1])
    player.load()
    player.scale(player.sounds['piano'], mod=0.5)
    player.scale(player.sounds['guitar'], mod=0.3)
    sleep(10)
