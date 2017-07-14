#!/usr/bin/env python3
# coding: utf-8
'''
Simple module aiming to ease code production
'''
from .devscripts import retry
from .logs import simple_logger

__all__ = [
    'retry',
    'simple_logger',
]
