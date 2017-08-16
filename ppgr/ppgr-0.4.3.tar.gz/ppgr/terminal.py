import sys
from contextlib import contextmanager
from time import sleep


def write(s="", wait=None, clear=True, flush=True, end="", stream=sys.stdout):
    """Write that defaults to flushing and clearing the screen, can also sleep after writing."""

    if clear:
        stream.write("\x1b[2J\x1b[H")
    stream.write(str(s) + end)
    if flush:
        stream.flush()
    if wait is not None:
        sleep(wait)


@contextmanager
def no_cursor():
    """Contextmanager that hides the cursor in terminal."""

    write("\x1b[?25l", clear=False)
    try:
        yield
    finally:
        write("\x1b[?25h", clear=False)
