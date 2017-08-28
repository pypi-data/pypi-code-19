from pyadf.inline_nodes.inline_node import InlineNode

class Text(InlineNode):

    def __init__(self, text):
        self.text = text
        super(Text, self).__init__()

    def to_doc(self):
        return self.with_marks({
            'type': 'text',
            'text': self.text
        })