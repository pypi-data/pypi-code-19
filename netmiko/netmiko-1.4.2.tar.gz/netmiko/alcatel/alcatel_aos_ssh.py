"""Alcatel-Lucent Enterprise AOS support (AOS6 and AOS8)."""
from __future__ import print_function
from __future__ import unicode_literals
from netmiko.cisco_base_connection import CiscoSSHConnection


class AlcatelAosSSH(CiscoSSHConnection):
    """Alcatel-Lucent Enterprise AOS support (AOS6 and AOS8)."""
    def session_preparation(self):
        # Prompt can be anything, but best practice is to end with > or #
        self._test_channel_read(pattern=r'[>#]')
        self.set_base_prompt()

    def check_enable_mode(self, *args, **kwargs):
        """No enable mode on AOS"""
        pass

    def enable(self, *args, **kwargs):
        """No enable mode on AOS"""
        pass

    def exit_enable_mode(self, *args, **kwargs):
        """No enable mode on AOS"""
        pass

    def check_config_mode(self, *args, **kwargs):
        """No config mode on AOS"""
        pass

    def config_mode(self, *args, **kwargs):
        """No config mode on AOS"""
        return ''

    def exit_config_mode(self, *args, **kwargs):
        """No config mode on AOS"""
        return ''
