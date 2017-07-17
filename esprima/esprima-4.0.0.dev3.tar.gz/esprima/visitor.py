class Visitor(object):
    def __call__(self, node, metadata):
        self.visit(node, metadata)

    def visit(self, node, metadata):
        """Visit a node."""
        method = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method, self.generic_visit)
        return visitor(node, metadata)

    def generic_visit(self, node, metadata):
        """Called if no explicit visitor function exists for a node."""
        print('node', node)
        print('\tnode.type', node.type)
        print('\tmetadata', metadata)

    # def visit_BlockComment(self, node, metadata):
    #     import ipdb; ipdb.set_trace()
