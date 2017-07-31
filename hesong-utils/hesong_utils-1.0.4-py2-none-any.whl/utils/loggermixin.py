# -*- coding: utf-8 -*-

import logging

__all__ = ['LoggerMixin']


class LoggerMixin:
    """Mixin Class provide a :attr:`logger` property
    """

    @classmethod
    def get_logger(cls):
        """`logger` instance.

        :rtype: logging.Logger

        logger name format is `ModuleName.ClassName`
        """
        try:
            name = '{0.__module__:s}.{0.__qualname__:s}'.format(cls)
        except AttributeError:
            name = '{0.__module__:s}.{0.__name__:s}'.format(cls)
        return logging.getLogger(name)

    @property
    def logger(self):
        """`logger` instance.

        :rtype: logging.Logger

        logger name format is `ModuleName.ClassName`
        """
        return self.get_logger()
