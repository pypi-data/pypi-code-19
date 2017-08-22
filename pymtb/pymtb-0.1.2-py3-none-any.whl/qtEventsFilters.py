from PyQt5.QtCore import QObject, pyqtSignal, QEvent
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget

__all__ = ["grabHover"]

def grabHover(widget):
    """
    EventFilter that sends signal when mouse is over the widget using grabKeyboard()
    :param widget:
    :return: filtered widget
    """

    class Filter(QObject):
        tabPressed = pyqtSignal(QWidget)

        def mouseInWidget(self,w):
            a = w.mapFromGlobal(QCursor.pos())

            if a.x() < 0 or a.x() > w.width() or a.y() < 0 or a.y() > w.height():
                return False

            return a


        def eventFilter(self, obj, event):

            if obj == widget:
                if self.mouseInWidget(obj):
                    obj.grabKeyboard()
                if event.type() == QEvent.KeyPress:

                    if event.key() == 16777217:
                            self.tabPressed.emit(obj)
                            return True

            return QWidget.eventFilter(self, obj, event)

    filter = Filter(widget)
    widget.installEventFilter(filter)
    #return filter.tabPressed
    return filter
