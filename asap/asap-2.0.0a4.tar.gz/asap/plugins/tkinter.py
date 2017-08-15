from asap.core import api

from tkinter import font
import tkinter as tk

import logging
import queue
import threading, sys, os, traceback

def debug(msg):
  #sys.stderr.write("D:"+msg+"\n")
  pass

def warn(msg):
  sys.stderr.write("W:"+msg+"\n")


class KeyboardHandler(api.EventAPI):
  def __init__(self, root):
    api.EventAPI.__init__(self)
    self.root = root

  def setQueue(self, queue):
    api.EventAPI.setQueue(self, queue)
    self.root.bind_all('<KeyPress>', self.keyPressEvent)

  def keyPressEvent(self, evt):
    if not self.queue:
      warn("tkinter.KeyboardHandler ignoring keyPressEvent because no queue registered")
      return
    debug('keyPressEvent {}/{}/{}'.format(evt.char, evt.keysym, evt.keycode))
    if evt.char == evt.keysym:
      # normal character
      self.queue.append(api.Event(api.Term.fromNestedTuple(('keyboard', ('normal', '"{}"'.format(evt.char))))))
    else:
      self.queue.append(api.Event(api.Term.fromNestedTuple(('keyboard', ('special', '"{}"'.format(evt.keysym))))))

class WindowHandler(api.DoAPI):
  def __init__(self, root):
    #api.DoAPI.__init__(self)

    self.root = root
    self.items = []
    self.drawq = queue.Queue()

    #self.root.geometry("800x600")
    self.root.geometry("1200x800")
    self.XMUL = 25
    self.YMUL = 25
    self.XOFFSET = self.XMUL
    self.YOFFSET = self.YMUL

    self.imageCache = {}

    self.main = tk.Frame(self.root)
    self.main.pack(fill=tk.BOTH, expand=tk.YES)
    self.canvas = tk.Canvas(self.main, bg="grey")
    self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
    self.FONT = font.Font(family = 'Courier', size = self.YMUL-1)

    self.pixel_viewport = (1,1)
    self.updateViewport()

    self.my_actions = [
      DrawRectangleAction(self),
      DrawImageAction(self),
      DrawTextAction(self),
      DrawTextCenteredAction(self)]

    self.root.bind('<<DrawingUpdate>>', lambda x: self.drawingUpdate(x))

  def actions(self):
    return self.my_actions

  def beforeExecution(self):
    drawTextCentered = self.my_actions[3]
    drawTextCentered.resetCursor()

  def afterExecution(self):
    self.finishDrawing()

  def finishDrawing(self):
    # see http://stackoverflow.com/questions/7141509/tkinter-wait-for-item-in-queue/7198960#7198960
    self.root.event_generate('<<DrawingUpdate>>', when='tail')

  def updateViewport(self):
    self.canvas.update_idletasks() # required to make winfo_* return correct values
    self.pixel_viewport = (self.canvas.winfo_width(), self.canvas.winfo_height())
    self.viewport = (
      (self.pixel_viewport[0]-self.XOFFSET)/self.XMUL,
      (self.pixel_viewport[1]-self.YOFFSET)/self.YMUL)
    debug("updateViewport yielded {} / {}".format(repr(self.pixel_viewport), repr(self.viewport)));

  def clear(self):
    def clearInternal(self):
      for i in self.items:
        self.canvas.delete(i)
      self.items = []
    self.drawq.put(lambda self_: clearInternal(self_))

  def transformAsp2Pixel(self, spec, which):
    '''
    spec is either a number or 'rel(number)' or 'abs(number)'
    which is either 'x' or 'y'
    '''
    debug('transformAsp2Pixel({},{})'.format(repr(spec),which))
    assert(isinstance(spec,api.Term))
    assert(which in ['x', 'y'])
    if spec.pred == 'rel':
      return self.coordinate2canvas(str(spec.args[0]), 'rel', which)
    elif spec.pred == 'abs':
      return self.coordinate2canvas(str(spec.args[0]), 'abs', which)
    elif isinstance(spec.pred, int) or isinstance(spec.pred, str):
      return self.coordinate2canvas(spec.pred, 'abs', which)
    else:
      raise Exception("cannot interpret coordinate spec '{}'/{}".format(spec, which))
    
  def coordinate2canvas(self, spec, mode='abs', which='x'):
    assert(mode in ['abs','rel'] and which in ['x','y'])
    spec = float(spec)
    if mode == 'abs':
      if which == 'x':
        offset, mul = self.XOFFSET, self.XMUL
      else:
        offset, mul = self.YOFFSET, self.YMUL
      return offset+spec*mul
    elif mode == 'rel':
      if which == 'x':
        portsize = self.pixel_viewport[0]
      else:
        portsize = self.pixel_viewport[1]
      return portsize*spec/100.0
 
  def cachedImage(self, filename):
    def createPhotoImage(imgfilename):
      debug("createPhotoImage({})".format(repr(imgfilename)))
      return tk.PhotoImage(file=imgfilename)
    if filename not in self.imageCache:
      self.imageCache[filename] = createPhotoImage(filename)
    return self.imageCache[filename]

  def drawingUpdate(self, event):
    '''
    just call all queue elements with self
    see http://stackoverflow.com/questions/7141509/tkinter-wait-for-item-in-queue/7198960#7198960
    '''
    #warn("## drawevent "+repr(event));
    try:
      while not self.drawq.empty():
        drawevent = self.drawq.get()
        #print(repr(drawevent))
        drawevent(self)
      self.updateViewport()
    except:
      warn(traceback.format_exc())
      os._exit(-1)

