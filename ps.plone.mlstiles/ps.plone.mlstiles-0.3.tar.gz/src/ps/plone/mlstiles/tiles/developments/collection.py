# -*- coding: utf-8 -*-
"""MLS development collection tiles."""

# python imports
import copy

# zope imports
from Products.CMFPlone.utils import safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.cover import _ as _CC
from collective.cover.tiles import (
    base,
    configuration_view,
)
from plone import api as ploneapi
from plone.app.uuid.utils import uuidToObject
from plone.directives import form
from plone.memoize import view
from plone.mls.listing.i18n import _ as _MLS
from plone.memoize.view import memoize
from plone.namedfile.field import NamedBlobImage as NamedImage
from plone.tiles.interfaces import (
    ITileDataManager,
    ITileType,
)
from ps.plone.mls import (
    api,
    config,
)
from ps.plone.mls.interfaces import IDevelopmentCollection
from ps.plone.mls.browser.developments import collection
from zope import schema
from zope.annotation.interfaces import IAnnotations
from zope.component import (
    getMultiAdapter,
    queryUtility,
)
from zope.interface import implementer
from zope.schema.fieldproperty import FieldProperty
from zope.traversing.browser.absoluteurl import absoluteURL

# local imports
from ps.plone.mlstiles import _


class IDevelopmentCollectionTile(base.IPersistentCoverTile):
    """Configuration schema for a development collection."""

    header = schema.TextLine(
        required=False,
        title=_CC(u'Header'),
    )

    form.omitted('count')
    form.no_omit(configuration_view.IDefaultConfigureForm, 'count')
    count = schema.List(
        required=False,
        title=_CC(u'Number of items to display'),
        value_type=schema.TextLine(),
    )

    form.omitted('offset')
    form.no_omit(configuration_view.IDefaultConfigureForm, 'offset')
    offset = schema.Int(
        default=0,
        required=False,
        title=_CC(u'Start at item'),
    )

    form.omitted('title')
    form.no_omit(configuration_view.IDefaultConfigureForm, 'title')
    title = schema.TextLine(
        required=False,
        title=_CC(u'Title'),
    )

    form.omitted('description')
    form.no_omit(configuration_view.IDefaultConfigureForm, 'description')
    description = schema.TextLine(
        required=False,
        title=_CC(u'Description'),
    )

    form.omitted('banner')
    form.no_omit(configuration_view.IDefaultConfigureForm, 'banner')
    banner = NamedImage(
        required=False,
        title=_CC(u'Banner'),
    )

    form.omitted('logo')
    form.no_omit(configuration_view.IDefaultConfigureForm, 'logo')
    logo = NamedImage(
        required=False,
        title=_CC(u'Logo'),
    )

    form.omitted('location')
    form.no_omit(configuration_view.IDefaultConfigureForm, 'location')
    form.widget(location='ps.plone.mlstiles.widgets.ListingTextFieldWidget')
    location = schema.TextLine(
        required=False,
        title=_MLS(u'Location'),
    )

    form.omitted('lot_size')
    form.no_omit(configuration_view.IDefaultConfigureForm, 'lot_size')
    form.widget(lot_size='ps.plone.mlstiles.widgets.ListingTextFieldWidget')
    lot_size = schema.TextLine(
        required=False,
        title=_MLS(u'Total Lot Size'),
    )

    form.omitted('location_type')
    form.no_omit(configuration_view.IDefaultConfigureForm, 'location_type')
    form.widget(
        location_type='ps.plone.mlstiles.widgets.ListingTextFieldWidget',
    )
    location_type = schema.TextLine(
        required=False,
        title=_MLS(u'Location Type'),
    )

    form.omitted('agency_name')
    form.no_omit(configuration_view.IDefaultConfigureForm, 'agency_name')
    form.widget(agency_name='ps.plone.mlstiles.widgets.ListingTextFieldWidget')
    agency_name = schema.TextLine(
        required=False,
        title=_MLS(u'Agency Name'),
    )

    form.omitted('number_of_listings')
    form.no_omit(
        configuration_view.IDefaultConfigureForm,
        'number_of_listings',
    )
    form.widget(
        number_of_listings='ps.plone.mlstiles.widgets.ListingTextFieldWidget',
    )
    number_of_listings = schema.TextLine(
        required=False,
        title=_MLS(u'Listings'),
    )

    form.omitted('number_of_groups')
    form.no_omit(configuration_view.IDefaultConfigureForm, 'number_of_groups')
    form.widget(
        number_of_groups='ps.plone.mlstiles.widgets.ListingTextFieldWidget',
    )
    number_of_groups = schema.TextLine(
        required=False,
        title=_MLS(u'Property Groups'),
    )

    footer = schema.TextLine(
        required=False,
        title=_CC(u'Footer'),
    )

    uuid = schema.TextLine(
        readonly=True,
        title=_CC(u'UUID'),
    )


