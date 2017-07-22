import logging, sys
from eddy import log
from typing import List, Tuple
import os

logger = log.init_logging(__name__, logging.DEBUG, sys.stdout)

class Reader():
    ext : List[str] = []

    def convert(self) -> dict:
        return {}

class MDReader(Reader):
    """Markdown file reader"""
    ext = ['md', 'markdown', 'mdown', 'mkdn', 'mkd', '.mdwn', '.mdtxt', '.mdtext', '.Rmd']
    
    def __init__(self, logger, url, extensions : List[str] = []):
        self.logger = logger
        self.logger.debug("Starting markdown reader")
        try:
            import markdown #type: ignore
            from eddy.md_extensions.wikilinks import WikiLinkExtension
        except Exception as e:
            self.logger.warning("Can't import markdown" + str(e))
            return
        self.url = url
        extensions += ['markdown.extensions.meta', WikiLinkExtension(base_url=self.url, end_url='.html')]
        self.md = markdown.Markdown(extensions = extensions)

    def convert(self, path : str) -> dict:
        def convert_meta(meta):
            new_meta = {}
            for key, value in meta.items():
                new_meta[key.upper()] = value.pop()

            return new_meta

        self.logger.debug("Converting %s", path)
        with open(path) as file:
            file_content = file.read()
            if len(file_content) == 0:
                return {"CONTENT": "", "PATH": "", "TITLE": "fucked up"}
            content = self.md.reset().convert(file_content)
            self.md.Meta = convert_meta(self.md.Meta)
            title = os.path.splitext(os.path.basename(path))[0]
            return {"CONTENT": content, "PATH": path, "TITLE" : title, **self.md.Meta}

class RSTReader(Reader):
    """ Restructuredtext file reader"""
    ext = ["rst"]

    def __init__(self, logger, url, extensions=[]):
        self.logger = logger
        self.logger.debug("Starting rst reader")
        try:
            from docutils import core
            self.core = core
        except Exception as e:
            self.logger.warning("Can't import markdown" + e)
            return self

    def convert(self, path : str) -> dict:
        def parse_front_matter(path : str) -> Tuple[dict, str]:
            """Parse settings in rst file.
            ---
            setting: setting content
            ---
            """
            self.logger.debug("Converting %s", path)
            settings = {}
            count = 0
            file = open(path)
            lines = file.readlines()
            if len(lines) > 0 and "---" in lines[0]:
                for i, line in enumerate(lines[1:]):
                    if "---" in line:
                        break
                    var, content = line.split(':')
                    setting = [word.strip() for word in content.split(' ')]
                    setting = [s for s in setting if s != ""]
                    settings[var.strip()] = setting
                    count = i
            else:
                file.seek(0)

            return settings, ''.join(lines[count+1:])

        def to_html(content) -> dict :
            """Convert rst to html using docutils"""
            """Tiny bit of magic"""
            parts = self.core.publish_parts(source=content, writer_name='html')
            content = parts['body_pre_docinfo']+parts['fragment']
            return {'CONTENT': content}

        settings, content = parse_front_matter(path)
        html = to_html(content)
        return {"PATH": path, **html, **settings}
