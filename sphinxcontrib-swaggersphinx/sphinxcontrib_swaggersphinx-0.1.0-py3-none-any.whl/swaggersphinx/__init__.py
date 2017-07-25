from docutils import nodes

from .directive import SwaggerDirective

__author__ = 'Tim Shaffer'
__email__ = 'timshaffer@me.com'
__version__ = '0.1.0'


class swaggersphinx(nodes.Admonition, nodes.Element):
    pass


def visit_swaggersphinx_node(self, node):
    self.visit_admonition(node)


def depart_swaggersphinx_node(self, node):
    self.depart_admonition(node)


def setup(app):
    app.add_node(
        swaggersphinx,
        html=(visit_swaggersphinx_node, depart_swaggersphinx_node),
        latex=(visit_swaggersphinx_node, depart_swaggersphinx_node),
        text=(visit_swaggersphinx_node, depart_swaggersphinx_node))

    app.add_directive('swaggersphinx', SwaggerDirective)

    return {'version': __version__}
