#! /usr/bin/env python

import copy, json, logtool, os, pprint, yaml
from addict import Dict

DEFAULT_KEY = "_default_"
INCLUDE_KEY = "_include_"

class CfgStack (object):
  # pylint: disable=too-few-public-methods

  @logtool.log_call
  def __init__ (self, fname):
    # pylint: disable=too-many-nested-blocks,too-many-branches
    self.fname = fname
    if os.path.isfile (fname + ".json"):
      self.read = json.loads (file (fname + ".json").read ())
    elif os.path.isfile (fname + ".yaml"):
      self.read = yaml.safe_load (file (fname + ".yaml"))
    elif os.path.isfile (fname + ".yml"):
      self.read = yaml.safe_load (file (fname + ".yml"))
    else:
      raise ValueError ("CfgStack: Canot find file for: %s" % fname)
    if not isinstance (self.read, dict):
      raise ValueError ("CfgStack: %s -- object is not a dict" % fname)
    stack = [self.read,]
    for d in stack:
      include = d.get (INCLUDE_KEY, [])
      if isinstance (include, list):
        for f in include:
          if isinstance (f, basestring):
            for k, v in CfgStack (f).data.items ():
              l = d.get (k)
              if isinstance (l, dict):
                if isinstance (v, dict):
                  n = copy.deepcopy (v)
                  n.update (l)
                  d[k] = n
              else:
                d[k] = v
        d.pop (INCLUDE_KEY, None)
      default = d.get (DEFAULT_KEY, {})
      if isinstance (default, dict):
        for k, v in d.items ():
          if isinstance (v, dict):
            n = copy.deepcopy (default)
            n.update (v)
            d[k] = n
        d.pop (DEFAULT_KEY, None)
      for k, v in d.items ():
        if isinstance (v, dict):
          stack.append (v)
    self.data = Dict (self.read)

  @logtool.log_call
  def __repr__ (self):
    return yaml.dump (self.data.to_dict (), width = 70, indent = 2,
                      default_flow_style = False)

  @logtool.log_call
  def __str__ (self):
    return pprint.pformat (self.data.to_dict ())
