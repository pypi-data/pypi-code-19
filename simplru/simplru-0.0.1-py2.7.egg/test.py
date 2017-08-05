from simplru import lru_cache

@lru_cache(maxsize=2)
def f(x):
    return(x**2)

for i in [2,2,2,2,2,2,3,3,3,3, 4, 4, 5, 5, 5, 6, 6]:
    print(f(i))
    print(f.cache_info())
