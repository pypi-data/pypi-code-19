#!/usr/bin/env python
#
# Author: Jingyu Wang <badpasta@gmail.com>
# 
# Environment:
# -*- coding: utf-8 -*-
# Python by version 2.7.

import logging
import logging.config


class SmartLog:
    def __init__(self, target, logconfig):
        self.target = target
        self.config = logconfig
        logging.config.dictConfig(self.config)
        self.logger = logging.getLogger(self.target)

    def pushInfo(self, message):
        self.logger.info(message)

    def pushDebug(self, message):
        self.logger.debug(message)

    def pushError(self, message):
        self.logger.error(message)


