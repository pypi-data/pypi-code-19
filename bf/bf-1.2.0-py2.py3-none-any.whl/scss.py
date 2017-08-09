
import logging
LOG = logging.getLogger(__name__)

import os, re, sys
import sass                 # pip install libsass
from bl.dict import Dict    # ordered dict with string keys
from bl.string import String
from .css import CSS

class SCSS(CSS):

    def render_css(self, fn=None, text=None, margin='', indent='\t'):
        """output css using the Sass processor"""
        from .css import CSS
        fn = fn or os.path.splitext(self.fn)[0]+'.css'
        if not os.path.exists(os.path.dirname(fn)):
            os.makedirs(os.path.dirname(fn))
        curdir = os.path.abspath(os.curdir)
        os.chdir(os.path.dirname(fn))               # needed in order for scss to relative @import
        text = text or self.render_styles()
        if text != '': text = sass.compile(string=text)
        os.chdir(curdir)
        return CSS(fn=fn, text=text)
    
