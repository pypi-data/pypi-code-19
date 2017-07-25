# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Nicolas Hernandez 2017
# 
# The current class is used to store the data and the evaluation of data token given a grammar step 
#
# dict as key of set or dict     https://stackoverflow.com/questions/13264511/typeerror-unhashable-type-dict
#
# 
# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
import logging
from pprint import pprint, pformat
import ply.yacc as yacc

from pyrata.lexer import *
from pyrata.semantic_step_parser import *
import pyrata.compiled_pattern_re


# """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class CompiledData(object):
  
  compiledData = dict ()        # token (i.e. a dict) -> pattern (i.e. a string) -> evaluation (a bool)
                                # e.g. pos="DT" {'raw': 'The', 'pos': 'DT'}

  dictList = list ()            # data

  def __init__(self, **kwargs):
    if 'data' in kwargs.keys():
      self.dictList = kwargs['data']

  # """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  def get(self, token, step, **kwargs):
    """
    """
    return self.compiledData[key][step]

  # """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  def has_key(self, key, **kwargs):
    """
    """
    return frozenset(key.items()) in self.compiledData
    #return key in self.compiledData

  # """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  def has_(self, key, step, **kwargs):
    """
    TODO
    """
    return frozenset(key.items()) in self.compiledData
    #return key in self.compiledData
    
  # """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
  def __repr__(self):
    return '<pyrata.CompiledData object; \n' #\t="'+str(self.)+      '"\n\tends_wi_data="'+str(self.)+      '"\n\tlexicon="'+str(self.getLexer().lexer.lexicons.keys())        +'"\n\tpattern_steps="\n'+  pformat(self.getLexer().lexer.pattern_steps)+      '\n">'


# if __name__ == '__main__':
#   from nltk.corpus import brown
#   brown_sents = brown.sents()
#   import nltk
#   brown_pos_tag_sents = [nltk.pos_tag(sentence) for sentence in brown_sents[:1000]] 

#   print (brown_pos_tag_sents[0])
