import random

def randint(a,b):
    """Return random integer in range [a, b], including both end points. Intrinsically better numbers will be returned more often."""
    numbers = list(range(min(a,b), max(a,b)+1))
    return random.choice(numbers+multiples(numbers, 3)+multiples(numbers, 5)+multiples(numbers, 15))

def multiples(coll, div):
    """Returns all of the items in coll which are multiples of div"""
    return [x for x in coll if x%div==0]
