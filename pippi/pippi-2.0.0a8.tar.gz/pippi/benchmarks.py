""" Run this with `python -m pippi.benchmarks` to see some 
    timing information for synthesis etc.
"""
import timeit

init = """\
from pippi import oscs
osc = oscs.Osc()
"""

basic = """\
from pippi import oscs
osc = oscs.Osc()
out = osc.play(44100)
"""

if __name__ == '__main__':
    init_time = timeit.timeit(stmt=init, number=1000)
    print('init 1000x...')
    print(round(init_time, 2), init)

    print('1000 1 second renders w/default settings...')
    basic_time = timeit.timeit(stmt=basic, number=1000)
    print(round(basic_time, 2), basic)
