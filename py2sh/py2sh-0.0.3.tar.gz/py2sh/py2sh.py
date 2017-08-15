import re
import sys
import inspect
from functools import wraps
import helpstr
#Matches dictionary definitions of integer or string values
#                Match key            String Values         Numerical Values   Exponents
# kwargs_words = "([A-z]+[A-z0-9_]*)\ *\=(?:\"|\')(.+)(?:\"|\')"

# PLEASE READ BELOW
# It took bloodshed to carve these regexes out of characterspace^(len_regex) possibilities
kwargs_words = "([A-z]+[A-z0-9_]*)\ *\=(.+)"
kwargs_numbers = "([A-z]+[A-z0-9_]*)\ *\=(\-*[0-9]*\.*[0-9]+(?:e\-*\d+)*)"

re_kwargs_words = re.compile(kwargs_words)
re_kwargs_numbers = re.compile(kwargs_numbers)

args= "(\-*[0-9]*\.*[0-9]+)(e\-*\d+)|(.+)"

re_args = re.compile(args)


def numread(string):
  try:
    return int(string)
  except ValueError:
    try:
        return float(string)
    except ValueError:
        return string
def boolread(string):
  if string=="False":
    return False
  if string=="None":
    return None
  if string=="True":
    return True

  return string
def matchany_or_last(regex, string):
    match_first = regex +"\ *\,\ *"
    match_any = regex
    match_last =  "\ *\,_\ *" + regex

    re_match_first = re.compile(match_first)
    re_match_any = re.compile(match_any)
    re_match_last = re.compile(match_last)

    firsts = re_match_first.findall(string)
    string = re_match_first.sub('', string)

    anys = re_match_any.findall(string)
    string = re_match_any.sub('', string)

    lasts = re_match_last.findall(string)
    string = re_match_last.sub('', string)

    total = []
    total.extend(firsts)
    total.extend(anys)
    total.extend(lasts)
    return total, string

def _collectkwargs(argv):
  words, string = matchany_or_last(kwargs_words, argv)
  numbers, _ = matchany_or_last(kwargs_numbers, string)
  total = []
  total.extend(words)
  total.extend(numbers)
  ret = dict(total)
  for k in ret.keys():
      ret[k] = numread(ret[k])
      ret[k] = boolread(ret[k])
  return ret, string

def collectkwargs(argv):
    m, _ = _collectkwargs(argv)
    return m

def collectargs(argv):
  total = re_args.findall(argv)
  total = map(lambda x:  ''.join(list(x)), total)
  total = map(lambda x: numread(x), total)
  total = map(lambda x: boolread(x), total)
  return total

def parseargs(argc):
  kwargs, string = _collectkwargs(argc)
  args = collectargs(string)
  return kwargs, args

class shify:
  def __init__(self, *args, **kwargs):
    self.args = args
    self.kwargs = kwargs

  def __call__(self, func):
    name = self.kwargs.pop("name", "__imported__") 
    cli = self.kwargs.pop("cli", "never")
    tocontinue = name =="__main__" or cli=="allways"
    if not tocontinue:
        return func
    _shify(func, *self.args, **self.kwargs)

def _shify(f, 
        string='', 
        name="__imported__", 
        usage=None,
        includes=[],
        _debug=False, **kwargs):
  if string=='' and len(sys.argv) >= 1:
      string = sys.argv[1:]
  elif string != '' and isinstance(string, str):
      string = [string]
      return Exception("No string passed")
  """
  This is a micro argparse for turning any
  python function into a bash script.

  For scientists who are busy and need
  to throw something together quickly

  Handles strings and integers
  as kwargs and args
  """

  results=map(parseargs, string)
  kwargs = {}
  args = []
  visited = set()

  for kwarg, arg in results:
    for k, v in kwarg.iteritems():
      if k in kwargs and not k in visited:
        kwargs[k] = [kwargs[k], v]
        visited.add(k)
      elif k in kwargs and k in visited:
        kwargs[k] += [v]
      elif not k in kwargs:
        kwargs[k] = v

    args.extend(arg)

  if "help" in args or "help" in kwargs:
    if includes:
        help_args, help_kwargs = helpstr.helpstr(f, *includes)
    else:
        help_args, help_kwargs = helpstr.helpstr(f)

    pre = "      "
    print "usage: {}".format(f.__name__)
    if usage: #(I say let it fail:) and isinstance(help_kwargs["func_usage"], str):
        print pre+usage
        print pre +"-"*len(usage)

    print pre+"[help]"
    for arg in help_args:
        print pre+"[{}]".format(arg)

    for k,v in help_kwargs:
         print pre+"[{}={}]".format(k,v)

    if "help" in args:
        args.pop(args.index("help"))
    else:
        del kwargs["help"]
    return

  args = list(args)
  if _debug:
    print args
    print kwargs

  return f(*args, **kwargs)

def demo_2(g=6, h=7):
    print g,h


@shify(name=__name__,
       includes=[demo_2],
       usage="A py2sh demo")
def py2sh_demo(a, b, c=1, d= 2,*args, **kwargs):
    print args
    print kwargs
