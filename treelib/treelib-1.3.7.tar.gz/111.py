from treelib import Node, Tree


class Apple():
    def __init__(self, name):
        self.name = name
    def __str__(self):
        return self.name

harryApple = Apple("Harry")
addonApple = Apple("Addons")

tree      = Tree()
harryNode = Node( harryApple )  # root node
addonNode = Node( addonApple )

tree.add_node( harryNode )
tree.add_node( addonNode, parent=harryNode )
tree.show()