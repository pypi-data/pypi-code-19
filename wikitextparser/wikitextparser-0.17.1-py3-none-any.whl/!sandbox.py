from itertools import count
from timeit import timeit
from subprocess import run, PIPE

from jdatetime import date

from collections import deque
from wikitextparser import ParserFunction, parse as wtp
from mwparserfromhell import parse as mwp

l = list(range(10000))

m1 = """
for n, i in enumerate(l[:]):
    pass
"""
m2 = """
n = len(l)
for n, i in enumerate(reversed(l)):
    n -= 1
    pass
"""
t1 = timeit(m1, number=10**3, globals=globals())
t2 = timeit(m2, number=10**3, globals=globals())
print(t1)
print(t2)
print(t1/t2)
