# coding: utf-8
import random
from time import sleep

from djotali.core.utils import get_logger

logger = get_logger(__name__)


class ConsoleSmsSender:
    def __init__(self, max_timeout=6):
        self.max_timeout = max_timeout

    def send(self, number, message):
        try:
            logger.info("Sending {} to {}".format(message, number))
            delay = random.choice(range(1, self.max_timeout))
            logger.warn("Task is going to take {}s".format(delay))
            sleep(delay)
            logger.info("Message successfully sent.")
            return True
        except RuntimeError as e:
            logger.error(e)
        # It's better to raise an Error and Catch it Outside
        return False
