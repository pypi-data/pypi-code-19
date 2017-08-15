#! /usr/bin/env python

import copy, json, logtool, os, pprint, yaml
from addict import Dict

DEFAULT_KEY = "_default_"
INCLUDE_KEY = "_include_"

class CfgStack (object):
  # pylint: disable=too-few-public-methods

  @logtool.log_call
  def __init__ (self, fname, no_defaults = False):
    # pylint: disable=too-many-nested-blocks,too-many-branches
    self.read = self._load (fname)
    self._do_includes (no_defaults)
    self._do_defaults ()
    self.data = Dict (self.read)

  @logtool.log_call
  def _load (self, fname):
    if not isinstance (fname, basestring):
      raise ValueError ("Name: %s is not a string" % fname)
    # FIXME: Be smarter about relative paths
    if os.path.isfile (fname + ".json"):
      return json.loads (file (fname + ".json").read ())
    elif os.path.isfile (fname + ".yaml"):
      return yaml.safe_load (file (fname + ".yaml"))
    elif os.path.isfile (fname + ".yml"):
      return yaml.safe_load (file (fname + ".yml"))
    else:
      raise IOError ("CfgStack: Cannot find file for %s in %s"
                     % (fname, os.getcwd ()))

  @logtool.log_call (log_args = False, log_rc = False)
  def _meld (self, master, slave):
    if master is None:
      return slave
    if isinstance (master, dict) and isinstance (slave, dict):
      new = copy.deepcopy (slave)
      # FIXME: should be a deep merge
      new.update (master)
      return new
    return master

  @logtool.log_call (log_args = False, log_rc = False)
  def _do_nesting (self, d, stack):
    for _, v in d.items ():
      if isinstance (v, dict):
        stack.append (v)

  @logtool.log_call (log_args = False, log_rc = False)
  def _do_includes (self, no_defaults):
    stack = [self.read,]
    for d in stack:
      include = d.get (INCLUDE_KEY, [])
      if isinstance (include, list):
        for f in include:
          for k, v in CfgStack (f, no_defaults = no_defaults).read.items ():
            d[k] = self._meld (d.get (k), v)
        d.pop (INCLUDE_KEY, None)
      self._do_nesting (d, stack)

  @logtool.log_call
  def _do_defaults (self):
    stack = [self.read,]
    for d in stack:
      default = d.get (DEFAULT_KEY, {})
      if isinstance (default, dict):
        for k, v in d.items ():
          if isinstance (v, dict):
            d[k] = self._meld (v, default)
        d.pop (DEFAULT_KEY, None)
      self._do_nesting (d, stack)

  @logtool.log_call
  def as_yaml (self):
    return yaml.dump (self.data.to_dict (), width = 70, indent = 2,
                      default_flow_style = False)

  @logtool.log_call
  def as_json (self, indent = 2):
    return json.dumps (self.read, indent = indent)

  @logtool.log_call
  def as_pretty (self):
    return pprint.pformat (self.data.to_dict ())
