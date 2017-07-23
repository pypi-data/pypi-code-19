"""The hello command."""


from json import dumps

from .base import Base


class Hello(Base):
    """Hello Python!"""

    def run(self):
        print('Hello Python!')
