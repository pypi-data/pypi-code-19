# -*- coding: utf-8 -*-
"""Listing Quick Search Portlet."""

# zope imports
from Acquisition import aq_inner
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.portlets.portlets import base
from plone.directives import form
from plone.portlets.interfaces import IPortletDataProvider
from plone.z3cform import z2
from z3c.form import button
from z3c.form.interfaces import IFormLayer
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.interface import (
    alsoProvides,
    implementer,
)
from zope.schema.fieldproperty import FieldProperty

# local imports
from plone.mls.listing import (
    PLONE_4,
    PLONE_5,
)
from plone.mls.listing.browser import listing_search
from plone.mls.listing.i18n import _

# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False

if PLONE_4:
    from zope import formlib

MSG_PORTLET_DESCRIPTION = _(u'This portlet shows a listing quick search form.')

#: Definition of available fields in the given ``rows``.
FIELD_ORDER = {
    'row_listing_type': [
        'q',
        'listing_type',
    ],
    'row_location': [
        'location_state',
        'location_county',
        'location_district',
        'location_city',
    ],
    'row_beds_baths': [
        'beds',
        'baths',
    ],
    'row_object_type': [
        'object_type',
    ],
    'row_price': [
        'price_min',
        'price_max',
    ],
    'row_sizes': [
        'lot_size',
        'interior_area',
    ],
    'row_filter': [
        'air_condition',
        'pool',
        'jacuzzi',
        'location_type',
        'geographic_type',
    ],
}


