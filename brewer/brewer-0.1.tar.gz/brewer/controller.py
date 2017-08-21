import str116
from settings import relays
from slack import BrewerBot
import time
import omegacn7500
from terminaltables import AsciiTable

class Controller:
    def __init__(self):
        self.omega = omegacn7500.OmegaCN7500('/dev/ttyAMA0', 1) # port name, slave address
        self.slack = BrewerBot()

    def relay_status(self, relay_num):
        return str116.get_relay(relay_num)

    def set_relay(self, relay_num, state):
        str116.set_relay(relay_num, state)

    def pid_status(self):
        return {
            "pid_running": self.omega.is_running(),
            "sv": self.omega.get_setpoint(),
            "pv": self.omega.get_pv()
        }

    def pid(self, state):
        self._safegaurd_state(state)
        if state == 1:
            self.omega.run()
        else:
            self.omega.stop()
        return True


    def hlt(self, state):
        self._safegaurd_state(state)
        self.set_relay(relays["hlt"], state)
        return True

    def hlt_to(self, location):
        if location == "mash":
            self.set_relay(relays["hltToMash"], 1)
            return True
        elif location  == "boil":
            self.set_relay(relays["hltToMash"], 0)
            return True
        else:
            raise ValueError("Location unknown: valid locations are 'mash' and 'boil'")


    def rims_to(self, location):
        if location == "mash":
            self.set_relay(relays["rimsToMash"], 1)
            return True
        elif location == "boil":
            self.set_relay(relays["rimsToMash"], 0)
            return True
        else:
            raise ValueError("Location unknown: valid locations are 'mash' and 'boil'")

    def pump_status(self):
        return self.relay_status(relays["pump"])

    def pump(self, state):
        self._safegaurd_state(state)
        self.set_relay(relays['pump'], state)
        return True

    def _safegaurd_state(self, state):
        if not isinstance(state, int):
            raise ValueError("Relay State needs to be an integer, " + str(type(state)) + " given.")
        if state < 0 or state > 1:
            raise ValueError("State needs to be integer 0 or 1, " + str(state) + " given.")
        return True

    def sv(self):
        return float(self.omega.get_setpoint())

    def set_sv(self, temp):
        if not isinstance(temp, int) and not isinstance(temp, float):
            raise ValueError("Temp argument needs to be a float or integer, " + str(type(temp)) + " given")
        self.omega.set_setpoint(temp)
        return self.sv()

    def pv(self):
        return float(self.omega.get_pv())

    def watch(self):
        while self.pv() <= self.sv():
            time.sleep(2) # :nocov:

        self.slack.send("PV is now at " + str(self.pv()) + " f")
        return True

    def status_table(self):
        status = AsciiTable([
            ["Setting", "Value"],
            ["PID on?", str(self.pid_status()['pid_running'])],
            ["Pump on?", str(self.pump_status())],
            ["pv", str(self.pv())],
            ["sv", str(self.sv())]
        ])
        return status
