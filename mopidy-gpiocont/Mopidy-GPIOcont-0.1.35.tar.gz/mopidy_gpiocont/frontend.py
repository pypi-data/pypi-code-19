import pykka
import logging

from mopidy import core

logger = logging.getLogger(__name__)
logger.debug("GPIOcont: Frontend.py called")

class GPIOcont(pykka.ThreadingActor, core.CoreListener):

    def __init__(self, config, core):
        super(GPIOcont, self).__init__()
        self.core = core
        from .input_gpio import input_GPIO
        self.input = input_GPIO(self, config['gpiocont'])



    def input_event(self, input_event):
        logger.error("GPIOcont: Input event arrived at frontend.")

