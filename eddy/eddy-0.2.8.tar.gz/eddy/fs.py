import os, shutil
from os.path import *

from typing import Generator, Tuple, List

class FSystem():
    def __init__(self, path):
        self.path = path

    @property
    def content(self) -> str:
        return join(self.path, "content")

    @property
    def public(self) -> str:
        return join(self.path, "public")

    @property
    def settings(self) -> str:
        return join(self.path, "settings.py")

    @property
    def static(self) -> str:
        return join(self.path, "static")

    @property
    def templates(self) -> str:
        return join(self.static, "templates")

    def template(self, name : str) -> str:
        return join(self.templates, name)

    @property
    def css(self) -> str:
        return join(self.static, "css")

    def style(self, css : str) -> str:
        return join(self.css, css)

    @property
    def public_styles(self) -> str:
        return join(self.public, "styles")

    def public_style(self, style : str) -> str:
        return join(self.public_styles, style)

    def traverse(self) -> Generator[Tuple[str, str], None, None]:
        for dirname, dirnames, filenames in os.walk(self.content):
            for file in filenames:
                yield splitext(join(dirname, file))

    def write(self, file, content : str) -> None:
        public = join(self.public, self.public_link(file))
        print(public)

        if not exists(dirname(public)):
            os.makedirs(dirname(public))
        with open(public, 'w') as output:
            output.write(content)

    def public_link(self, file):
        return splitext(file[len(self.content)+1:])[0] + ".html"

    def make_public(self, private_content : List[Tuple[str, str]]):
        for private, public in private_content:
            if os.path.exists(public):
                shutil.rmtree(public)
            shutil.copytree(private, public) 
