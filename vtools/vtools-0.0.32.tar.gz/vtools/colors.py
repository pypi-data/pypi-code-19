####################################################################################################
########################################### vtools.vimg ############################################
############################################ colors.py #############################################
####################################################################################################
######################################### COLORS (in RGB) ##########################################
from .vtools import eprint

class vColor(tuple):
    """ The vColor class is here to easily create RGB or BGR colors.
    For the sake of my sanity and even though it's counterintuitive to OpenCV's default BGR format, 
    I've defaulted the class creation to use a RGB format for which I think many are more familiar 
    with, most importantly me though. To accommodate <strikethrough>insanity</strikethrough> color 
    creation using BGR, I've added a flag that you can specify as a named parameter to indicate the 
    incoming numbers are in BGR format.
    
    Expects a 3-tuple of integers or an iterator of 3 integers (type: uint8 [0-255])
    Named parameter:
    BGR : bool parameter, default is False. Indicate True/False whether or not the input numbers are
          in BGR format. Useful for working with existing images.
    
    """
    def __new__(cls, *args, BGR = False):

        if len(args) == 3:
            color_tup = tuple(e for e in args) if not BGR else tuple(e for e in args)[::-1]
        elif len(args) == 1 and hasattr(args[0], '__iter__') and len(list(args[0])) == 3:
            color_tup = tuple(args[0]) if not BGR else tuple(args[0])[::-1]
        else:
            eprint("\n\nA tuple or iterable in RGB integer format. May be in BGR if "
                   "you specify BGR = True as a parameter.\n\n")
            return

        obj = super().__new__(cls, color_tup)

        return obj

    def __init__(self, *args, BGR = False):

        if len(args) == 3:
            color_tup = tuple(e for e in args) if not BGR else tuple(e for e in args)[::-1]
        elif len(args) == 1 and hasattr(args[0], '__iter__') and len(list(args[0])) == 3:
            color_tup = tuple(args[0]) if not BGR else tuple(args[0])[::-1]

        self._r, self._g, self._b = color_tup
        self._RGB = not BGR

    def __eq__(self, comp):
        return (c for c in self) == (c for c in comp)

    def RGB(self):
        return vColor(self._r, self._g, self._b)

    def BGR(self):
        return vColor(self._b, self._g, self._r, BGR = True)

    def isRGB(self):
        return self._RGB

    def isBGR(self):
        return not self._RGB

WHITE   = vColor(255,255,255)
BLACK   = vColor(0,0,0)
RED     = vColor(255,0,0)
GREEN   = vColor(0,255,0)
BLUE    = vColor(0,0,255)
AQUA    = vColor(0,255,255)
MAROON  = vColor(128,0,0)
FUCHSIA = vColor(255,0,255)
OLIVE   = vColor(128,128,0)
NAVY    = vColor(0,0,128)
TEAL    = vColor(0,128,128)
PURPLE  = vColor(128,0,128)
YELLOW  = vColor(255,255,0)