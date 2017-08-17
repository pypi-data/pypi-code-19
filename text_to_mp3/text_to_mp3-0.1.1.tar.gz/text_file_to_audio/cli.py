# -*- coding: utf-8 -*-

"""Console script for text_file_to_audio."""

import sys
import threading
import time
import click
from .text_file_to_audio import audio


@click.argument('path')
@click.command()
def main(path):
    """Console script for text_file_to_audio."""
    if path:
        click.echo("Creating audio file.......")
        loader = KThread(target=loading)
        loader.start()

        audio(path)
        loader.kill()

    else:
        click.echo("Text file path required")
    return


class KThread(threading.Thread):
    """
    A subclass of threading.

    Thread, with a kill() method.
    """

    def __init__(self, *args, **keywords):
        """Init."""
        threading.Thread.__init__(self, *args, **keywords)
        self.killed = False

    def start(self):
        """Start the thread."""
        self.__run_backup = self.run
        self.run = self.__run      # Force the Thread to install our trace.
        threading.Thread.start(self)

    def __run(self):
        """Hacked run function, which installs the trace."""
        sys.settrace(self.globaltrace)
        self.__run_backup()
        self.run = self.__run_backup

    def globaltrace(self, frame, why, arg):
        """Trace."""
        if why == 'call':
            return self.localtrace
        else:
            return None

    def localtrace(self, frame, why, arg):
        """Local trace."""
        if self.killed:
            if why == 'line':
                raise SystemExit()
        return self.localtrace

    def kill(self):
        """Kill."""
        self.killed = True


def spinning_cursor():
    """Spinning cursor."""
    while True:
        for cursor in '|/-\\':
            yield cursor


def loading():
    """Loader"""
    spinner = spinning_cursor()
    while True:
        sys.stdout.write(spinner.next())
        sys.stdout.flush()
        time.sleep(0.1)
        sys.stdout.write('\b')


if __name__ == "__main__":
    main()
