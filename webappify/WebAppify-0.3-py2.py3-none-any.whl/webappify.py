"""
WebAppify
=========

WebAppify is a simple module to easily create your own desktop apps of websites. WebAppify uses PyQt5 and QtWebKit or
QtWebEngine for displaying the web page, and works on Python 2.7 and Python 3.4 and up.

To create your own desktop web app, import and set up the WebApp class.

.. code:: python

   from webappify import WebApp

   app = WebApp('OpenStreetMap', 'https://www.openstreetmap.org', 'osm.png')
   app.run()

This will create a window with the website, using the icon provided.

.. note::

   If your site needs Flash Player, you'll need the appropriate Flash Player plugin installed system-wide. For QtWebKit
   you will need the NPAPI plugin, and for QtWebEngine you will need the PPAPI plugin.
"""
import sys
import platform

from PyQt5 import QtCore, QtGui, QtWidgets

IS_PY2 = sys.version_info[0] == 2

try:
    from PyQt5 import QtWebEngineWidgets
    HAS_WEBENGINE = True
except ImportError:
    HAS_WEBENGINE = False

try:
    from PyQt5 import QtWebKit, QtWebKitWidgets
    HAS_WEBKIT = True
except ImportError:
    HAS_WEBKIT = False

if HAS_WEBENGINE:
    SETTINGS = [
        QtWebEngineWidgets.QWebEngineSettings.PluginsEnabled,
        QtWebEngineWidgets.QWebEngineSettings.JavascriptCanAccessClipboard,
        QtWebEngineWidgets.QWebEngineSettings.LocalContentCanAccessRemoteUrls
    ]
    WebView = QtWebEngineWidgets.QWebEngineView
elif HAS_WEBKIT:
    SETTINGS = [
        QtWebKit.QWebSettings.PluginsEnabled,
        QtWebKit.QWebSettings.JavascriptCanOpenWindows,
        QtWebKit.QWebSettings.JavascriptCanCloseWindows,
        QtWebKit.QWebSettings.JavascriptCanAccessClipboard,
        QtWebKit.QWebSettings.OfflineStorageDatabaseEnabled,
        QtWebKit.QWebSettings.OfflineWebApplicationCacheEnabled,
        QtWebKit.QWebSettings.LocalStorageEnabled,
        QtWebKit.QWebSettings.LocalContentCanAccessRemoteUrls
    ]
    WebView = QtWebKitWidgets.QWebView

    class WebPage(QtWebKitWidgets.QWebPage):
        """Custom class for overriding the user agent to make WebKit look like Chrome"""
        def userAgentForUrl(self, url):
            return 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                   'Chrome/28.0.1500.52 Safari/537.36'
else:
    print('Cannot detect either QtWebEngine or QtWebKit!')
    sys.exit(1)


