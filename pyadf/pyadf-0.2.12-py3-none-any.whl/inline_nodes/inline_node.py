from pyadf.inline_nodes.marks.link import Link

class InlineNode(object):

    def __init__(self):
        self.marks = []

    def add_mark(self, mark):
        self.marks.append(mark)

    def with_marks(self, obj):
        if (self.marks != None):                
            mark_count = len(self.marks)
            if (mark_count > 0):
                obj['marks'] = [mark.to_doc() for mark in self.marks]

        return obj