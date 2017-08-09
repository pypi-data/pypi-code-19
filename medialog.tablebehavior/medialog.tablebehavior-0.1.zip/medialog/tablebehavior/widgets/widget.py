import zope.component
import zope.interface
import zope.schema.interfaces

from z3c.form import interfaces
from z3c.form import widget
from z3c.form.browser import text


class ITableWidget(interfaces.IWidget):
    """tablefield widget."""


class TableWidget(text.TextWidget):
    maxlength = 255
    size = 30
    
    zope.interface.implementsOnly(ITableWidget)
    
    def tablevalue(self):
    	return self.value()

def TableFieldWidget(field, request):
    """IFieldWidget factory for TableWidget."""
    return widget.FieldWidget(field, TableWidget(request))
