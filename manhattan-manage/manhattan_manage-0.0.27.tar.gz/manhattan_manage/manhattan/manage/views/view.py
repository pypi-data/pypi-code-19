"""
Generic view document chain.

: `view_projection`
    The projection used when requesting the document from the database (defaults
    to None which means the detault projection for the frame class will be
    used).

"""

from manhattan.chains import Chain, ChainMgr

from . import factories

__all__ = ['view_chains']


# Define the chains
view_chains = ChainMgr()

# GET
view_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'decorate',
    'render_template'
    ])


# Define the links
view_chains.set_link(factories.config(view_projection=None))
view_chains.set_link(factories.authenticate())
view_chains.set_link(factories.get_document('view'))
view_chains.set_link(factories.decorate('view'))
view_chains.set_link(factories.render_template('view'))