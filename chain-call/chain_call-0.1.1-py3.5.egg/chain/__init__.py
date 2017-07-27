from functools import partial
from inspect import signature


class Call():

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __getattr__(self, name):
        return Param(self.func, name)

    def parameters(self):
        return signature(self.func).parameters.keys()


class Param():

    def __init__(self, parent, name):
        self.parent = parent
        self.name = name

    def __call__(self, parm):
        parms = {}
        parms[self.name] = parm
        return Call(partial(self.parent, **parms))


def main():
    print("This is the chain-call module.")
    print("You can use it like this:")
    print("> Call(print).sep('.').end('\\n*****')(1,2,'aaa')")
    print()
    print("Also you can use it like this:")
    Call(print).sep('.').end('\n*****')(1, 2, 'aaa')
    print("> Call(len).parameters()")
    print(Call(len).parameters())


if __name__ == '__main__':
    main()
