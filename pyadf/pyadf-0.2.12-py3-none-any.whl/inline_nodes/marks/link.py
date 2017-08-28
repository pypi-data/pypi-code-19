from pyadf.inline_nodes.marks.mark import Mark

class Link(Mark):

    def __init__(self, href, title):
        self.href = href
        self.title = title
        super(Link, self).__init__(type_name='link')


    def attrs(self):
        result = {
            'href': self.href
        }
        if (self.title != None):
            result['title'] = self.title
        return result