"""
Tools to ease the homesickness of lisp programmers.
"""
from functools import reduce


def compose(*functions):
  """Compose together multiple functions"""
  def compose2(f, g):
    return lambda x: f(g(x))
  return reduce(compose2, reversed(functions), lambda x: x)


def channel(v, funList):
  """Pass the first argumnet to the function
  composed from a list of functions"""
  composedFun = compose(*funList)
  return composedFun(v)
