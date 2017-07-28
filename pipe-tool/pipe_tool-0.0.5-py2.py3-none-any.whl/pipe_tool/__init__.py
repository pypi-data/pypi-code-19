from functools import reduce


class Map():

    def __init__(self, func):
        self.func = func

    def __ror__(self, left):
        return map(self.func, left)

class Filter():

    def __init__(self, func):
        self.func = func

    def __ror__(self, left):
        return filter(self.func, left)

class Reduce():

    def __init__(self, func):
        self.func = func

    def __ror__(self, left):
        return reduce(self.func, left)

class List():

    def __ror__(self, left):
        return list(left)



def main():
    print(range(10) | Map(lambda x: x + 1) | List())
    print(range(10) | Filter(lambda x: x % 2 == 1) | List())
    print(range(10) | Reduce(lambda x,y: x + y))

if __name__ == '__main__':
    main()
