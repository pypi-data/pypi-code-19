#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os


def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)
