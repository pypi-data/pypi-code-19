# -*- coding: utf-8 -*-
"""
    sphinxcontrib.websupport_lean.writer
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    sphinxcontrib.websupport_lean writer that adds potential third party
    annotations.

    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from sphinx.writers.html import HTMLTranslator


class WebSupportTranslator(HTMLTranslator):
    """
    Our custom HTML translator.
    """

    def __init__(self, builder, *args, **kwargs):
        HTMLTranslator.__init__(self, builder, *args, **kwargs)

    def add_db_node(self, node):
        storage = self.builder.storage
        if not storage.has_node(node.uid):
            storage.add_node(id=node.uid,
                             document=self.builder.current_docname,
                             source=node.rawsource or node.astext())
