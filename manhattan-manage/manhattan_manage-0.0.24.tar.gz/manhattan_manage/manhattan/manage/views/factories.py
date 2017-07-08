"""
Link factories for manhattan views.
"""


import bson
import os
import urllib

import flask
import inflection
from manhattan.nav import Nav, NavItem
from manhattan import secure

# Optional imports
try:
    from manhattan.assets import Asset
except ImportError as e:
    pass

__all__ = [
    'authenticate',
    'config',
    'decorate',
    'get_document',
    'init_form',
    'redirect',
    'render_template',
    'store_assets',
    'validate'
    ]


def authenticate(
        user_g_key='user',
        sign_in_endpoint='users.sign_in',
        sign_out_endpoint='users.sign_out'
        ):
    """
    Authenticate the caller has permission to call the view.

    This link adds a `user` key to the the state containing the currently signed
    in user.
    """

    def authenticate(state):
        # Get the signed in user
        state.manage_user = flask.g.get(user_g_key)

        # We're not allowed to access this view point so determine if that's
        # because we're not sign-in or because we don't have permission.
        if not state.manage_user:
            # We need to sign-in to view this endpoint

            # Forward the user to the sign-in page with the requested URL as the
            # `next` parameter.
            redirect_url = flask.url_for(
                sign_in_endpoint,
                next=secure.safe_redirect_url(
                    flask.request.url,
                    [flask.url_for(sign_out_endpoint)]
                    )
                )
            return flask.redirect(redirect_url)

        # Check if we're allowed to access this requested endpoint
        if not Nav.allowed(flask.request.endpoint, **flask.request.view_args):

            # We don't have permission to view this endpoint
            flask.abort(403, 'Permission denied')

    return authenticate

def config(**defaults):
    """
    Return a function will configure a view's state adding defaults where no
    existing value currently exists in the state.

    This function is designed to be included as the first link in a chain and
    to set the initial state so that chains can be configured on a per copy
    basis.
    """

    def config(state):
        # Apply defaults
        for key, value in defaults.items():

            # First check if a value is already set against the state
            if key in state:
                continue

            # Next check if a value is defined against the config
            if hasattr(state.manage_config, key):
                state[key] = getattr(state.manage_config, key)
                continue

            # Finally if no value has been provided then set the default
            state[key] = value

    return config

