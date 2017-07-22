from typing import Dict, Any, List
import os, datetime

import jinja2
from jinja2 import Environment, FileSystemLoader, select_autoescape

def jinja_functions(user_functions : Dict[str, Any], env, writer) -> Dict[str, Any]:
    def get_style(style : str) -> str :
        return os.path.join(env['URL'], "styles", style, "main.css")

    def get_colorscheme(colorscheme : str) -> str:
        return os.path.join(env['URL'], "styles",  "colorschemes" ,  colorscheme)

    helpers = {
        'get_style' : get_style,
        'get_colorscheme' : get_colorscheme,
    }

    return {**user_functions, **helpers}

def split_text(text):
#    def find_tags(text):
#        beg = 0
#        for i, c in enumerate(text):
#            if c == '<':
#                beg = 1
#            elif c == '>' and beg == 1:
#                beg = 0
#                yield i
#
    m = len(text)//2
    if m == 0:
        return "", ""

    for i,c in enumerate(text[m:]):
        if c==' ' or c=='\n' or c=='\t':
            return text[:i+m], text[m+i:]
#    for c in find_tags(text):
#        print(c)
#        if c > m-0.01*len(text):
#            return text[:c+1], text[c+1:]

class Generator():
    def __init__(self, logger, writer):
        logger.debug("Inititalizad generator")
        self.logger = logger
        self.writer = writer
        self.pages : List[dict]= []
        self.jinja_env = Environment(
            loader=FileSystemLoader(writer.templates))

    def get_context(self, file_data : Dict[str, Any]) -> None:
        self.pages.append(file_data)

    def generate(self) -> None:
        self.pages = self.generate_links(self.pages)
        for page in self.pages:
            jinja_helpers = jinja_functions(page['JINJA_FUNCTIONS'], page, self.writer)
            self.jinja_env.globals.update(jinja_helpers)
            template = self.jinja_env.get_template(os.path.join(page['SITE_TEMPLATE'], page['TEMPLATE'] + ".html"))
            page['LEFT'], page['RIGHT'] =  split_text(page['CONTENT'])
            output = template.render(page)

            self.writer.write(page['PATH'], output)
            self.writer.make_public(
                [(os.path.join(self.writer.style(page['STYLE'])),
                  self.writer.public_style(page['STYLE'])),
                 (os.path.join(self.writer.style("colorschemes")),
                  self.writer.public_style("colorschemes")),
                ])


    def generate_links(self, data):
        filelinks = {}
        dates = {}
        for page in data:
            name = os.path.basename(os.path.splitext(page['PATH'])[0])
            dates[name] = page.get('DATE') or datetime.date.today()
            filelinks[name] = self.writer.public_link(page['PATH'])
        print("filelinks", filelinks)
        pages = [{**d, "links": filelinks, "dates": dates} for d in data]
        return pages
