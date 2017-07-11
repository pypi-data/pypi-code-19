from timeit import timeit
from subprocess import run, PIPE
from jdatetime import date

from collections import deque


d = deque((range(10)))
l = list(range(10))

t0 = timeit("""
d.appendleft(0)
list(d)
""", """
""", globals=globals(), number=10**4)
print(t0)

t1 = timeit("""
l.append(0)
l.reverse()
""", """
""", globals=globals(), number=10 **4)
print(t1)

print(t1 / t0)