# -*- coding: utf-8 -*-
"""
    sphinxcontrib.websupport.storage
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Storage for the websupport package.

    :copyright: Copyright 2007-2016 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""


class StorageBackend(object):
    def pre_build(self):
        """Called immediately before the build process begins. Use this
        to prepare the StorageBackend for the addition of nodes.
        """
        pass

    def has_node(self, id):
        """Check to see if a node exists.

        :param id: the id to check for.
        """
        raise NotImplementedError()

    def add_node(self, id, document, source):
        """Add a node to the StorageBackend.

        :param id: a unique id provided for users' customizing websupport.
        :param document: the name of the document the node belongs to.
        :param source: the source files name.
        """
        raise NotImplementedError()

    def post_build(self):
        """Called after a build has completed. Use this to finalize the
        addition of nodes if needed.
        """
        pass
