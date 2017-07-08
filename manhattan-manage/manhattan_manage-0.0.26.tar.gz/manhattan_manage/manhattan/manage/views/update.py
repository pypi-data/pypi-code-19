"""
Generic update document chain.
"""

import flask
from manhattan.chains import Chain, ChainMgr

from . import factories

__all__ = ['update_chains']


# Define the chains
update_chains = ChainMgr()

# GET
update_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'init_form',
    'decorate',
    'render_template'
    ])

# POST
update_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'init_form',
    'validate',
    [
        [
            'build_form_data',
            'update_document',
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
update_chains.set_link(factories.config())
update_chains.set_link(factories.authenticate())
update_chains.set_link(factories.get_document('update'))
update_chains.set_link(factories.init_form('update'))
update_chains.set_link(factories.validate())
update_chains.set_link(factories.store_assets())
update_chains.set_link(factories.decorate('update'))
update_chains.set_link(factories.render_template('update'))
update_chains.set_link(factories.redirect('view', include_id=True))

@update_chains.link
def build_form_data(state):
    """
    Generate the form data that will be used to update the document.

    This link adds a `form_data` key to the the state containing the initialized
    form.
    """
    state.form_data = state.form.data

@update_chains.link
def update_document(state):
    """Update a document"""

    # Get the initialized document
    document = state[state.manage_config.var_name]

    assert document, \
            'No `{0}` set in state'.format(state.manage_config.var_name)

    # Check to see if the frame class supports `logged_update`s and if so
    if hasattr(state.manage_config.frame_cls, 'logged_update'):
        # Supports `logged_update`
        document.logged_update(state.manage_user, state.form_data)

    else:
        # Doesn't support `logged_update`
        for k, v in state.form_data.items():
            setattr(document, k, v)
        document.update()

    assert document, \
            'No `{0}` set in state'.format(state.manage_config.var_name)

    # Flash message that the document was updated
    flask.flash('{document} updated.'.format(document=document))
