import math

__author__ = 'Michael'

MATH_VARS = dict(math.__dict__)
for key in list(MATH_VARS.keys()):
    if key.startswith("__"):
        MATH_VARS.pop(key)

INTRO_STR = "Welcome to Michael Kim's Py-Calculator!\n"
