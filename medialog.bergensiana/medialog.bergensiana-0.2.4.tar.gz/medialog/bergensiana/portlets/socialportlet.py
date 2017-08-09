from plone.app.portlets.browser import formhelper
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from z3c.form import field
from zope import schema
from zope.interface import implements
from zope.schema.fieldproperty import FieldProperty


from zope.i18nmessageid import MessageFactory
_ = MessageFactory('medialog.spacetectheme')

# TODO: If you require i18n translation for any of your schema fields below,

class ISocialPortlet(IPortletDataProvider):
    """A portlet which renders social links.
    """

    header = schema.TextLine(
        title=_(u"Portlet header"),
        description=_(u"Title of the rendered portlet"),
        required=True)


class Assignment(base.Assignment):
    """
    Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ISocialPortlet)

    header = u""
   
    def __init__(self, header=u""):
        self.header = header
        
    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header


class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('socialportlet.pt')
    render = _template

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)



class AddForm(formhelper.AddForm):
    schema = ISocialPortlet
    label = _(u"Add Social Portlet")
    description = _(u"This portlet displays social links.")

    def create(self, data):
        return Assignment(**data)


class EditForm(formhelper.EditForm):
    schema = ISocialPortlet
    label = _(u"Edit SocialPortlet")
    description = _(u"This portlet displays social links.")
