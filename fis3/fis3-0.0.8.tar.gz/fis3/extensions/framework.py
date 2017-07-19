from jinja2 import nodes
from jinja2.ext import Extension
from ..resource import Resource


class FisFrameworkExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['fis_framework'])

    def __init__(self, environment):
        super(FisFrameworkExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        args = [parser.parse_expression()]

        return nodes.CallBlock(self.call_method('_handler', args), [], [], []).set_lineno(lineno)

    def _handler(self, res_id, caller):
        """Helper callback."""
        return Resource.framework(res_id)
