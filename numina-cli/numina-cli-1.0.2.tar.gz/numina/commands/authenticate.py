"""The authetication command."""


from json import dumps
import requests
from .base import Base
import os

class Authenticate(Base):

    def run(self):
        authfile = open(os.path.expanduser('~') + '/.numina-token.txt', 'w')
        print('\n Authentication token has been saved for future use: ' + dumps(self.options["<token>"]))
        authfile.write(dumps(self.options["<token>"]))
        authfile.close()
