"""
Generic add document chain.
"""

import flask
from manhattan.chains import Chain, ChainMgr

from . import factories

__all__ = ['add_chains']


# Define the chains
add_chains = ChainMgr()

# GET
add_chains['get'] = Chain([
    'config',
    'authenticate',
    'init_form',
    'decorate',
    'render_template'
])

# POST
add_chains['post'] = Chain([
    'config',
    'authenticate',
    'init_form',
    'validate',
    [
        [
            'init_document',
            'add_document',
            'store_assets',
            'redirect'
        ],
        [
            'decorate',
            'render_template'
        ]
    ]
])


# Define the links
add_chains.set_link(factories.config())
add_chains.set_link(factories.authenticate())
add_chains.set_link(factories.init_form('add'))
add_chains.set_link(factories.validate())
add_chains.set_link(factories.store_assets())
add_chains.set_link(factories.decorate('add'))
add_chains.set_link(factories.render_template('add'))
add_chains.set_link(factories.redirect('view', include_id=True))

@add_chains.link
def init_document(state):
    """
    Initialize a new document and populates it using the submitted form data.

    This link adds a `{state.manage_config.var_name}` key to the the state
    containing the initialized document.
    """

    # Initialize a new document
    document = state.manage_config.frame_cls()

    # Populate the document from the form
    state.form.populate_obj(document)

    # Set the document against the state
    state[state.manage_config.var_name] = document

@add_chains.link
def add_document(state):
    """Add a document"""

    # Get the initialized document
    document = state[state.manage_config.var_name]

    assert document, \
            'No `{0}` set in state'.format(state.manage_config.var_name)

    # Check to see if the frame class supports `logged_insert`s and if so
    if hasattr(state.manage_config.frame_cls, 'logged_insert'):
        # Supports `logged_insert`
        document.logged_insert(state.manage_user)

    else:
        # Doesn't support `logged_insert`
        document.insert()

    assert document, \
            'No `{0}` set in state'.format(state.manage_config.var_name)

    # Flash message that the document was added
    flask.flash('{document} added.'.format(document=document))
