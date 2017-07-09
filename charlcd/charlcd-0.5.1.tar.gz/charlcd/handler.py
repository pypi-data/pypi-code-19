#!/usr/bin/python3
# pylint: disable=I0011,R0913,R0902
"""CharLCD handler"""

from message_listener.abstract.handler_interface import Handler as HandlerInterface
import charlcd.abstract.lcd as lcd


class Handler(HandlerInterface):
    """CharLCD handler - best used with buffered CharLCD
    supports 3 events: lcd.cmd, lcd.char and lcd.content
    """
    def handle(self, message):
        handled = False
        if message is not None and 'event' in message:
            if message['event'] == 'lcd.cmd':
                self.worker.drv.command(
                    message['parameters']['data'],
                    message['parameters']['enable']
                )
                handled = True

            if message['event'] == 'lcd.char':
                self.worker.drv.write(
                    message['parameters']['data'],
                    message['parameters']['enable']
                )
                handled = True

            if message['event'] == 'lcd.content':
                idx = 0
                for row in message['parameters']['content']:
                    self.worker.write(row, 0, idx)
                    idx += 1

                if self.worker.display_mode == lcd.DISPLAY_MODE_BUFFERED:
                    self.worker.flush()
                handled = True

        return handled
