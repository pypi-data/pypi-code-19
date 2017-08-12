from datetime import datetime
import bluetooth
from bluetooth.btcommon import is_valid_address
from bibliopixel.remote import trigger
import time
import sys


BASE_EVENT = {
    'state': True,
    'condition': 'all',
    'last_state': False
}


def check_all(last, cur, state):
    if last == cur:
        return False

    return (all(cur) == state)


def check_any(last, cur, state):
    if last == cur:
        return False

    for i in range(len(last)):
        if state:
            if not last[i] and cur[i]:
                return True
        else:
            if last[i] and not cur[i]:
                return True


CONDITIONS = {
    'all': check_all,
    'any': check_any
}


class bt_proximity(trigger.TriggerBase):
    def __init__(self, q, events, check_interval=30, lookup_timeout=3):
        super().__init__(q, events)
        self.check_interval = check_interval
        self.lookup_timeout = lookup_timeout
        self.states = {}
        self.checks = []
        for event in self.events:
            event = dict(BASE_EVENT, **event)
            if 'address' not in event:
                raise ValueError('bt_proximity events require the `address` parameter')
            if 'name' not in event:
                raise ValueError('bt_proximity events require the `name` parameter')
            if isinstance(event['address'], str):
                event['address'] = [event['address']]
            if event['condition'].lower() not in CONDITIONS.keys():
                raise ValueError('`condition` must be one of: {}'.format(', '.join(CONDITIONS.keys())))

            for mac in event['address']:
                if not is_valid_address(mac):
                    raise ValueError('bt_proximity: {} is not a valid mac address'.format(mac))
                self.states[mac] = False

            self.checks.append(event)

        # Get initial device and check states
        self.states = self.check_devices()
        check_states = self.get_check_states(self.states)
        for i, c in enumerate(self.checks):
            c['last_state'] = check_states[i]

    def check_devices(self):
        states = {}
        for mac in self.states.keys():
            states[mac] = (bluetooth.lookup_name(mac, self.lookup_timeout) is not None)
        return states

    def get_check_states(self, states):
        result = []
        for c in self.checks:
            sub_states = [states[mac] for mac in c['address']]
            result.append(sub_states)
        return result

    def start(self):
        while True:
            now = time.time()
            states = self.check_devices()
            check_states = self.get_check_states(states)
            for i, c in enumerate(self.checks):
                state = check_states[i]
                check_func = CONDITIONS[c['condition'].lower()]
                if check_func(c['last_state'], state, c['state']):
                    self.trigger(c['name'])
                c['last_state'] = state
            self.states = states
            sleep = self.check_interval - (time.time() - now)
            if sleep > 0:
                time.sleep(sleep)


sys.modules[__name__] = bt_proximity
