#!/usr/bin/env python
# -*- coding: utf-8 -*-

# imports
import os

def ensure_dir(directory):
    """ensure a directory exists"""
    if os.path.exists(directory):
        assert os.path.isdir(directory)
        return directory
    os.makedirs(directory)
    return directory
