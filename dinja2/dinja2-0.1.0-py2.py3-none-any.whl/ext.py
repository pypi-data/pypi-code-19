# coding=utf-8
import logging

import jinja2
from jinja2 import nodes
from jinja2.ext import Extension


class ActiveUrlExtension(Extension):
    """
    returns 'active' when first argument is matching request.path
    """

    tags = {'is_active'}

    def parse(self, parser):
        tag = next(parser.stream)
        args = [parser.parse_expression()]
        if parser.stream.current.type != 'block_end':
            parser.stream.expect('comma')
            args.append(parser.parse_expression())

        return nodes.CallBlock(self.call_method('_render', args), [], [], []).set_lineno(tag.lineno)

    @jinja2.contextfunction
    def _render(self, context, target, active_class='active', *args, **kwargs):
        if 'request' not in context:
            logging.warning("No request in context, cannot set active")
            return ''
        request = context['request']
        if request.path != target:
            return ''
        return active_class


active = ActiveUrlExtension
