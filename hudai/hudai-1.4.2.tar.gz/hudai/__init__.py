"""
Python wrapper for HUD.ai data access layer

Example usage:

from hudai.client import HudAi

client = HudAi()
"""

__version__ = '1.4.2'

class HudAiError(Exception):
    def __init__(self, message=None, type='validation_error'):
        super(HudAiError, self).__init__(message)

        self._message = message
        self.type = type
