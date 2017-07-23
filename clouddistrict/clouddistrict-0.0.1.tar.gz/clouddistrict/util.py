'''
towniesim.util
==============

Utility functions
'''
import re
from random import uniform, randint, seed, gauss

RE_PERCENT = re.compile(r'(\d+(?:\.\d*)?)%?\s*(.*)')


def initialize_seed(n):
    '''
    Initialize seed for deterministic output.
    '''
    if n is None:
        seed()
    else:
        seed(n)


def nds(number_dice, sides):
    '''
    short for number_dice_sides
    Another convenience dice roller like ``nds(3, 6)`` for 3d6.
    '''
    summed = 0
    for i in range(number_dice):
        summed += randint(1, sides)
    return summed


def roll(s):
    '''
    Roll dice like ``roll('3d6')``
    '''
    s = s.strip().lower()
    num, sides = s.split('d')
    return nds(int(num), int(sides))


def percents_from_list(lst):
    '''
    Utility function to derive percents and values for ``random_from_list``
    '''
    probs = {}
    for item in lst:
        match = RE_PERCENT.match(item)
        if match is None and len(lst) == 1:
            return item
        elif match is None:
            raise ValueError('In list of percents, {} doesnt match pattern '
                             'like "50% elf"'.format(item))
        percent = float(match.group(1))
        value = match.group(2)
        probs[value] = percent
    return probs


def random_from_list(lst):
    '''
    This will pick a random item from a list that matches string patterns like:
    ['50% human', '45% elf', '5% dwarf']
    It can also work with arbitrary numbers like:
    ['5 human', '1 elf', '1 dwarf']
    Or:
    [('human', 5), ('elf', 1)]
    or:
    {'human': 5, 'elf': 1}

    This is used so configs can be created and parsed with configobj like:
    tavern_races=50% human, 30% elf, 20% dwarf
    '''
    if isinstance(lst, dict):
        lst = list(lst.items())
    if lst and isinstance(lst[0], (list, tuple)):
        probs = sorted(lst, key=lambda x: x[1], reverse=True)
    else:
        probs = sorted(percents_from_list(lst).items(), key=lambda x: x[1],
                       reverse=True)
    inc = []
    summ = 0
    # build this list so we can incrementally check if rand < summ
    for value, num in probs:
        summ += num
        inc += [(value, summ)]

    total = sum(x[1] for x in probs)
    rand = uniform(0, total)
    for value, num in inc:
        if rand <= num:
            return value
    return value


def le_switch(d, n):
    for i, v in sorted(d.items()):
        if n <= i:
            return v
    return None


def even_switch(d, n):
    summ = 0
    inc = []
    if isinstance(d, dict):
        lst = d.items()
    else:
        lst = d
    for num, value in lst:
        summ += num
        inc += [(value, summ)]
    for value, num in inc:
        if n <= num:
            return value
    return None


def gauss_mm(mu, sigma, mn=None, mx=None):
    g = gauss(mu, sigma)
    if mx is not None:
        g = min(g, mx)
    if mn is not None:
        g = max(g, mn)
    return g
