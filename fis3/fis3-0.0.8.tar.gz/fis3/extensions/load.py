from jinja2 import nodes
from jinja2.ext import Extension
from ..resource import Resource


class FisLoadExtension(Extension):
    # a set of names that trigger the extension.
    tags = set(['fis_load'])

    def __init__(self, environment):
        super(FisLoadExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno

        args = [parser.parse_expression()]

        return nodes.CallBlock(self.call_method('_handler', args), [], [], []).set_lineno(lineno)

    def _handler(self, res_id, caller):
        """Helper callback."""
        Resource.load(res_id)
        return ''