def decorate(view_type, title=None, last_breadcrumb=None, tabs=None):
    """
    Return a function that will add decor information to the state for the named
    view.

    Decor refers to content that is common to the majority of pages (for example
    the page title). By default decor includes:

    - `actions`
    - `breadcrumb`
    - `tabs`
    - `title`
    - `result_action` (only added to `list` view types).

    This link adds a `decor` key to the state.
    """

    def _get_breadcrumb_label(config, view_type):
        # Given a view type return the associated default breadcrumb label
        if view_type is 'list':
            return config.name_plural.capitalize()

        elif view_type is 'view':
            return config.name.capitalize() + ' details'

        return inflection.humanize(view_type)

    def decorate(state):
        # Add `decor` to the state which all decorations will be assigned to
        state.decor = {}

        # Localize `manage_config`
        config = state.manage_config

        # Title
        state.decor['title'] = title
        if not title:
            if view_type is 'list':
                state.decor['title'] = config.name_plural.capitalize()

            elif view_type is 'order':
                state.decor['title'] = 'Order ' + config.name_plural

            elif view_type is 'view':
                state.decor['title'] = config.titleize(state[config.var_name])

            elif view_type is 'add':
                state.decor['title'] = 'Add ' + config.name

            elif config.var_name in state:
                state.decor['title'] = '{view_type} {document}'.format(
                    document=config.titleize(state[config.var_name]),
                    view_type=inflection.humanize(view_type)
                    )
            else:
                state.decor['title'] = inflection.humanize(view_type)

        # Breadcrumb
        breadcrumbs = Nav.local_menu()

        # All view types except list are assumed to start their breadcrumb trail
        # with list...
        if view_type is not 'list':
            if Nav.exists(config.get_endpoint('list')):
                list_item = NavItem(
                    _get_breadcrumb_label(config, 'list'),
                    config.get_endpoint('list')
                    )
                breadcrumbs.add(list_item)

        # ...followed by view (with the exception of add and view).
        if view_type not in ['add', 'list', 'view']:
            if (Nav.exists(config.get_endpoint('view'))
                    and config.var_name in state):

                _id = state[config.var_name]._id
                view_args = dict([(config.var_name, _id)])
                view_item = NavItem(
                    _get_breadcrumb_label(config, 'view'),
                    config.get_endpoint('view'),
                    view_args=view_args
                    )
                breadcrumbs.add(view_item)

        # Add the last breadcrumb
        item = NavItem(
            last_breadcrumb or _get_breadcrumb_label(config, view_type),
            ''
            )
        breadcrumbs.add(item)

        # Set the breadcrumbs against the state
        state.decor['breadcrumbs'] = breadcrumbs

        # Actions
        actions = Nav.local_menu()

        # List pages are assumed to support add and order actions
        if view_type is 'list':
            if Nav.exists(config.get_endpoint('add')):
                actions.add(NavItem('Add', config.get_endpoint('add')))

            if Nav.exists(config.get_endpoint('order')):
                actions.add(NavItem('Order', config.get_endpoint('order')))

        # View pages are assumed to support update and delete actions
        elif view_type is 'view':
            _id = state[config.var_name]._id
            view_args = dict([(config.var_name, _id)])

            if Nav.exists(config.get_endpoint('update')):
                endpoint = config.get_endpoint('update')
                actions.add(NavItem('Update', endpoint, view_args=view_args))

            if Nav.exists(config.get_endpoint('delete')):
                endpoint = config.get_endpoint('delete')
                actions.add(NavItem('Delete', endpoint, view_args=view_args))

        # Update pages are assumed to support delete actions if there is no view
        # page.
        elif view_type is 'update' \
                and not Nav.exists(config.get_endpoint('view')):

            if Nav.exists(config.get_endpoint('delete')):
                _id = state[config.var_name]._id
                endpoint = config.get_endpoint('delete')
                view_args = dict([(config.var_name, _id)])
                actions.add(NavItem('Delete', endpoint, view_args=view_args))

        # Set the actions against the state
        state.decor['actions'] = actions

        # Tabs (if a tabs menu has been specified we attempt to find it and
        # include it in the decor).
        state.decor['tabs'] = None
        if tabs:
            state.decor['tabs'] = Nav.menu(tabs, raise_unless_exists=True)

        # View link

        # List view types are provided with a result action, the result action
        # should be a function that accepts typically a single document as an
        # argument and returns a `Nav.query` result.
        if view_type is 'list':

            def results_action(document):
                # A generic results action
                args = {}
                args[config.var_name] = document._id

                # Check for view link
                link = Nav.query(config.get_endpoint('view'), **args)
                if not link.exists:

                    # Check for update link
                    link = Nav.query(config.get_endpoint('update'), **args)
                    if link.exists:
                        return link

                return link

            state.decor['results_action'] = results_action

    return decorate

def get_document(projection=None):
    """
    Return a function that will attempt to retreive a document from the
    database by `_id` using the `var_name` named parameter in the request.

    This link adds a `{state.manage_config.var_name}` key to the the state
    containing the document retreived.

    Optionally a projection to use when getting the document can be specified,
    this can either be a dictionary or the name of the projection as defined
    against the config, e.g: `get_document('view')` will use the projection
    defined against the config attribute `view_projection`.
    """

    def get_document(state):
        # Get the Id of the document passed in the request
        document_id = flask.request.values.get(state.manage_config.var_name)

        # Attempt to convert the Id to the required type
        try:
            document_id = bson.objectid.ObjectId(document_id)
        except bson.errors.InvalidId:
            flask.abort(404)

        # If there's a projection defined check if it's a string, if so we need
        # to look for the projection against the config.
        _projection = None
        if projection:
            if isinstance(projection, str):
                if hasattr(state.manage_config, projection + '_projection'):
                    _projection = getattr(state, projection + '_projection')
            elif isinstance(projection, dict):
                _projection = projection

        # Attempt to retrieve the document
        kwargs = {}
        if _projection:
            kwargs['projection'] = _projection
        document = state.manage_config.frame_cls.by_id(document_id, **kwargs)

        if not document:
            flask.abort(404)

        # Set the document against the state
        state[state.manage_config.var_name] = document

    return get_document

