from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99
from . import WBase
import os

__all__ = ["WSelectDir", "WSelectFile"]


class _WSelectFileOrDir(WBase):
    @property
    def value(self):
        return self._get_value()

    # Emitted whenever the valu property changes **to a valid value**
    valueChanged = pyqtSignal()

    def __init__(self, *args, dialog_title="", dialog_path=".", dialog_wild="*"):
        a99.WBase.__init__(self, *args)

        self._last_value = None

        self._type = None
        self.dialog_title = dialog_title
        self.dialog_path = dialog_path
        self.dialog_wild = dialog_wild

        lw = QHBoxLayout()
        a99.set_margin(lw, 0)
        lw.setSpacing(4)
        self.setLayout(lw)

        # t = self.label = self.keep_ref(QLabel())
        # lw.addWidget(t)

        e = self.edit = QLineEdit()
        e.textChanged.connect(self.edit_changed)
        lw.addWidget(e)
        # e.setReadOnly(True)

        b = self.button = QToolButton()
        b.clicked.connect(self.on_button_clicked)
        lw.addWidget(b)
        b.setFixedWidth(30)

        # Forces paint red if invalid
        self.edit_changed()

    def on_button_clicked(self, _):
        self._on_button_clicked()

    def edit_changed(self):
        flag_valid = self.validate()
        a99.style_widget_valid(self.edit, not flag_valid)
        if flag_valid:
            self._wanna_emit()

    def validate(self):
        """Returns True/False whether value is valid, i.e., existing file or directory"""
        return self._validate()

    def _wanna_emit(self):
        value_now = self._get_value()
        if value_now != self._last_value:
            self._last_value = value_now
            self.valueChanged.emit()

    def _get_value(self):
        return self.edit.text().strip()


class WSelectFile(_WSelectFileOrDir):
    def __init__(self, *args, **kwargs):
        _WSelectFileOrDir.__init__(self, *args, **kwargs)
        # self.label.setText("&File")
        self.button.setIcon(a99.get_icon("document-open"))

    def _on_button_clicked(self):
        path_ = self.edit.text().strip()
        if len(path_) == 0:
            path_ = self.dialog_path
        res = QFileDialog.getOpenFileName(self, self.dialog_title, path_,
                                          self.dialog_wild)[0]
        if res:
            self.edit.setText(res)
            self.dialog_path = res

    def _validate(self):
        return os.path.isfile(self.value)


class WSelectDir(_WSelectFileOrDir):
    def __init__(self, *args, **kwargs):
        _WSelectFileOrDir.__init__(self, *args, **kwargs)
        self.button.setIcon(a99.get_icon("folder-change"))
        self.edit.setText(self.dialog_path)

    def _on_button_clicked(self):
        path_ = self.edit.text().strip()
        if len(path_) == 0:
            path_ = self.dialog_path
        res = QFileDialog.getExistingDirectory(self, self.dialog_title, path_)
        if len(res) > 0:
            self.edit.setText(res)
            self.dialog_path = res

    def _validate(self):
        return os.path.isdir(self.value)
