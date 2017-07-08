from timeit import timeit
from subprocess import run, PIPE
from jdatetime import date


a = 1
b = 2
c = 3

x, y = (a + c, b + c)

a += c
b += c

assert x, y == (a, b)

t0 = timeit("""
tuple(i for i in range(10))
""", """
""", globals=globals(), number=10**6)
print(t0)

t1 = timeit("""
[i for i in range(10)]
""", """
""", globals=globals(), number=10 **6)
print(t1)

print(t1 / t0)