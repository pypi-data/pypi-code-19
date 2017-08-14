
from datetime import timedelta

import humanize


class TimeeDuration(object):

    def __init__(self, seconds):
        self._seconds = seconds

    @property
    def seconds(self):
        return self._seconds

    @property
    def in_words(self):

        in_words = humanize.naturaldelta(timedelta(seconds=self.seconds))

        return in_words

    def __repr__(self):

        repr_string = '<TimeeDuration | words:{in_words} | seconds:{seconds} >'.format(
            in_words=self.in_words,
            seconds=self.seconds
        )

        return repr_string
