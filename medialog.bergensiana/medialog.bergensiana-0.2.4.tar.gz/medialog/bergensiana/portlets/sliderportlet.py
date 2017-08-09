from plone.app.portlets.browser import formhelper
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import field
from zope import schema
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty
from plone import api

from zope.i18nmessageid import MessageFactory
_ = MessageFactory('medialog.spacetectheme')

# TODO: If you require i18n translation for any of your schema fields below,

class ISliderPortlet(IPortletDataProvider):
    """A portlet which renders slider links.
    """

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)
        
    tags =  schema.Choice( title = _(u"Show images with this Tag"),
        vocabulary = "plone.app.vocabularies.Keywords", 
        required=True, 
    )

    sort_on = schema.Choice(
            title=_(u"Sort Tags on"),
            values=(
                "sortable_title",
                "created",
                "getObjPositionInParent",
                "id",
                "modified",
                "path",
            ),
    )
    
    sort_order = schema.Choice(
            title=_(u"Sort Order"),
            values=(
                "ascending",
                "descending",
            ),
    )


class Assignment(base.Assignment):
    """
    Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """
    implements(ISliderPortlet)
    
    header = u""
   
    def __init__(self, header=u"",  tags='', sort_on='', sort_order='', get_images=None):
        self.header = header
        self.sort_on = sort_on
        self.sort_order = sort_order
        self.tags = tags
        self.get_images = get_images

    
    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header
        

class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('sliderportlet.pt')
    render = _template
    
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @memoize
    def get_images(self):
        tags = self.data.tags
        sort_on = self.data.sort_on
        sort_order = self.data.sort_order
        catalog = api.portal.get_tool(name='portal_catalog')
        tagged_images = catalog(portal_type='Image', Subject=tags, sort_on=sort_on, sort_order=sort_order)
        return [image for image in tagged_images]

    @memoize  
    def get_image_list(self):
        tags = self.data.tags
        sort_on = self.data.sort_on
        sort_order = self.data.sort_order
        catalog = api.portal.get_tool(name='portal_catalog')
        tagged_images = catalog(portal_type='Image', Subject=tags, sort_on=sort_on, sort_order=sort_order)
        return [{'url': image.getURL(), 'title': image.Title, 'description': image.Description }  for image in tagged_images]

    @memoize
    def hasImages(self):
        return ( len(self.get_images()) > 0 )


class AddForm(formhelper.AddForm):
    schema = ISliderPortlet
    label = _(u"Add Slider Portlet")
    description = _(u"This portlet displays sliding images.")

    def create(self, data):
        return Assignment(**data)


class EditForm(formhelper.EditForm):
    schema = ISliderPortlet
    label = _(u"Edit SliderPortlet")
    description = _(u"This portlet displays sliding image.")
