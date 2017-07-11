'''
Created on 15 Mar 2017

@author: desouslu
'''

class Deco(object):
    def __init__(self, factor):
        self.factor = factor

    def __call__(self, Cla):
        NewClass = Cla
        #def newfoo(self2, y):
         #   return self.factor*Cla.foo(y)
        def newfoo(self2, y):
            return self.factor+y
        NewClass.foo = newfoo
        return NewClass



@Deco(2)
class A(object):
    def foo(self, y):
        return y



a = A()

print(a.foo(3))