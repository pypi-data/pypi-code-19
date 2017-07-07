from copy import deepcopy
from ftw.testbrowser.widgets.base import PloneWidget
from ftw.testbrowser.widgets.base import widget


@widget
class ReferenceBrowserWidget(PloneWidget):

    @staticmethod
    def match(node):
        if not node.tag == 'div' or 'field' not in node.classes:
            return False
        return bool(node.css('div.referencewidget'))

    def fill(self, values):

        # Clear widget data
        for item in self.css('.selected_items input[type="hidden"]'):
            item.node.getparent().remove(item.node)

        field = self.css('input[type="hidden"]').first

        if isinstance(values, basestring):
            field.value = values
        elif isinstance(values, list):
            for index, obj in enumerate(values):
                template = deepcopy(field.node)
                path = obj

                if not isinstance(values, basestring):
                    path = '/'.join(obj.getPhysicalPath())

                if index == 0:
                    field.value = path
                else:
                    new = deepcopy(template)
                    new.value = path
                    self.node.append(new)

        else:
            # Assume an DX object
            field.value = '/'.join(values.getPhysicalPath())
