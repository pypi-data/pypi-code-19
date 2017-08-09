from zope import schema
#from plone.directives import dexterity
from plone.directives import form
from plone.autoform.interfaces import IFormFieldProvider
from zope.interface import alsoProvides
from zope.i18nmessageid import MessageFactory


from medialog.tablebehavior.widgets.widget import TableFieldWidget

_ = MessageFactory('medialog.tablebehavior')
from zope.interface import implementer

class ITableBehavior(form.Schema):
    """ A field for a table (to and from)"""

       
    form.fieldset(
        'plotly',
        label = 'Table',
        fields=[
              'table',
        ],
     )  
    
    table = schema.Text(
        title=u'Table',
        default=u'[["A", "B"], [1, 10]]',
        required=False,
    )  
    
    form.widget(table=TableFieldWidget)

alsoProvides(ITableBehavior, IFormFieldProvider)

