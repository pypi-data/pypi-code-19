import time
from .timer import Timer


class TimeOut(Timer):
    """
    Helper to checks if an elapsed time has been reached.
    """

    def __init__(self, timeout):
        """

        :param timeout: duration (in seconds) until the TimeOut object expires
        """
        self._timeout = timeout
        Timer.__init__(self)

    def isExpired(self):
        """
        Checks if the TimeOut has expired.

        example:
        # wait max 60 seconds until my system has started and check every seconds
        timeout = TimeOut(60)
        while not self._isStarted() and not timeout.isExpired():
            time.sleep(1)

        :return: True if expired, False otherwise
        """
        return self.getElapsedSeconds() > self._timeout

    def waitUntilExpired(self):
        """
        Waits until the TimeOut has expired.

        example:
        while True:
            timeout = TimeOut(self._pollingIntervalInSeconds)
            self._performLengthyOperation()
            timeout.waitExpired()
        """
        remaining = self._timeout - self.getElapsedSeconds()
        if remaining >= 0:
            time.sleep(remaining)

    @staticmethod
    def waitUntilCondition(condition, timeout, evaluateInterval = 1):
        """
        evaluate a condition (lambda) multiple times until it is statisfied or a timeout occurs
        :param condition: the lambda expression to evaluate
        :param timeout: the max time to wait (in seconds) until the condition is satisfied
        :param evaluateInterval: the interval (in seconds) between to evaluation of the condition
        :return: true if the condition is satisfed before the timeout expired, false otherwise
        """
        timeout = TimeOut(timeout)
        satisfied = False
        while not satisfied and not timeout.isExpired():
            satisfied = condition()
            if not satisfied:
                time.sleep(evaluateInterval)

        if not satisfied:  # if not satisfied after timeout, let's try a last time
            return condition()
        else:
            return True
