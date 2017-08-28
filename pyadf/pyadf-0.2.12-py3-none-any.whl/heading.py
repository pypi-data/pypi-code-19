from pyadf.group_node import GroupNode

class Heading(GroupNode):

    def __init__(self, level, parent=None):
        self.type = 'heading'
        self.level = level
        super(Heading, self).__init__(parent=parent)

    def attrs(self):
        return {
            'level': self.level
        }