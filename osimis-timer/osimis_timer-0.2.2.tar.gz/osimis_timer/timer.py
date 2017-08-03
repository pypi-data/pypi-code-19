import time


class Timer:
    """
    Helper to measure time duration (in seconds/ms)

    example:
        timer = Timer()  # creates and starts the Timer
        lengthyOperation()
        elapsed = timer.getElapsedSeconds() # get the elapsed time.  The timer continues to measure the elapsed time
        lengthyOperation()
        elapsed = timer.getElapsedSeconds() # get the elapsed time since beginning

        timer.reset()  # reset the timer
    """


    def __init__(self):
        self.reset()

    def reset(self):
        self._start = time.perf_counter()

    def getElapsedSeconds(self):
        stop = time.perf_counter()
        return stop - self._start

    def getElapsedMs(self):
        return 1000.0 * self.getElapsedSeconds()
