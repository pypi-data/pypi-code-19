from collections import deque
from bisect import bisect_left, insort

def rolling_median(iterable, K):
    # taking iterator so it works on sequences and generators
    it = iter(iterable)

    # a deque has optimized access from its endpoints
    # we consume and store the first K values
    deq = deque(next(it) for _ in range(K))

    # initialize the sorted array
    sor = sorted(deq)

    # index of median in sorted list
    i = (K+1)//2 -1

    yield sor[i]
    for r in it:
        # `deq` keeps track of chrological order
        out = deq.popleft()
        deq.append(r)
        # `sor` keeps track of sortedness
        sor.pop(bisect_left(sor, out))
        insort(sor, r)
        yield sor[i]

