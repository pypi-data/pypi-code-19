
  def selectAnswerset(self, answersets):
    if len(answersets) == 0:
      raise RuntimeError("no answersets!")
    if len(answersets) != 1:
      if self.mode == 'acceptmultipleanswersets':
        return answersets[0]
      warn("more than one answerset!")
      asSetOfStrings = map(lambda a: set(map(str, a)), answersets)
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
        warnVerbose("Full Answer #{}: {}\n".format(idx, str(answerset)))
      raise RuntimeError("more than one answerset!")
    return answersets[0]

  def checkForASPErrors(self, answerset):
    # check for errors
    error = False
    for atom in answerset:
      atuple = getTupleValues(atom)
      if len(atuple) == 2 and atuple[0] == 'error':
        warn("ASP ERROR: {}".format(repr(atuple[1])))
        error = True
    if error:
      raise RuntimeError("encountered ASP error(s)!")

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