class DrawRectangleAction(api.Action):
  '''
  action handler class for
    drawRectangle(x1spec,y1spec,x2spec,y2spec[,color])
  '''
  def __init__(self, window):
    self.window = window
  @property
  def interface(self):
    return ('drawRectangle', 5, 4)
  def execute(self, ainput):
    assert(isinstance(ainput, api.ActionInput))
    assert(len(ainput.inputs) in [4, 5])
    debug('DrawRectangleAction.execute({})'.format(ainput))
    x1, y1, x2, y2 = ainput.inputs[0:4]
    color = 'white'
    if len(ainput.inputs) > 4:
      color = ainput.inputs[4]
    px1 = self.window.transformAsp2Pixel(x1,'x')
    py1 = self.window.transformAsp2Pixel(y1,'y')
    px2 = self.window.transformAsp2Pixel(x2,'x')
    py2 = self.window.transformAsp2Pixel(y2,'y')
    self.window.drawq.put(lambda window:
      DrawRectangleAction.drawRectangleInternal(
        window, px1, py1, px2, py2, color))
  @staticmethod
  def drawRectangleInternal(window, x1, y1, x2, y2, color):
    '''this method runs in the TK thread'''
    debug("drawRectangleInternal {}/{} {}/{} {}".format(x1, y1, x2, y2, color))
    window.items.append(window.canvas.create_rectangle(
      x1, y1, x2, y2, fill=color))

class DrawImageAction(api.Action):
  '''
  action handler class for
    drawImage(xspec,spec,imagefilename)
  '''
  def __init__(self, window):
    self.window = window
  @property
  def interface(self):
    return ('drawImage', 3, 3)
  def execute(self, ainput):
    assert(isinstance(ainput, api.ActionInput))
    assert(len(ainput.inputs) in [3, 3])
    debug('DrawImageAction.execute({})'.format(ainput))
    x, y, filename = ainput.inputs
    px = self.window.transformAsp2Pixel(x,'x')
    py = self.window.transformAsp2Pixel(y,'y')
    f = str(filename).strip('"')
    self.window.drawq.put(lambda window:
      DrawImageAction.drawImageInternal(window, px, py, f))
  @staticmethod
  def drawImageInternal(window, x, y, filename):
    '''this method runs in the TK thread'''
    debug("drawImageInternal {}/{} {}".format(x, y, filename))
    img = window.cachedImage(filename)
    window.items.append( window.canvas.create_image(
      x, y, image=img, anchor=tk.SW) )

