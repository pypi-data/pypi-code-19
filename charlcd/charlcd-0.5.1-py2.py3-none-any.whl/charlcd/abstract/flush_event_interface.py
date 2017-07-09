#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=I0011,R0913,R0902
"""Interface for buffered flush events
"""


class FlushEvent(object):
    """Required functions for flush events"""
    def pre_flush(self, buffer):
        """called before buffered flush"""
        raise NotImplementedError('pre_flush not implemented')

    def post_flush(self, buffer):
        """called after flush"""
        raise NotImplementedError('post_flush not implemented')
