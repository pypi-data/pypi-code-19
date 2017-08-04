from datetime import datetime
from croniter import croniter
from bibliopixel.remote import trigger
import time


class crontab(trigger.TriggerBase):
    def __init__(self, q, configs):
        super().__init__(q, configs)

        self.crontabs = []
        for c in self.configs:
            tab = croniter(c['config'], datetime.now())
            self.crontabs.append({
                'name': c['name'],
                'tab': tab,
                'next': tab.get_next(datetime)
            })

    def start(self):
        while True:
            now = datetime.now()
            for c in self.crontabs:
                if c['next'] <= now:
                    self.trigger(c['name'])
                    c['next'] = c['tab'].get_next(datetime)
            time.sleep(60 - now.second)
