
class ASPProcessor(EventThread):
  rPointXY = re.compile(r'point\(([0-9.]+),([0-9.]+)\)')
  def __init__(self, **kwargs):
    self.frontend = kwargs['frontend']
    del(kwargs['frontend'])
    self.sugarout = kwargs['sugarout']
    del(kwargs['sugarout'])
    EventThread.__init__(self, **kwargs)
    self.loadBaseProgram()

  def loadBaseProgram(self):
    # get special directives
    # #error #persistent #actions
    # write temporary file with the rest of the input
    hexfile = tempfile.NamedTemporaryFile(delete=False)
    rSpecial = re.compile(
      r'#(error|persistent|actions)\s(.*)\.')
    self.persistent = set()
    self.actions = set()
    errors = []
    try:
      with open(self.sugarout, 'rt') as f:
        for line in f:
          m = rSpecial.match(line)
          if m:
            type_, content = m.groups()
            if type_ == 'persistent':
              for item in content.split(','):
                self.persistent.add(item.strip())
            elif type_ == 'actions':
              for item in content.split(','):
                self.actions.add(item.strip())
            elif type_ == 'error':
              errors.append(content)
            else:
              assert(False and "we should handle all types above")
          else:
            hexfile.write(line)
      hexfile.close()
      if len(errors) > 0:
        raise Exception("errors in sugarizer! ({})".format(
          ', '.join(errors)))
      # load the HEX code
      edb, idb = dlvhex.loadSubprogram(hexfile.name)
      self.baseProgram = [edb, idb]
    finally:
      #print "keeping temporary hex input file " + hexfile.name
      os.unlink(hexfile.name)
      pass

    #print "Evaluating the program:" 
    #print dlvhex.getValue(self.baseProgram[1]) 
    #print "Evaluating wrt the following facts:" 
    #print dlvhex.getValue(self.baseProgramcompleteprog[0]) 

  def selectAnswerset(self, answersets):
    if len(answersets) == 0:
      raise RuntimeError("no answersets!")
    if len(answersets) != 1:
      warn("more than one answerset!")
      asSetOfStrings = map(lambda a: set(map(dlvhex.getValue, a)), answersets)
      for idx, answerset in enumerate(asSetOfStrings):
        if idx == 0:
          continue
        for idxPrev, answersetPrev in enumerate(asSetOfStrings):
          if idxPrev >= idx:
            break
          plus = answerset - answersetPrev
          minus = answersetPrev - answerset
          #warn('plus {}'.format(plus))
          #warn('minus {}'.format(minus))
          diff = map(lambda p: p+'+', plus) + map(lambda m: m+'-', minus)
          warn("#{} vs #{}: {}".format(idx, idxPrev, ', '.join(sorted(diff))))
      for idx, answerset in enumerate(answersets):
        warn("Full Answer #{}: {}\n".format(idx, dlvhex.getValue(answerset)))
      raise RuntimeError("more than one answerset!")
    return answersets[0]

  def checkForASPErrors(self, answerset):
    # check for errors
    error = False
    for atom in answerset:
      atuple = dlvhex.getTupleValues(atom)
      if len(atuple) == 2 and atuple[0] == 'error':
        warn("ASP ERROR: {}".format(repr(atuple[1])))
        error = True
    if error:
      raise RuntimeError("encountered ASP error(s)!")

  def showPredicates(self, answerset, preds):
    # this function is for debugging
    predcollection = {}
    for atom in answerset:
      atuple = dlvhex.getTupleValues(atom)
      pred = atuple[0]
      if pred in preds:
        if pred in predcollection:
          predcollection[pred].append( atuple[1:] )
        else:
          predcollection[pred] = [ atuple[1:] ]
    for pred, extension in predcollection.iteritems():
      #warn(repr(extension))
      warn("{}: {}".format(pred, ", ".join(map(lambda ext: "/".join(ext), extension))))

  def enqueueSoftEvents(self, actions):
    '''
    find soft events and execute them
    return unhandled actions
    '''
    ret = []
    for a in actions:
      aname, aargs, ser = a[0], a[1:-1], a[-1]
      if aname == 'softEvent':
        name = aargs[0]
        self.queue.put_front(MyEvent('softevent', name))
      else:
        ret.append(a)
    return ret