class QuickSearchForm(form.SchemaForm):
    """Quick Search Form."""

    if PLONE_5:
        template = ViewPageTemplateFile('templates/p5_search_form.pt')
    elif PLONE_4:
        template = ViewPageTemplateFile('templates/search_form.pt')

    schema = listing_search.IListingSearchForm
    ignoreContext = True
    method = 'get'

    def __init__(self, context, request, data=None):
        """Customized form constructor.

        This one also takes an optional ``data`` attribute so it can be
        instantiated from within a portlet without loosing access to the
        portlet data.
        """
        super(QuickSearchForm, self).__init__(context, request)
        self.data = data
        form_context = self.getContent()
        if form_context is not None:
            self.prefix = 'form.{0}'.format(form_context.id)
        self.omitted = []

    @property
    def config(self):
        """Get view configuration data from annotations."""
        annotations = IAnnotations(self.getContent())
        return annotations.get(listing_search.CONFIGURATION_KEY, {})

    def getContent(self):
        search_path = self.data.target_search
        if search_path is None:
            return self.context

        if search_path.startswith('/'):
            obj = api.content.get(path=search_path)
        else:
            obj = api.content.get(UID=search_path)

        return obj

    def update(self):
        super(QuickSearchForm, self).update()
        if self.config.get('location_city', None):
            self.omitted.extend([
                'location_state',
                'location_county',
                'location_district',
                'location_city',
            ])

        if self.config.get('location_district', None):
            self.omitted.extend([
                'location_state',
                'location_county',
                'location_district',
            ])
        elif self.config.get('location_county', None):
            self.omitted.extend([
                'location_state',
                'location_county',
                'location_district',
            ])
        elif self.config.get('location_state', None):
            self.omitted.extend([
                'location_state',
                'location_county',
                'location_district',
            ])

        # Hide those 2 fields from quick search.
        if not self.show_filter:
            self.omitted.extend([
                'location_county',
                'location_district',
            ])

    @button.buttonAndHandler(PMF(u'label_search', default=u'Search'),
                             name='search')
    def handle_search(self, action):
        """Search button."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

    @property
    def action(self):
        """See interfaces.IInputForm."""
        search_path = self.data.target_search

        if search_path is None:
            return

        if search_path.startswith('/'):
            obj = api.content.get(path=search_path)
        else:
            obj = api.content.get(UID=search_path)

        if obj:
            return obj.absolute_url()

    def _widgets(self, row):
        """Return a list of widgets that should be shown for a given row."""
        widget_data = dict(self.widgets.items())
        available_fields = FIELD_ORDER.get(row, [])
        return [
            widget_data.get(key, None) for key in available_fields if
            key not in self.omitted
        ]

    @property
    def show_filter(self):
        """Decide if the filter should be shown or not."""
        form = self.request.form
        button = '{0}.buttons.search'.format(self.prefix)
        return (
            listing_search.IListingSearch.providedBy(self.context) and
            (button in form.keys() or self.config.get('auto_search', False))
        )

    def widgets_listing_type(self):
        """Return the widgets for the row ``row_listing_type``."""
        return self._widgets('row_listing_type')

    def widgets_location(self):
        """Return the widgets for the row ``row_location``."""
        return self._widgets('row_location')

    def widgets_beds_baths(self):
        """Return the widgets for the row ``row_beds_baths``."""
        return self._widgets('row_beds_baths')

    def widgets_object_type(self):
        """Return the widgets for the row ``row_object_type``."""
        return self._widgets('row_object_type')

    def widgets_price(self):
        """Return the widgets for the row ``row_price``."""
        return self._widgets('row_price')

    def widgets_sizes(self):
        """Return the widgets for the row ``row_sizes``."""
        return self._widgets('row_sizes')

    def widgets_filter(self):
        """Return the widgets for the row ``row_filter``."""
        return self._widgets('row_filter')

    def widgets_filter_other(self):
        """Return all other widgets that have not been shown until now."""
        defined_fields = FIELD_ORDER.values()
        shown_fields = [
            shown_field for field_lists in defined_fields for
            shown_field in field_lists
        ]
        return [
            widget for field_name, widget in self.widgets.items() if
            field_name not in shown_fields
        ]


class IQuickSearchPortlet(IPortletDataProvider):
    """A portlet displaying a listing quick search form."""

    heading = schema.TextLine(
        description=_(
            u'Custom title for the portlet (search mode). If no title is '
            u'provided, the default title is used.'
        ),
        required=False,
        title=_(u'Portlet Title (Search)'),
    )

    heading_filter = schema.TextLine(
        description=_(
            u'Custom title for the portlet (filter mode). If no title is '
            u'provided, the default title is used.'
        ),
        required=False,
        title=_(u'Portlet Title (Filter)'),
    )

    target_search = schema.Choice(
        description=_(
            u'Find the search page which will be used to show the results.'
        ),
        required=True,
        vocabulary='plone.mls.listing.available_searches',
        title=_(u'Search Page'),
    )


@implementer(IQuickSearchPortlet)
class Assignment(base.Assignment):
    """Quick Search Portlet Assignment."""

    heading = FieldProperty(IQuickSearchPortlet['heading'])
    heading_filter = FieldProperty(IQuickSearchPortlet['heading_filter'])
    target_search = None

    title = _(u'MLS: Listing Quick Search')
    mode = 'SEARCH'

    def __init__(self, heading=None, heading_filter=None, target_search=None):
        self.heading = heading
        self.heading_filter = heading_filter
        self.target_search = target_search


class Renderer(base.Renderer):
    """Listing Quick Search Portlet Renderer."""

    if PLONE_5:
        render = ViewPageTemplateFile('templates/p5_quick_search.pt')
    elif PLONE_4:
        render = ViewPageTemplateFile('templates/quick_search.pt')

    @property
    def available(self):
        """Check the portlet availability."""
        search_view = self._search_context()
        return (
            listing_search.IListingSearch.providedBy(search_view) and
            self.mode != 'HIDDEN'
            # self.view.context != search_view
        )

    @property
    def config(self):
        """Get view configuration data from annotations."""
        annotations = IAnnotations(self._search_context())
        return annotations.get(listing_search.CONFIGURATION_KEY, {})

    def _search_context(self):
        search_path = self.data.target_search

        if search_path is None:
            return

        if search_path.startswith('/'):
            obj = api.content.get(path=search_path)
        else:
            obj = api.content.get(UID=search_path)

        return obj

    @property
    def title(self):
        """Return the title dependend on the mode that we are in."""
        if self.mode == 'SEARCH':
            return self.data.heading or _(u'Listing Search')
            return self.data.title
        if self.mode == 'FILTER':
            return self.data.heading_filter or _(u'Filter Results')

    @property
    def mode(self):
        """Return the mode that we are in.

        This can be either ``FILTER`` if a search was already performed and we
        are on a search page or ``SEARCH`` otherwise.
        """
        search_context = self._search_context()
        if search_context != self.context:
            return 'SEARCH'

        if search_context:
            prefix = 'form.{0}'.format(search_context.id)
        else:
            prefix = 'form'
        button = '{0}.buttons.search'.format(prefix)
        form = self.request.form
        if (
            listing_search.IListingSearch.providedBy(self.context) and
            (button in form.keys() or self.config.get('auto_search', False))
        ):
            return 'FILTER'
        elif (
            listing_search.IListingSearch.providedBy(self.context) and
            button not in form.keys()
        ):
            return 'HIDDEN'
        else:
            return 'SEARCH'

    def update(self):
        z2.switch_on(self, request_layer=IFormLayer)
        self.form = QuickSearchForm(aq_inner(self.context), self.request,
                                    self.data)
        if HAS_WRAPPED_FORM:
            alsoProvides(self.form, IWrappedForm)
        self.form.update()


class AddForm(base.AddForm):
    """Add form for the Listing Quick Search portlet."""

    if PLONE_5:
        schema = IQuickSearchPortlet
    elif PLONE_4:
        form_fields = formlib.form.Fields(IQuickSearchPortlet)

    label = _(u'Add Listing Quick Search portlet')
    description = MSG_PORTLET_DESCRIPTION

    def create(self, data):
        assignment = Assignment()
        if PLONE_4:
            formlib.form.applyChanges(assignment, self.form_fields, data)
        return assignment


class EditForm(base.EditForm):
    """Edit form for the Listing Quick Search portlet."""

    if PLONE_5:
        schema = IQuickSearchPortlet
    elif PLONE_4:
        form_fields = formlib.form.Fields(IQuickSearchPortlet)

    label = _(u'Edit Listing Quick Search portlet')
    description = MSG_PORTLET_DESCRIPTION

    def update(self):
        if self.context.target_search.startswith('/'):
            obj = api.content.get(path=self.context.target_search)
            if obj is not None:
                uid = api.content.get_uuid(obj)
                self.context.target_search = uid
        super(EditForm, self).update()
