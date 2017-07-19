from jinja2 import nodes
from jinja2.ext import Extension
from ..resource import Resource


class FisScriptExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['fis_script'])

    def __init__(self, environment):
        super(FisScriptExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        body = parser.parse_statements(['name:end_fis_script'], drop_needle=True)

        return nodes.CallBlock(self.call_method('_handler', []),
                               [], [], body).set_lineno(lineno)

    def _handler(self, caller):
        """Helper callback."""
        Resource.script(caller())
        return ''
