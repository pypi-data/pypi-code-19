#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A DICOM server browser and fetch tool dialog
"""

from __future__ import print_function, division, absolute_import
import sys
import os.path
import zipfile


# user interface
from qtpy.QtWidgets import (
    QPushButton, QDialog, QMessageBox,
    QApplication, QGridLayout,
)
from qtpy.QtCore import QTimer
from qtpy.compat import getsavefilename

try:
    from . fetchdialog import FetchDialog
    from . version import __version__
except (ValueError, ImportError):
    from dcmfetch.fetchdialog import FetchDialog
    from dcmfetch.version import __version__


class TopLevel(QDialog):
    def __init__(self, aetfile=None, savedir=None, parent=None):
        super(TopLevel, self).__init__(parent)
        self._fetchBtn = QPushButton("Fetch")

        self._saveBtn = QPushButton("Save")

        self._quitBtn = QPushButton("Quit")

        self._fetchBtn.clicked.connect(self.fetch)
        self._saveBtn.clicked.connect(self.save)
        self._quitBtn.clicked.connect(self.reject)

        self._fetchBtn.setEnabled(True)
        self._saveBtn.setEnabled(False)
        self._quitBtn.setEnabled(True)

        grid = QGridLayout()
        grid.addWidget(self._fetchBtn, 0, 0)
        grid.addWidget(self._saveBtn, 0, 1)
        grid.addWidget(self._quitBtn, 0, 2)
        self.setLayout(grid)
        self._fetchDlg = FetchDialog(parent=self, aetfile=aetfile)
        self._suggestedFile = ""
        self._fileList = []
        if savedir is not None:
            self._saveDir = savedir
        else:
            self._saveDir = os.getenv('USERPROFILE') or os.getenv('HOME')

    def fetch(self):
        self._fetchDlg.exec_()
        if self._fetchDlg.result() == QDialog.Accepted:
            self._suggestedFile = self._fetchDlg.series_filename
            self._fileList = self._fetchDlg.get_image_files()
            self._saveBtn.setEnabled(True)
        else:
            self._saveBtn.setEnabled(False)

    def save(self):
        if self._suggestedFile and self._fileList:
            suggested_path = os.path.join(self._saveDir, self._suggestedFile + ".zip")
            savefile, _ = getsavefilename(self, "Save Zip File", suggested_path, '*.zip')
            if not savefile:
                return
            try:
                # was: compression=zipfile.ZIP_DEFLATED, but caused sigsegv on anaconda
                zipf = zipfile.ZipFile(savefile, "w", compression=zipfile.ZIP_STORED, allowZip64=True)
                for (n, pathelement) in enumerate(self._fileList):
                    archfile = "%s/%05d.dcm" % (self._suggestedFile, n + 1)
                    zipf.write(pathelement, archfile)
                zipf.close()
            except IOError as e:
                print('Save File: IOError! (%s)' % e, file=sys.stderr)
                return

            self._saveBtn.setEnabled(False)
            self._fetchDlg.free_image_files()
            self._suggestedFile = ""
            self._fileList = []
            self._saveDir = os.path.dirname(savefile)

    def checkSave(self):
        if self._fileList:
            msgBox = QMessageBox()
            msgBox.setText("The series has not been saved.")
            msgBox.setInformativeText("Do you want to save it now?")
            msgBox.setStandardButtons(QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
            msgBox.setDefaultButton(QMessageBox.Save)

        while self._fileList:
            ret = msgBox.exec_()
            if ret == QMessageBox.Save:
                self.save()
            elif ret == QMessageBox.Discard:
                self._fetchDlg.free_image_files()
                self._suggestedFile = ""
                self._fileList = []
                return True
            else:
                return False
        return True

    def reject(self):
        if self.checkSave():
            self.close()

    def closeEvent(self, event):
        if self.checkSave():
            super(TopLevel, self).closeEvent(event)
            event.accept()
        else:
            event.ignore()


def main():
    from argparse import ArgumentParser, ArgumentTypeError
    from signal import signal, SIGINT
    from os.path import isdir, normpath, abspath
    from os import access, W_OK, X_OK

    def output_directory(string):
        ''' Argparse type handler for an output directory to write DICOM files to.
            Returns an absolute path.
        '''
        path = normpath(abspath(string))
        if not isdir(path):
            raise ArgumentTypeError('the output directory "%s" must exist already' % string)
        if not access(path, W_OK | X_OK):
            raise ArgumentTypeError('the output directory "%s" must be writable' % string)
        return path

    parser = ArgumentParser(
        description='Fetch DICOM series from Archive Server'
    )
    parser.add_argument(
        '-V', '--version',
        action='version', version='%%(prog)s %s' % __version__
    )
    parser.add_argument(
        '-o', '--out', action='store',
        type=output_directory, help='Output directory to store series in'
    )

    args = parser.parse_args()

    try:
        app = QApplication(sys.argv)

        # Boiler-plate code to handle Ctrl-C cleanly
        t = QTimer(); t.start(500); t.timeout.connect(lambda: None)
        signal(SIGINT, lambda sig, frame: QApplication.quit())

        toplevel = TopLevel(savedir=args.out)
        toplevel.show()
        app.exec_()
    except Exception as e:
        print('Top level exception: %s' % e, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
