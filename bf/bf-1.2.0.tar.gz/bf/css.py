
import logging
log = logging.getLogger(__name__)

import os, re, shutil
import cssselect
from unum import Unum       # pip install unum
from bl.file import File
from bl.url import URL
from .styles import Styles

Unum.UNIT_FORMAT = "%s"
Unum.UNIT_INDENT = ""
Unum.VALUE_FORMAT = "%s"

class CSS(File):
    """
    CSS.styles: the style rules are keys in the "styles" dict. This is limiting, but it works --  
        it happens to result in things being ordered correctly (with @-rules first), and 
        it allows us to effectively query and manipulate the contents of the stylesheet at any time.
    CSS.pt, CSS.px, CSS.em, CSS.en, CSS.inch, CSS.pi, CSS.percent: 
        All the main units are supported and are defined in terms of points, with 1.0em = 12.0pt
    """
    pt = Unum.unit('pt')
    px = Unum.unit('px', 0.75*pt)
    em = Unum.unit('em', 12.*pt)
    en = Unum.unit('en', 6.*pt)
    inch = Unum.unit('in', 72.*pt)
    pi = Unum.unit('pi', 12.*pt)
    percent = Unum.unit('%', 0.01*em)

    def __init__(self, fn=None, styles=None, text=None, encoding='UTF-8', **args):
        File.__init__(self, fn=fn, encoding=encoding, **args)
        if styles is not None:
            self.styles = styles
        elif fn is not None and os.path.exists(fn):
            self.styles = Styles.from_css(open(fn, 'rb').read().decode(encoding))
        elif text is not None:
            self.styles = Styles.from_css(text)
        else:
            self.styles = Styles()

    def render_styles(self, margin='', indent='\t'):
        return Styles.render(self.styles, margin=margin, indent=indent)

    def write(self, fn=None, encoding='UTF-8', **args):
        text = self.render_styles()
        File.write(self, fn=fn, data=text.encode(encoding))

    @classmethod
    def merge_stylesheets(Class, fn, cssfns):
        """merge the given CSS files, in order, into a single stylesheet. First listed takes priority.
        """
        stylesheet = Class(fn=fn)
        for cssfn in cssfns:
            css = Class(fn=cssfn)
            for sel in sorted(css.styles.keys()):
                if sel not in stylesheet.styles:
                    stylesheet.styles[sel] = css.styles[sel]
                elif stylesheet.styles[sel] != css.styles[sel]:
                    log.warn("sel %r not equivalent:\n\t%s\n\t%s" % (sel, stylesheet.fn, css.fn))
                    log.warn("\n\t%r\n\t%r" % (stylesheet.styles[sel], css.styles[sel]))
        return stylesheet

    @classmethod
    def selector_to_xpath(cls, selector, xmlns=None):
        """convert a css selector into an xpath expression. 
            xmlns is option single-item dict with namespace prefix and href
        """
        selector = selector.replace(' .', ' *.')
        if selector[0] == '.':
            selector = '*' + selector
            log.debug(selector)
        
        if '#' in selector:
            selector = selector.replace('#', '*#')
            log.debug(selector)

        if xmlns is not None:
            prefix = xmlns.keys()[0]
            href = xmlns[prefix]
            selector = ' '.join([
                (n.strip() != '>' and prefix + '|' + n.strip() or n.strip())
                for n in selector.split(' ')
                ])
            log.debug(selector)
        
        path = cssselect.CSSSelector(selector, namespaces=xmlns).path
        path = path.replace("descendant-or-self::", "")
        path = path.replace("/descendant::", "//")
        
        log.debug(' ==> %s' % path)
        
        return path
