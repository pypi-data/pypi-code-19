from PyQt5.QtWidgets import QListWidgetItem


class ListWidgetItem(QListWidgetItem):
    """
    ListWidget item with a custom "path" property
    """
    def __init__(self,name,path):
        super(ListWidgetItem, self).__init__(name)
        self.path = path