def init_form(view_name, populate_on=None):
    """
    Return a function that will initialize a form for the named generic view
    (e.g list, add, update, etc.)

    Optionally the CSRF projection for the form can be enabled (default) or
    disabled.

    This link adds a `form` key to the the state containing the initialized
    form.
    """

    # If populate_on is not specified then we default to `POST`
    if populate_on is None:
        populate_on = ['POST']

    def init_form(state):
        # Get the form class
        form_cls = state.manage_config.get_form_cls(view_name)
        assert form_cls, 'No form defined for this view {0}'.format(view_name)

        # Initialize the form
        formdata = None
        if flask.request.method in populate_on:
            if flask.request.method in ['POST', 'PUT']:
                formdata = flask.request.form
            else:
                formdata = flask.request.args

        # If a document is assign to the state then is is sent as the first
        # argument when initializing the form.
        obj = None
        if state.manage_config.var_name in state:
            obj = state[state.manage_config.var_name]
        state.form = form_cls(formdata, obj=obj)

    return init_form

def redirect(endpoint, include_id=False):
    """
    Return a function that will trigger a redirect to the given endpoint.

    Optionally an Id for the current document in the state can be added to the
    URL, e.g `url_for('view.user', user=user._id)` by passing `include_id` as
    True.
    """

    def redirect(state):
        # Build the URL arguments
        url_args = {}
        if include_id:
            url_args[state.manage_config.var_name] = \
                    state[state.manage_config.var_name]._id

        # Get the URL for the endpoint
        prefix = state.manage_config.endpoint_prefix
        if state.manage_config.endpoint_prefix:
            url = flask.url_for('.' + prefix + endpoint, **url_args)
        else:
            url = flask.url_for('.' + endpoint, **url_args)

        # Return the redirect response
        return flask.redirect(url)

    return redirect

def render_template(template_name):
    """
    Return a function that will render the named template. The state object is
    used as template arguments.
    """

    def render_template(state):
        # Build the template filepath
        template_filepath = os.path.join(
            state.manage_config.template_path,
            template_name + '.html'
            )

        # Render the template
        return flask.render_template(template_filepath, **state)

    return render_template

def store_assets():
    """
    Return a function that will convert temporary assets to permenant assets.
    """

    def store_assets(state):

        # Check that the app supports an asset manager, if not then there's
        # nothing to do.
        if not hasattr(flask.current_app, 'asset_mgr'):
            return
        asset_mgr = flask.current_app.asset_mgr

        # Get the document being added or updated
        document = state[state.manage_config.var_name]

        # Find any values against the document which are temporary assets
        update_fields = []
        for field in document.get_fields():
            value = document.get(field)

            # Ignore any value that's not a temporary asset
            if not (isinstance(value, Asset) and value.temporary):
                continue

            # Store the asset permenantly
            flask.current_app.asset_mgr.store(value)

            # Check if any variations are defined for the field
            if hasattr(state.manage_config, field + '_variations'):
                variations = getattr(state.manage_config, field + '_variations')

                # Store variations for the asset
                asset_mgr.generate_variations(value, variations)

            # Flag the field requires updating against the database
            update_fields.append(field)

        if update_fields:
            document.update(*update_fields)

    return store_assets

def validate(error_msg='Please review your submission'):
    """
    Return a function that will call validate against `state.form`. If the form
    is valid the function will return `True` or `False` if not.

    Optionally an `error_msg` can be passed, if the form fails to validate this
    will be flashed to the user.
    """

    def validate(state):
        assert state.form, 'No form to validate against'

        if state.form.validate():
            return True

        flask.flash(error_msg, 'error')
        return False

    return validate
