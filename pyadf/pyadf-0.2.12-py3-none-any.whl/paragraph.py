from pyadf.group_node import GroupNode

class Paragraph(GroupNode):

    def __init__(self, parent=None):
        self.type = 'paragraph'
        super(Paragraph, self).__init__(parent=parent)