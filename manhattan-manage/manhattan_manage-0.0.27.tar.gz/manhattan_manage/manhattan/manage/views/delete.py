"""
Generic delete document chain.
"""

import flask
from manhattan.chains import Chain, ChainMgr

from . import factories

__all__ = ['delete_chains']


# Define the chains
delete_chains = ChainMgr()

# GET
delete_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'decorate',
    'render_template'
    ])

# POST
delete_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'delete_document',
    'redirect'
    ])


# Define the links
delete_chains.set_link(factories.config())
delete_chains.set_link(factories.authenticate())
delete_chains.set_link(factories.get_document('delete'))
delete_chains.set_link(factories.decorate('delete'))
delete_chains.set_link(factories.render_template('delete'))
delete_chains.set_link(factories.redirect('list'))

@delete_chains.link
def delete_document(state):
    """Delete a document"""

    # Get the document
    document = state[state.manage_config.var_name]

    assert document, \
            'No `{0}` set in state'.format(state.manage_config.var_name)

    # Check to see if the frame class supports `logged_delete`s and if so
    if hasattr(state.manage_config.frame_cls, 'logged_delete'):
        # Supports `logged_delete`
        document.logged_delete(state.manage_user)

    else:
        # Doesn't support `logged_delete`
        document.delete()

    # Flash message that the document was deleted
    flask.flash('{document} deleted.'.format(document=document))