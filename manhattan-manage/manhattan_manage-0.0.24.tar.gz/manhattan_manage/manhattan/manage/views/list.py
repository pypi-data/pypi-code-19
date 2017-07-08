"""
Generic list document chain.

: `list_projection`
    The projection used when requesting results from the database (defaults to
    None which means the detault projection for the frame class will be used).

: `list_search_fields`
    A list of fields searched when matching the results (defaults to None which
    means no results are searched).

: `orphans`
    The maximum number of orphan that can be merged into the last page of
    results (the orphans will form the last page) (defaults to 2).

: `per_page`
    The number of results that will appear per page (defaults to 30).

"""

import re
from urllib.parse import urlencode

import flask
from manhattan.chains import Chain, ChainMgr
from manhattan import formatters
from mongoframes import ASC, DESC, And, In, InvalidPage, Or, Paginator, Q

from . import factories

__all__ = ['list_chains']


# Define the chains
list_chains = ChainMgr()

# GET
list_chains['get'] = Chain([
    'config',
    'authenticate',
    'init_form',
    'validate',
    'search',
    'filter',
    'sort',
    'paginate',
    'form_info',
    'decorate',
    'render_template'
])


# Define the links
list_chains.set_link(factories.config(
    list_projection=None,
    list_search_fields=None,
    orphans=2,
    per_page=20
    ))
list_chains.set_link(factories.authenticate())
list_chains.set_link(factories.init_form('list', populate_on=['GET']))
list_chains.set_link(factories.decorate('list'))
list_chains.set_link(factories.render_template('list'))
list_chains.set_link(factories.redirect('list'))

@list_chains.link
def search(state):
    """
    Build a database query based on the `q` parameter within the request to
    filter the paginated documents.

    This link adds the `query` key to the state containing the database query.
    """
    if 'query' not in state:
        state.query = None

    # If no query was provided then skip this step
    if 'q' not in state.form.data or not state.form.data['q']:
        return

    # Replace accented characters in the string with closest matching
    # equivalent non-accented characters.
    q = formatters.text.remove_accents(state.form.data['q'])

    # Make the query safe for regular expressions
    q = re.escape(q)

    # Build the query to search
    assert state.manage_config.list_search_fields, 'No search fields defined'

    q_match = re.compile(q, re.I)
    conditions = []
    for field in state.manage_config.list_search_fields:
        conditions.append(Q[field] == q_match)

    state.query = Or(*conditions)

@list_chains.link
def filter(state):
    """
    Apply any filters to the query.
    """

    # Check that there are filters to apply
    if not hasattr(state.form, 'filters'):
        return

    filter_conditions = []

    for filter_field in state.form.filters:

        # Get the name of the filter field against excluding the prefix
        based_field_name = filter_field.name.split('filters-', 1)[1]

        # Check for a custom filter handler
        custom_func_name = 'filter_' + based_field_name
        if hasattr(state.form.filters, custom_func_name):
            # Custom filter function exists so call it
            custom_func = getattr(state.form.filters, custom_func_name)
            condition = custom_func(state.form, filter_field)
            if condition:
                filter_conditions.append(condition)

        else:
            # No custom filter apply the default filter
            filter_value = filter_field.data

            # Build the conditions
            if filter_value:
                if isinstance(filter_value, list):
                    filter_conditions.append(
                            In(Q[based_field_name], filter_value))

                else:
                    filter_conditions.append(
                            Q[based_field_name] == filter_value)

    # Apply the filter conditions to the query
    if filter_conditions:
        if state.query:
            state.query = And(state.query, *filter_conditions)
        else:
            state.query = And(*filter_conditions)

@list_chains.link
def sort(state):
    """
    Build the sort operation to order the paginated documents.

    This link adds the `sort_by` key to the state containing the sort operation.
    """
    state.sort = None

    # If no sort field/direction was provided then skip this step
    if 'sort_by' not in state.form.data or not state.form.data['sort_by']:
        return

    # Build a sort operation from the form data
    state.sort_by = [(
        state.form.data['sort_by'].lstrip('-'),
        DESC if state.form.data['sort_by'].startswith('-') else ASC
        )]

@list_chains.link
def paginate(state):
    """
    Select a paginated list of documents from the database.

    This link adds `page` and `paginator` keys to the state containing the
    the paged results and the document paginator.
    """

    # Select the documents in paginated form
    state.paginator = Paginator(
        state.manage_config.frame_cls,
        state.query or {},
        sort=state.sort_by or None,
        per_page=state.per_page,
        orphans=state.orphans,
        projection=state.list_projection
        )

    # Select the requested page
    try:
        state.page = state.paginator[state.form.data.get('page', 1)]
    except InvalidPage:
        return flask.redirect(flask.url_for(flask.request.url_rule.endpoint))

@list_chains.link
def form_info(state):
    """
    This link adds information about the form to the `state.form` instance
    (against `_info`, e.g `state.form._info`):

    - `filters_applied` flags that at least one field in the filters form has
      been applied.
    - `paging_query_string` a URL that can be used to retain the form's state
      when navigating between pages.
    - `show_search_button` flags if there are any visible search fields in the
      form (excluding fields in the filters field form).

    NOTE: We store information against `_info` (prefixing wth the an underscore)
    because it prevents potential name clashes with fields that might be defined
    against the form, further for the most part filter forms are generated using
    a template macro which is aware of/expects this attribute and so we
    typcially don't expect developers to interact with this information
    directly.
    """

    if not state.form:
        return

    # Allocate storage for the form information against the form
    form_info = {}
    state.form._info = form_info

    # Check to see if any fields in the `filters` field form have been set
    form_info['filters_applied'] = False
    if hasattr(state.form, 'filters'):
        for field in state.form.filters:
            if field.data:
                form_info['filters_applied'] = True
                break

    # Generate a paging URL for the form
    paging_fields = [f for f in state.form if f.name not in {'filters', 'page'}]
    if hasattr(state.form, 'filters'):
        paging_fields += list(state.form.filters)

    params = {f.name: f.raw_data for f in paging_fields if f.raw_data}
    form_info['paging_query_string'] = urlencode(params, True)

    # Determine if there are any visible fields in the form that are not part
    # of pagination, sorting of the (advanced) filter field.
    form_info['show_search_button'] = False
    none_search_fields = {'filters', 'page', 'sort_by'}
    for field in state.form:
        if field.type != 'HiddenField' and field.name not in none_search_fields:
            form_info['show_search_button'] = True
            break

@list_chains.link
def validate(state):
    """Validate the filter form"""
    if not state.form.validate():
        flask.flash('Invalid page or search request', 'error')
