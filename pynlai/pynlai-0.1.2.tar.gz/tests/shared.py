# -*- coding: utf-8 -*-

'''
shared
------

shared module for pynlai unit tests
'''


import en_core_web_sm as en


# loading the nl model is expensive, so just do it once
nlp = en.load()
