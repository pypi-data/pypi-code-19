import plugin_super_class
from PyQt5 import QtGui, QtCore


class SearchPlugin(plugin_super_class.PluginSuperClass):

    def __init__(self, *args):
        super(SearchPlugin, self).__init__('SearchPlugin', 'srch', *args)

    def get_message_menu(self, menu, text):
        google = QtWidgets.QAction(
            QtWidgets.QApplication.translate("srch", "Find in Google"),
            menu)
        google.triggered.connect(lambda: self.google(text))

        duck = QtWidgets.QAction(
            QtWidgets.QApplication.translate("srch", "Find in DuckDuckGo"),
            menu)
        duck.triggered.connect(lambda: self.duck(text))

        yandex = QtWidgets.QAction(
            QtWidgets.QApplication.translate("srch", "Find in Yandex"),
            menu)
        yandex.triggered.connect(lambda: self.yandex(text))

        bing = QtWidgets.QAction(
            QtWidgets.QApplication.translate("srch", "Find in Bing"),
            menu)
        bing.triggered.connect(lambda: self.bing(text))

        return [duck, google, yandex, bing]

    def google(self, text):
        url = QtCore.QUrl('https://www.google.com/search?q=' + text)
        QtGui.QDesktopServices.openUrl(url)

    def duck(self, text):
        url = QtCore.QUrl('https://duckduckgo.com/?q=' + text)
        QtGui.QDesktopServices.openUrl(url)

    def yandex(self, text):
        url = QtCore.QUrl('https://yandex.com/search/?text=' + text)
        QtGui.QDesktopServices.openUrl(url)

    def bing(self, text):
        url = QtCore.QUrl('https://www.bing.com/search?q=' + text)
        QtGui.QDesktopServices.openUrl(url)