class DrawTextActionBase(api.Action):
  '''
  action handler base class for
    drawText(xspec,yspec,text[,color])
      draws text at specified position
    drawTextCentered(text[,color])
      draws a list from top to bottom
  '''
  def __init__(self, window):
    self.window = window
  @staticmethod
  def drawTextInternal(window, x, y, text, color, align):
    debug("drawTextInternal {}/{},{},{} {}".format(
      x, y, align, color, repr(text)))
    if align == 'center':
      anchor, justify = tk.S, tk.CENTER
    else:
      anchor, justify = tk.SW, tk.LEFT
    window.items.append( window.canvas.create_text(
      x, y, text=text, fill=color, font=window.FONT,
      anchor=anchor, justify=justify))

class DrawTextAction(DrawTextActionBase):
  '''
  action handler class for
    drawText(xspec,yspec,text[,color])
      draws text at specified position
  '''
  def __init__(self, window):
    DrawTextActionBase.__init__(self, window)
  @property
  def interface(self):
    return ('drawText', 4, 3)
  def execute(self, ainput):
    assert(isinstance(ainput, api.ActionInput))
    assert(len(ainput.inputs) in [3, 4])
    debug('DrawTextAction.execute({})'.format(ainput))
    x, y, text = ainput.inputs[0:3]
    try:
      text = text.unquoted()
    except:
      text = str(text)
    color = 'white'
    if len(ainput.inputs) > 3:
      color = ainput.inputs[3]
    px = self.window.transformAsp2Pixel(x,'x')
    py = self.window.transformAsp2Pixel(y,'y')
    self.window.drawq.put(lambda window:
      DrawTextActionBase.drawTextInternal(
        window, px, py, text, color, 'left'))

class DrawTextCenteredAction(DrawTextActionBase):
  '''
  action handler class for
    drawTextCentered(text[,color])
      draws a list from top to bottom
  '''
  def __init__(self, window):
    DrawTextActionBase.__init__(self, window)
    self.resetCursor()
  @property
  def interface(self):
    return ('drawTextCentered', 2, 1)
  def resetCursor(self):
    self.cursorY = 1
  def execute(self, ainput):
    assert(isinstance(ainput, api.ActionInput))
    assert(len(ainput.inputs) in [1, 2])
    debug('DrawTextCenteredAction.execute({})'.format(ainput))
    text = ainput.inputs[0]
    try:
      text = text.unquoted()
    except:
      text = str(text)
    color = 'white'
    if len(ainput.inputs) > 1:
      color = ainput.inputs[1]
    px = self.window.coordinate2canvas(50, 'rel', 'x')
    advance = 1 + text.count('\n')
    self.cursorY += advance
    py = self.window.coordinate2canvas(self.cursorY, 'abs', 'y')
    self.window.drawq.put(lambda window:
      DrawTextActionBase.drawTextInternal(
        window, px, py, text, color, 'center'))

class Plugin(threading.Thread,api.EventAPI,api.DoAPI):
  def __init__(self):
    threading.Thread.__init__(self)
    api.EventAPI.__init__(self)
    # do not initialize any Tk here!
    # It has to be done in thread in run()
    # (Tkinter is not threadsafe)
    self.daemon = True
    self.keyboard = None
    self.window = None
    self.root = None
    self.startupFinished = threading.Event()
    self.start()
    # wait until run() has initialized all attributes (window, ...)
    if not self.startupFinished.wait(1.0):
      raise Exception("Plugin thread did not start within timeout!")

  def setQueue(self, queue):
    if not self.keyboard:
      warn("tkinter.Plugin ignoring setQueue because startup not finished")
      return
    api.EventAPI.setQueue(self, queue)
    self.keyboard.setQueue(queue)

  def actions(self):
    if not self.window:
      warn("tkinter.Plugin ignoring actions because startup not finished")
      return
    return self.window.actions()

  def beforeExecution(self):
    self.window.beforeExecution()

  def afterExecution(self):
    self.window.afterExecution()

  def run(self):
    self.root = tk.Tk()
    self.keyboard = KeyboardHandler(self.root)
    self.window = WindowHandler(self.root)

    self.root.bind('<<Quit>>', lambda x: self.root.quit())
    #self.root.bind('<Configure>', lambda x: self.configureEvent(x)) # resize, move window

    # notify constructor that we finished initializing
    self.startupFinished.set()
    self.root.mainloop()

  def quit(self):
    self.root.event_generate('<<Quit>>', when='tail')

