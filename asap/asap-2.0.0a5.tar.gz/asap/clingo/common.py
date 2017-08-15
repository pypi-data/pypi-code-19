
from asap.core import api

# this module is provided by clingo.so built using `scons pyclingo` in the potassco suite
import clingo

def termToClingoSym(term):
  '''
  convert Term to clingo.Function
  '''
  #debug("converting term '{}' to clingo.Function".format(repr(term)))
  if not isinstance(term, api.Term):
    raise Exception("termToClingoSym expected api.Term but got '{}'".format(repr(term)))
  ret = None
  if len(term.args) == 0:
    if isinstance(term.pred, int):
      ret = clingo.Number(term.pred)
    elif term.pred[0] == '"':
      ret = clingo.String(term.pred[1:-1])
    else:
      ret = clingo.Function(term.pred)
  else:
    ret = clingo.Function(term.pred, [termToClingoSym(x) for x in term.args])
  #debug("converted term '{}' to clingo.Function '{}'".format(repr(term), repr(ret)))
  return ret


def clingoSymToTerm(sym):
  '''
  convert clingo.Function to Term
  '''
  #debug("converting clingo.Function '{}' to Term".format(repr(fun)))
  assert(isinstance(sym, clingo.Symbol))
  if sym.type == clingo.SymbolType.Number:
    ret = api.Term(int(sym.number))
  elif sym.type == clingo.SymbolType.String:
    ret = api.Term('"'+sym.string+'"')
  elif sym.type == clingo.SymbolType.Function:
    ret = api.Term(sym.name, [clingoSymToTerm(x) for x in sym.arguments])
  else:
    raise Exception("cannot convert '{}' to Term!".format(repr(sym)))
  #debug("converted clingo.Function '{}' to Term '{}'".format(repr(sym), repr(ret)))
  return ret
