

  def configureEvent(self, evt):
    '''
    event handler for <Configure>
    (window resize or location change)
    '''
    self.eventq.put_once(MyEvent('resize'))

  def clear(self):
    def clearInternal(self):
      for i in self.items:
        self.canvas.delete(i)
      self.items = []
    self.drawq.put(lambda self_: clearInternal(self_))


class Persistence:
  def __init__(self, fluents):
    # load from file, if existing
    self.fluents = fluents
    # build a regex that recognizes fluents, with or without arguments
    fluents_regexes = map(lambda f: "({}(\(.*\))?)".format(f), self.fluents)
    self.rfluents = re.compile('|'.join(fluents_regexes))
    self.data = { 'sit':set(), 'val':set() }
    if len(fluents) > 0:
      try:
        with open('persistence.pickle', 'rb') as f:
          p = pickle.load(f)
          if not isinstance(p, dict):
            raise Exception("found pickle in wrong format!")
          if p['fluents'] != self.fluents:
            raise Exception("found pickle with wrong fluents {}!".format(p['fluents']))
          self.data = p['data']
      except Exception as e:
        # warn but ignore
        print "Warning:", str(e)

  def get(self):
    return (self.data['sit'], self.data['val'])
    
  def store(self, sit, val):
    if len(self.fluents) > 0:
      self.data = { 'sit': sit, 'val': set() }
      # store only those fluents that should be persistent!
      for fluent, value, t in val:
        if self.rfluents.match(fluent) != None:
          self.data['val'].add( (fluent, value, t) )
        else:
          #warnVerbose("fluent {} did not match re".format(fluent))
          pass
      #warnVerbose('storing persistence {} and {}'.format(self.fluents, self.data)) 
      with open('persistence.pickle', 'wb') as f:
        to_store = { 'fluents':self.fluents, 'data':self.data }
        pickle.dump(to_store, f)

