
import logging
log = logging.getLogger(__name__)

import sys, cssutils
cssutils.log.setLevel(logging.FATAL)

from bl.dict import Dict
from bl.string import String

class Styles(Dict):

    @classmethod
    def styleProperties(Class, style):
        """return a properties dict from a given cssutils style
        """
        properties = Dict()
        for property in style.getProperties(all=True):
            stylename = property.name + ':'
            properties[stylename] = property.value
            if property.priority != '':
                properties[stylename] = ' !'+property.priority
        return properties

    @classmethod
    def from_css(Class, csstext, encoding=None, href=None, media=None, title=None, validate=None):
        """parse CSS text into a Styles object, using cssutils
        """
        styles = Class()
        cssStyleSheet = cssutils.parseString(csstext, encoding=encoding, href=href, media=media, title=title, validate=validate)
        for rule in cssStyleSheet.cssRules:
            if rule.type==cssutils.css.CSSRule.FONT_FACE_RULE:
                if styles.get('@font-face') is None: styles['@font-face'] = []
                styles['@font-face'].append(Class.styleProperties(rule.style))
            
            elif rule.type==cssutils.css.CSSRule.IMPORT_RULE:
                if styles.get('@import') is None: styles['@import'] = []
                styles['@import'].append(Dict(href=rule.href))              # no support yet for media queries
            
            elif rule.type==cssutils.css.CSSRule.NAMESPACE_RULE:
                pass
            
            elif rule.type==cssutils.css.CSSRule.MEDIA_RULE:
                pass
            
            elif rule.type==cssutils.css.CSSRule.PAGE_RULE:
                pass
            
            elif rule.type==cssutils.css.CSSRule.STYLE_RULE:
                for selector in rule.selectorList:
                    sel = selector.selectorText
                    if sel not in styles:
                        styles[sel] = Class.styleProperties(rule.style)
            
            elif rule.type==cssutils.css.CSSRule.COMMENT:
                pass
            
            elif rule.type==cssutils.css.CSSRule.VARIABLES_RULE:
                pass
            
            else:
                log.warning("Unknown rule type: %r" % rule.cssText)

        return styles
    
    @classmethod    
    def render(c, styles, margin='', indent='\t'):
        """output css text from styles. 
        margin is what to put at the beginning of every line in the output.
        indent is how much to indent indented lines (such as inside braces).
        """
        from unum import Unum
        def render_dict(d):
            return ('{\n' 
                    + c.render(styles[k], 
                        margin=margin+indent,   # add indent to margin
                        indent=indent) 
                    + '}\n')
        s = ""
        # render the css text
        for k in styles.keys():
            s += margin + k + ' '
            if type(styles[k]) == Unum:
                s += str(styles[k]) + ';'
            elif type(styles[k]) in [str, String]:
                s += styles[k] + ';'
            elif type(styles[k]) in [dict, Dict]:
                s += render_dict(styles[k])
            elif type(styles[k]) in [tuple, list]:
                for i in styles[k]:
                    if type(i) in [str, String]:
                        s += i + ' '
                    if type(i) == bytes:
                        s += str(i, 'utf-8') + ' '
                    elif type(i) in [dict, Dict]:
                        s += render_dict(i)
            else:
                s += ';'
            s += '\n'
        return s

