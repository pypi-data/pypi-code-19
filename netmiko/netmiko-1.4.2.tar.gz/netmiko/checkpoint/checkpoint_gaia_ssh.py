from __future__ import unicode_literals
from netmiko.base_connection import BaseConnection


class CheckPointGaiaSSH(BaseConnection):
    """
    Implements methods for communicating with Check Point Gaia
    firewalls.
    """
    def session_preparation(self):
        """
        Prepare the session after the connection has been established.

        Set the base prompt for interaction ('>').
        """
        self._test_channel_read()
        self.set_base_prompt()
        self.disable_paging(command="set clienv rows 0\n")

    def config_mode(self, config_command=''):
        """No config mode for Check Point devices."""
        return ''

    def exit_config_mode(self, exit_config=''):
        """No config mode for Check Point devices."""
        return ''
