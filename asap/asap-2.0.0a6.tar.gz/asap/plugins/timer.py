from asap.core import api

import sys
import threading

def debug(msg):
  sys.stderr.write("D:"+msg+"\n")

class StartTimerAction(api.Action):
  '''
  Do.startTimer(name,delay) 2 mandatory arguments
  name is string
  delay is integer (milliseconds)
  '''
  def __init__(self, queue):
    self.queue = queue

  @property
  def interface(self):
    return ('startTimer', 2, 2)

  def execute(self, ainput):
    assert(len(ainput.inputs) == 2)
    name, millis = ainput.inputs
    millis = float(int(millis))
    class EventCreator:
      def __init__(self, queue, eventdata):
        self.queue = queue
        self.eventdata = eventdata
      def __call__(self):
        # enqueue event
        self.queue.append(api.Event(self.eventdata))
    debug("startTimer {} for {} ms".format(name, millis))
    t = threading.Timer(millis/1000.0, EventCreator(self.queue, api.Term('timer',[name])))
    t.start()

class Plugin(api.DoAPI, api.EventAPI):
  def __init__(self):
    api.EventAPI.__init__(self)

  def actions(self):
    if not self.queue:
      raise Exception('timer.Plugin.actions() can only be called after provding the queue via timer.Plugin.setQueue()')
    return [StartTimerAction(self.queue)]