class WebWindow(QtWidgets.QWidget):
    """
    A window with a single web view and nothing else
    """
    def __init__(self, app, title, url, icon, canMinimizeToTray=False):
        """
        Create the window
        """
        super(WebWindow, self).__init__(None)
        self.hasShownWarning = False
        self.app = app
        self.icon = QtGui.QIcon(icon)
        self.canMinimizeToTray = canMinimizeToTray
        self.setWindowTitle(title)
        self.setWindowIcon(self.icon)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.webview = WebView(self)
        if not HAS_WEBENGINE and HAS_WEBKIT:
            self.webview.setPage(WebPage(self.webview))
        for setting in SETTINGS:
            self.webview.settings().setAttribute(setting, True)
        self.webview.setUrl(QtCore.QUrl(url))
        self.layout.addWidget(self.webview)
        self.webview.titleChanged.connect(self.onTitleChanged)

    def _showWarning(self):
        """
        Show a balloon message to inform the user that the app is minimized
        """
        if not self.hasShownWarning:
            self.trayIcon.showMessage(self.windowTitle(), 'This program will continue running in the system tray. '
                                      'To close the program, choose <b>Quit</b> in the context menu of the system '
                                      'tray icon.', QtWidgets.QSystemTrayIcon.Information, 5000)
            self.hasShownWarning = True

    def _updateTrayMenu(self):
        """
        Update the enabled/disabled status of the items in the tray icon menu
        """
        if not self.canMinimizeToTray:
            return
        self.restoreAction.setEnabled(not self.isVisible())
        self.minimizeAction.setEnabled(self.isVisible() and not self.isMinimized())
        self.maximizeAction.setEnabled(self.isVisible() and not self.isMaximized())

    def _raiseWindow(self):
        """
        Raise the Window, depending on the version of Python
        """
        # Get the "raise" method depending on Python 2 or 3
        if IS_PY2:
            raiser = getattr(self, 'raise_')
        else:
            raiser = getattr(self, 'raise')
        raiser()

    def _restoreWindow(self):
        """
        Restore the window and activate it
        """
        self.showNormal()
        self.activateWindow()
        self._raiseWindow()

    def _maximizeWindow(self):
        """
        Restore the window and activate it
        """
        self.showMaximized()
        self.activateWindow()
        self._raiseWindow()

    def _getTrayMenu(self):
        """
        Create and return the menu for the tray icon
        """
        # Create the actions for the menu
        self.restoreAction = QtWidgets.QAction('&Restore', self)
        self.restoreAction.triggered.connect(self._restoreWindow)
        self.minimizeAction = QtWidgets.QAction('Mi&nimize', self)
        self.minimizeAction.triggered.connect(self.close)
        self.maximizeAction = QtWidgets.QAction('Ma&ximize', self)
        self.maximizeAction.triggered.connect(self._maximizeWindow)
        self.quitAction = QtWidgets.QAction('&Quit', self)
        self.quitAction.triggered.connect(self.app.quit)
        # Create the menu and add the actions
        trayIconMenu = QtWidgets.QMenu(self)
        trayIconMenu.addAction(self.restoreAction)
        trayIconMenu.addAction(self.minimizeAction)
        trayIconMenu.addAction(self.maximizeAction)
        trayIconMenu.addSeparator()
        trayIconMenu.addAction(self.quitAction)
        return trayIconMenu

    def setupTrayIcon(self):
        """
        Set up the tray icon
        """
        self.trayIcon = QtWidgets.QSystemTrayIcon(self.icon, self)
        self.trayIcon.setContextMenu(self._getTrayMenu())
        self.trayIcon.activated.connect(self.onTrayIconActivated)
        self.trayIcon.show()

    def closeEvent(self, event):
        """
        Override the close event to minimize to the tray
        """
        # If we don't want to minimize to the tray, just close the window as per usual
        if not self.canMinimizeToTray:
            super(WebWindow, self).closeEvent(event)
            return
        # If we want to minimize to the tray, then just hide the window
        if platform.platform().lower() == 'darwin' and (not event.spontaneous() or not self.isVisible()):
            return
        else:
            self._showWarning()
            self.hide()
            event.ignore()
        # Update the menu to match
        self._updateTrayMenu()

    def showEvent(self, event):
        """
        Override the show event to catch max/min/etc events and update the tray icon menu accordingly
        """
        super(WebWindow, self).showEvent(event)
        self._updateTrayMenu()

    def hideEvent(self, event):
        """
        Override the hide event to catch max/min/etc events and update the tray icon menu accordingly
        """
        super(WebWindow, self).hideEvent(event)
        self._updateTrayMenu()

    def changeEvent(self, event):
        """
        Catch the minimize event and close the form
        """
        if self.canMinimizeToTray:
            if event.type() == QtCore.QEvent.WindowStateChange and self.windowState() & QtCore.Qt.WindowMinimized:
                self.close()
        super(WebWindow, self).changeEvent(event)

    def onTitleChanged(self, title):
        """
        React to title changes
        """
        if title:
            self.setWindowTitle(title)
            if self.canMinimizeToTray:
                self.trayIcon.setToolTip(title)

    def onTrayIconActivated(self, reason):
        """
        React to the tray icon being activated
        """
        if reason == QtWidgets.QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.close()
            else:
                self.showNormal()


class WebApp(QtWidgets.QApplication):
    """
    A generic application to open a web page in a desktop app
    """
    def __init__(self, title, url, icon, canMinimizeToTray=False):
        """
        Create an application which loads a URL into a window
        """
        super(WebApp, self).__init__(sys.argv)
        self.window = None
        self.trayIcon = None
        self.title = title
        self.url = url
        self.icon = icon
        self.canMinimizeToTray = QtWidgets.QSystemTrayIcon.isSystemTrayAvailable() and canMinimizeToTray
        if self.canMinimizeToTray:
            self.setQuitOnLastWindowClosed(False)
        self.setWindowIcon(QtGui.QIcon(self.icon))
        self.setApplicationName(title)
        self.setApplicationDisplayName(title)

    def run(self):
        """
        Set up the window and the tray icon, and run the app
        """
        self.window = WebWindow(self, self.title, self.url, self.icon, self.canMinimizeToTray)
        if self.canMinimizeToTray:
            self.window.setupTrayIcon()
        self.window.showMaximized()
        # Get the "exec" method depending on Python 2 or 3
        if IS_PY2:
            runner = getattr(self, 'exec_')
        else:
            runner = getattr(self, 'exec')
        return runner()