@implementer(IDevelopmentCollectionTile)
class DevelopmentCollectionTile(base.PersistentCoverTile):
    """A tile that shows a list of MLS developments."""

    is_configurable = True
    is_editable = True
    short_name = _(u'MLS: Development Collection')
    index = ViewPageTemplateFile('collection.pt')
    configured_fields = []

    header = FieldProperty(IDevelopmentCollectionTile['header'])
    count = FieldProperty(IDevelopmentCollectionTile['count'])
    offset = FieldProperty(IDevelopmentCollectionTile['offset'])
    title = FieldProperty(IDevelopmentCollectionTile['title'])
    description = FieldProperty(IDevelopmentCollectionTile['description'])
    banner = FieldProperty(IDevelopmentCollectionTile['banner'])
    logo = FieldProperty(IDevelopmentCollectionTile['logo'])
    location = FieldProperty(IDevelopmentCollectionTile['location'])
    lot_size = FieldProperty(IDevelopmentCollectionTile['lot_size'])
    location_type = FieldProperty(IDevelopmentCollectionTile['location_type'])
    agency_name = FieldProperty(IDevelopmentCollectionTile['agency_name'])
    number_of_listings = FieldProperty(
        IDevelopmentCollectionTile['number_of_listings'],
    )
    number_of_groups = FieldProperty(
        IDevelopmentCollectionTile['number_of_groups'],
    )
    footer = FieldProperty(IDevelopmentCollectionTile['footer'])
    uuid = FieldProperty(IDevelopmentCollectionTile['uuid'])

    def get_title(self):
        return self.data['title']

    def has_development_collection(self, obj):
        """Check if the obj is activated for recent MLS developments."""
        return IDevelopmentCollection.providedBy(obj)

    def get_config(self, obj):
        """Get collection configuration data from annotations."""
        annotations = IAnnotations(obj)
        return annotations.get(config.SETTINGS_DEVELOPMENT_COLLECTION, {})

    def results(self):
        items = []

        self.configured_fields = self.get_configured_fields()
        size_conf = [
            i for i in self.configured_fields if i['id'] == 'count'
        ]

        if size_conf and 'size' in size_conf[0].keys():
            size = int(size_conf[0]['size'])
        else:
            size = 5

        offset = 0
        offset_conf = [
            i for i in self.configured_fields if i['id'] == 'offset'
        ]
        if offset_conf:
            try:
                offset = int(offset_conf[0].get('offset', 0))
            except ValueError:
                offset = 0

        uuid = self.data.get('uuid', None)
        obj = uuidToObject(uuid)
        if uuid and obj:
            if not self.has_development_collection(obj):
                return items
            config = copy.copy(self.get_config(obj))
            portal_state = getMultiAdapter(
                (self.context, self.request),
                name='plone_portal_state',
            )
            lang = portal_state.language()
            mlsapi = api.get_api(context=obj, lang=lang)
            fields = collection.FIELDS
            if 'banner_image' not in fields:
                fields.append('banner_image')
            params = {
                # 'summary': '1',
                'fields': u','.join(fields),
                'limit': size,
                'offset': offset,
            }
            config.update(params)
            params = api.prepare_search_params(
                config,
                context=obj,
                omit=collection.EXCLUDED_SEARCH_FIELDS,
            )
            try:
                result = api.Development.search(mlsapi, params=params)
            except Exception:
                pass
            else:
                items = result.get_items()

        else:
            self.remove_relation()

        return items

    @memoize
    def view_url(self, obj):
        """Generate view url."""
        return '/'.join([
            absoluteURL(obj, self.request),
            '',
        ])

    def get_url(self, item):
        """Get the (possibly modified) URL for the development item."""
        config = {}
        uuid = self.data.get('uuid', None)
        obj = uuidToObject(uuid)
        if uuid and obj:
            config = copy.copy(self.get_config(obj))

        url = u'{0}{1}'.format(self.view_url(obj), item.id.value)
        if config.get('modify_url', True):
            url = u'{0}___{1}-{2}'.format(
                url,
                item.title.value,
                item.location.value,
            )
        return url

    def is_empty(self):
        return self.data.get('uuid', None) is None or \
            uuidToObject(self.data.get('uuid')) is None

    def populate_with_object(self, obj):
        # Check permission.
        super(DevelopmentCollectionTile, self).populate_with_object(obj)

        if obj.portal_type in self.accepted_ct():
            # Use obj's title as header.
            header = safe_unicode(obj.Title())
            footer = _CC(u'More…')
            uuid = ploneapi.content.get_uuid(obj)

            data_mgr = ITileDataManager(self)
            data_mgr.set({
                'header': header,
                'footer': footer,
                'uuid': uuid,
            })

    def _field_wrapped_in_link(self, field):
        tile_conf = self.get_tile_configuration()
        field_conf = tile_conf.get(field, None)
        if field_conf and isinstance(field_conf, dict):
            return field_conf.get('wraplink', None) == u'on'
        else:
            return False

    def get_configured_fields(self):
        # Override this method, since we are not storing anything
        # in the fields, we just use them for configuration
        tile_type = queryUtility(ITileType, name=self.__name__)
        conf = self.get_tile_configuration()

        fields = schema.getFieldsInOrder(tile_type.schema)

        results = []
        for name, obj in fields:
            field = {'id': name,
                     'title': obj.title}
            if name in conf:
                field_conf = conf[name]
                if ('visibility' in field_conf and
                        field_conf['visibility'] == u'off'):
                    # If the field was configured to be invisible, then just
                    # ignore it
                    continue

                if 'htmltag' in field_conf:
                    # If this field has the capability to change its html tag
                    # render, save it here
                    field['htmltag'] = field_conf['htmltag']

                if 'htmltag-listings' in field_conf:
                    # If this field has the capability to change its html tag
                    # render, save it here
                    field['htmltag-listings'] = field_conf['htmltag-listings']

                if 'wraplink' in field_conf:
                    field['wraplink'] = self._field_wrapped_in_link(name)

                if 'imgsize' in field_conf:
                    field['scale'] = field_conf['imgsize']

                if 'size' in field_conf:
                    field['size'] = field_conf['size']

                if 'offset' in field_conf:
                    field['offset'] = field_conf['offset']

            results.append(field)

        return results

    def thumbnail(self, item):
        """Return a thumbnail of an image.

        Do so if the item has an image field and the field is visible in
        the tile.

        :param item: [required]
        :type item: content object
        """
        if self._has_image_field(item) and self._field_is_visible('image'):
            tile_conf = self.get_tile_configuration()
            image_conf = tile_conf.get('image', None)
            if image_conf:
                scaleconf = image_conf['imgsize']
                # Scale string is something like: 'mini 200:200'.
                # We need the name only: 'mini'.
                scale = scaleconf.split(' ')[0]
                scales = ploneapi.content.get(path='@@images')
                return scales.scale('image', scale)

    @view.memoize
    def get_banner_position(self):
        tile_conf = self.get_tile_configuration()
        image_conf = tile_conf.get('banner', None)
        if image_conf:
            return image_conf['position']
        return ''

    @view.memoize
    def get_logo_position(self):
        tile_conf = self.get_tile_configuration()
        image_conf = tile_conf.get('logo', None)
        if image_conf:
            return image_conf['position']
        return ''

    def remove_relation(self):
        data_mgr = ITileDataManager(self)
        old_data = data_mgr.get()
        if 'uuid' in old_data:
            old_data.pop('uuid')
        data_mgr.set(old_data)

    def show_header(self):
        return self._field_is_visible('header')

    def collection_url(self):
        uuid = self.data.get('uuid', None)
        obj = uuidToObject(uuid)
        return obj.absolute_url() if obj else ''

    def show_footer(self):
        return self._field_is_visible('footer')
