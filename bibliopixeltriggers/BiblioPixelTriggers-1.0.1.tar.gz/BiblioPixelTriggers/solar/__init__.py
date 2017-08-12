from datetime import datetime
from . sunrise_sunset import SunriseSunset
from bibliopixel.remote import trigger
import time
import sys


VALID_OPTIONS = [
    'sunrise',
    'sunset',
    'dawn',
    'dusk',
    'civil_dawn',
    'civil_dusk',
    'nautical_dawn',
    'nautical_dusk',
    'astronomical_dawn',
    'astronomical_dusk'
]


def get_tz_offset():
    offset = time.timezone if (time.localtime().tm_isdst == 0) else time.altzone
    return (offset / 60 / 60 * -1)


class solar(trigger.TriggerBase):
    def __init__(self, q, events, lat, lon):
        super().__init__(q, events)

        now = datetime.now()
        self.day = now.timetuple().tm_yday

        self.triggers = []
        for event in self.events:
            if not event['config'].lower() in VALID_OPTIONS:
                raise ValueError('`event` must be one of: {}'.format(', '.join(VALID_OPTIONS)))
            self.triggers.append({
                'name': event['name'],
                'config': event['config']
            })

        self.sun_calc = SunriseSunset(lat, lon, get_tz_offset())
        self.today_times = self.sun_calc.calculate(now)

    def start(self):
        while True:
            now = datetime.now().replace(second=0, microsecond=0, tzinfo=None)
            day = now.timetuple().tm_yday
            if day != self.day:
                self.today_times = self.sun_calc.calculate(now)
            for t in self.triggers:
                if self.today_times[t['config'].lower()] == now:
                    self.trigger(t['name'])
            time.sleep(60 - datetime.now().second)


sys.modules[__name__] = solar
