#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A Qt based DICOM server browser dialog.
"""

from __future__ import print_function, division, absolute_import
from datetime import datetime
import tempfile
from shutil import rmtree
from glob import glob
from os.path import join, isdir
import platform


try:
    from . aettable import AetTable
    from . import queryinterface as qi
except SystemError:
    try:
        from aettable import AetTable
        import queryinterface as qi
    except SystemError:
        from dcmfetch.aettable import AetTable
        import dcmfetch.queryinterface as qi

# user interface

from qtpy.QtWidgets import (
    QTreeWidget, QPushButton, QDialog, QLabel, QComboBox,
    QLineEdit, QProgressBar, QMenu, QStatusBar,
    QMessageBox, QTreeWidgetItem,
    QHBoxLayout, QVBoxLayout, QApplication
)
from qtpy.QtCore import Qt, Signal


def dicom_date_as_slplan(ansidate):
    ''' Dicom (ansi) date formatted in the 'slplan' 01-Jan-1999 style.
    '''
    if not ansidate:
        return '??-bad-date'
    try:
        dtime = datetime.strptime(ansidate.strip(), '%Y%m%d')
    except ValueError:
        try:
            dtime = datetime.strptime(ansidate.strip(), '%Y-%m-%d')
        except ValueError:
            return '??-???-????'

    # strftime in python 2 can't handle dates earlier than 1900
    return datetime.strftime(dtime, '%d-%b-%Y') if dtime.year >= 1900 else '??-???-????'


def dicom_patname_as_slplan(patientname):
    ''' Dicom (ansi) patient name formatted in the 'slplan' Bloggs, Joe style.
        Handles case where original name is already in slplan form or is not structured,
    '''
    FIELDSIZE = 28

    # if we have ansi delimiter characters
    if '^' in patientname:
        #
        # Ansi patient names are in form:
        #       lastname^firstname^middlename^title^suffix
        #
        patientname = patientname.strip()
        fields = patientname.split('^')
        lastname = fields[0]
        firstname = fields[1]
    elif ',' in patientname:
        # work around for improperly formatted patient names
        patientname = patientname.strip()
        fields = patientname.split(',')
        fields = [field.strip() for field in fields]
        lastname = fields[0]
        firstname = fields[1]
    else:
        #
        # If no delimiters at all treat as a lastname only.
        # This means that we do nothing with names
        # like "Joe Bloggs" as we have no reasonable
        # way of distinguishing it from "Bloggs Joe".
        # This behaviour is also right for phantoms
        # and things that don't have compound names.
        #
        lastname = patientname.strip()
        firstname = ''

    if firstname:
        formattedstring = ', '.join((lastname, firstname))
    else:
        formattedstring = lastname
    if len(formattedstring) > FIELDSIZE:
        formattedstring = formattedstring[0:FIELDSIZE]
    return formattedstring


class TreeWidgetWithPopUp(QTreeWidget):
    """ Helper class - a QTreeWidget but with an added background popup menu
    """

    def __init__(self, parent=None):
        QTreeWidget.__init__(self, parent)
        self._popup = None

    def set_popup(self, menu):
        self._popup = menu

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton and self._popup is not None:
            self._popup.exec_(event.globalPos())
        QTreeWidget.mousePressEvent(self, event)


class FetchDialog(QDialog):
    '''
    * Dicom fetch dialog class.
    * Dialog consists of cancel, find and fetch buttons,
    * a pull down menu of dicom servers, three query specification fields,
    * listboxes for patients and for the series belonging to the selected patient.
    * There is also progress bar for image transfer. The formatting of the items
    * in the listboxes may be modified using the pop up menus associated with them.
    * The queries and the move requests are done via a QueryInterface object. The
    * dicom server names are obtained from an external table.
    '''
    fetchStarting = Signal()
    fetchContinuing = Signal()
    fetchComplete = Signal()
    fetchFailed = Signal()

    slbtitlesa = ["Study ID", "Study Date", "Series", "Modality", "Images", "Description"]
    slbtitlesb = ["Study ID", "Study Date", "Series", "Modality", "Images", "Description"]
    DFLT_LOCAL_AET = platform.node().split('.')[0].replace('-', '')[:11] + 'Store'

    def __init__(self, aetfile=None, local_aet=None, parent=None):
        '''Constructs user interface components in dialog and sets up signal/slots.
        '''
        super(FetchDialog, self).__init__(parent)

        try:
            self.nodetable = AetTable(aetfile)
        except IOError as e:
            raise ValueError('No dicom nodes file (%s)' % e)

        if len(list(self.nodetable.keys())) < 1:
            raise ValueError('No valid entries configured in dicom nodes file %s' % aetfile)

        self.local_aet = local_aet if local_aet is not None else self.DFLT_LOCAL_AET
        self.qinterface = qi.QueryInterface(self.nodetable, self.local_aet)
        self.series_filename = ""

        self._patListValid = False
        self._seriesListValid = False
        self._fetchOK = False
        self._formatPatNames = True

        self._patresponses = []
        self._comboresponses = []
        self._imagefiles = []
        self._tempdir = None

        toplevel = QVBoxLayout()
        buttonbox = QHBoxLayout()

        # upper section - controls
        self._cancelbtn = QPushButton(self.tr("&Cancel"))
        self._cancelbtn.setAutoDefault(False)
        buttonbox.addWidget(self._cancelbtn)
        self._cancelbtn.clicked.connect(self.reject)

        self._findbtn = QPushButton(self.tr("&Find"))
        buttonbox.addWidget(self._findbtn)
        self._findbtn.setAutoDefault(False)
        self._findbtn.clicked.connect(self.find)

        self._serfindbtn = QPushButton("Series Find")
        buttonbox.addWidget(self._serfindbtn)
        self._serfindbtn.setAutoDefault(False)
        self._serfindbtn.hide()  # hidden just to vector kbd return
        self._serfindbtn.clicked.connect(self.series_find)

        self._fetchbtn = QPushButton(self.tr("Fe&tch"))
        buttonbox.addWidget(self._fetchbtn)
        self._fetchbtn.setAutoDefault(False)
        self._fetchbtn.clicked.connect(self.fetch)
        self._fetchbtn.setEnabled(False)

        serverlbl = QLabel("Server:")
        serverlbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        buttonbox.addWidget(serverlbl)
        servercbmo = QComboBox()
        servercbmo.setFrame(True)

        # an ordered dictionary
        for key in self.nodetable:
            if 'F' in self.nodetable[key].facilities:
                servercbmo.addItem(key)
        self.server = list(self.nodetable.keys())[0]

        servercbmo.currentIndexChanged[str].connect(self.set_server)

        buttonbox.addWidget(servercbmo)

        self._progbarlbl = QLabel("Fetching from Server")
        self._progbarlbl.hide()
        self._progbar = QProgressBar()
        self._progbar.setRange(0, 100)
        self._progbar.hide()

        toplevel.addLayout(buttonbox)

        # check dicom node has move to callback configured
        facilities = self.nodetable[self.server].facilities
        self._fetchOK = any(c in facilities for c in 'GCM')

        self._countImages = 'I' in facilities

        # editable text fields - search strings
        entrybox = QHBoxLayout()
        namlbl = QLabel("Name: ")
        self._namtxt = QLineEdit()
        entrybox.addWidget(namlbl)
        entrybox.addWidget(self._namtxt)
        self._namtxt.returnPressed.connect(self.find)

        idlbl = QLabel("PID: ")
        self._idtxt = QLineEdit()
        entrybox.addWidget(idlbl)
        entrybox.addWidget(self._idtxt)
        self._idtxt.returnPressed.connect(self.find)

        doblbl = QLabel("DOB: ")
        self._dobtxt = QLineEdit()
        entrybox.addWidget(doblbl)
        entrybox.addWidget(self._dobtxt)
        self._dobtxt.returnPressed.connect(self.find)
        toplevel.addLayout(entrybox)

        # patient and series listboxes
        self._patlist = TreeWidgetWithPopUp()  # need to set single clickable + send event
        self._patlist.setHeaderLabels(["Patient Name", "Patient ID", "Birth Date", "Sex"])
        toplevel.addWidget(self._patlist)
        self._patlist.activated.connect(self.series_find)

        self._serieslist = TreeWidgetWithPopUp()
        self._serieslist.setHeaderLabels(self.slbtitlesa if self._countImages else self.slbtitlesb)

        self._serieslist.currentItemChanged.connect(self.enable_fetch)
        self._serieslist.activated.connect(self.enable_fetch)

        # need to set double clickable + send event
        toplevel.addWidget(self._serieslist)

        # pop up menu's on listboxes
        self._patfmtmenu = QMenu()  # or cmbo?
        self._patfmtmenu.setTitle("Patient List Format")
        self._patfmtact = self._patfmtmenu.addAction("Cooked Names")
        self._patfmtact.setCheckable(True)
        self._patfmtact.setChecked(self._formatPatNames)
        self._patfmtact.toggled.connect(self.set_format_pat_names)

        self._patlist.set_popup(self._patfmtmenu)

        self._imgcntmenu = QMenu()
        self._imgcntmenu.setTitle("Image List Format")
        self._imgcntact = self._imgcntmenu.addAction("Count Images")
        self._imgcntact.setCheckable(True)
        self._imgcntact.setChecked(self._countImages)
        self._imgcntact.toggled.connect(self.set_count_images)
        self._serieslist.set_popup(self._imgcntmenu)

        statusbar = QStatusBar()
        statusbar.addWidget(QLabel(qi.toolkit))
        statusbar.addWidget(self._progbarlbl)
        statusbar.addWidget(self._progbar)
        statusbar.setSizeGripEnabled(False)

        toplevel.addWidget(statusbar)

        self.setLayout(toplevel)
        # want to set non resizable really ...
        self.setWindowTitle("DICOM Fetch")

        self.fetch_in_progress = False

    def set_local_aet(self, laet):
        '''Sets Calling Application Entity Title to be used for all DICOM Associations
        '''
        self.qinterface.localaet = laet
        self.local_aet = laet

    def set_server(self, apptitle):
        '''Sets the dicom server to query, both here and in the query interface object.
        '''
        apptitle = str(apptitle)
        self.server = apptitle
        facilities = self.nodetable[apptitle].facilities
        self._fetchOK = any(c in facilities for c in 'GCM')
        self._countImages = 'I' in facilities
        self._imgcntact.setChecked(self._countImages)
        self._serieslist.setHeaderLabels(self.slbtitlesa if self._countImages else self.slbtitlesb)

        self._patlist.clear()
        self._serieslist.clear()
        self._seriesListValid = False
        self._patListValid = False
        self._fetchbtn.setEnabled(False)
        self._findbtn.setDefault(True)

    def find(self):
        '''Perform a patient level find and populate upper list box with results.
        '''
        patid = str(self._idtxt.text())
        patname = str(self._namtxt.text())
        patdob = str(self._dobtxt.text())
        if not patid and not patname and not patdob:
            QMessageBox.warning(
                self, "",
                "Please specify a patient name or id (may include wild cards)"
            )
            return

        #
        # check with user if all wild cards used as number of pats
        # on main pacs could be very large
        # (nb back to front buttons is to make "cancel" the (safe) default)
        #
        if ( (not patid or patid == "*") and
             (not patname or patname == "*") and
             (not patdob or patdob == "*")):
            reply = QMessageBox.warning(
                self, "",
                "This will list ALL of the patients on the server",
                QMessageBox.Cancel | QMessageBox.Ok
            )
            if reply != QMessageBox.Ok:
                return

        patsex = '*'
        if patid == "*":
            patid = ""
        if patname == "*":
            patname = ""
        if patdob == "*":
            patdob = ""

        # literal name string implies trailing wild card
        if '*' not in patname:
            patname = patname + '*'

        # perform patient level query (how do we handle errors  ?)
        old_cursor = self.cursor()
        self.setCursor(Qt.WaitCursor)
        try:
            self._patresponses = self.qinterface.pat_level_find(
                self.server,
                patname,
                patid,
                patdob,
                patsex
            )
        except qi.QIError as e:
            self.setCursor(old_cursor)
            QMessageBox.critical(self, "", "Top Level Find Failed (%s)" % e)
            self._patresponses = []
            return
        self.setCursor(old_cursor)

        # load patient list box with results
        self.load_patient_listbox(self._patresponses)

        # default "selection" is first in the list, pat is now valid unless the list is empty
        if len(self._patresponses) > 0:
            # initially selected item is first in list box
            self._selectedPatID = self._patresponses[0].patid
            self._patListValid = True
        else:
            self._patListValid = False

        self._serieslist.clear()
        self._seriesListValid = False

        # grey out fetch and wake up frame
        self._fetchbtn.setEnabled(False)
        self._serfindbtn.setDefault(True)

        return

    def series_find(self):
        '''Perform a study/series level find and populate lower list box with results.
        '''

        # shouldn't have been able to select anything if list is empty
        if len(self._patresponses) < 1:
            QMessageBox.warning(self, "", "No Patients to Select")
            return

        curritem = self._patlist.currentItem()
        if curritem is None:
            QMessageBox.warning(self, "", "No Patient Selected")
            return

        # need to convert from the horrid QVariant type, but not in the new API
        try:
            patid = str(curritem.data(0, Qt.UserRole).toString())
        except AttributeError:
            patid = str(curritem.data(0, Qt.UserRole))

        # pick up pat id from selected row from previous query
        self._selectedPatID = patid

        # require a valid patient id
        if not self._patListValid or self._selectedPatID == "":
            QMessageBox.warning(self, "", "Missing or Invalid Patient")
            return

        # TODO: clear old listing (doesn't seem to work.. appears quite difficult in Qt)
        self.load_series_listbox([])
        QApplication.instance().processEvents()

        # send the study query
        old_cursor = self.cursor()
        self.setCursor(Qt.WaitCursor)
        try:
            self._comboresponses = self.qinterface.combo_find(
                self.server,
                patid,
                self._countImages
            )
        except qi.QIError as e:
            self.setCursor(old_cursor)
            QMessageBox.critical(self, "", "Series Level Find Failed (%s)" % e)
            self._seriesListValid = False
            self._comboresponses = []
            return
        self.setCursor(old_cursor)

        self.load_series_listbox(self._comboresponses)

        # first element in study list will be initially selected if possible
        if len(self._comboresponses) > 0:
            first = self._comboresponses[0]
            self._selectedStudyUID = first.studyuid
            self._selectedSeriesUID = first.seriesuid
            self._selectedSeriesImages = first.nimages
            self._seriesListValid = True

        else:
            self._seriesListValid = False

        return

    def fetch(self):
        '''Fetch selected dicom series. Result is available via get_image_files()
        '''
        if self.fetch_in_progress:
            return
        else:
            self.fetch_in_progress = True

        # no fetch possible if node not configured for move to call back
        if not self._fetchOK:
            QMessageBox.critical(
                self, "",
                "Can't fetch images - dicom node not configured to send images back"
            )
            self.fetch_in_progress = False
            return

        # only perform move if we have definite patient/study
        if not self._seriesListValid or not self._patListValid:
            QMessageBox.warning(self, "", "Select a Patient and a Series First")
            self.fetch_in_progress = False
            return

        assert self._comboresponses

        curritem = self._serieslist.currentItem()
        if curritem is None:
            QMessageBox.warning(self, "", "No Series Selected")
            self.fetch_in_progress = False
            return

        # need to convert from horrid QVariant type in V1, no problem in V2
        try:
            uids = [str(curritem.data(i, Qt.UserRole).toString()) for i in [0, 1]]
        except AttributeError:
            uids = [str(curritem.data(i, Qt.UserRole)) for i in [0, 1]]

        self._selectedStudyUID = uids[0]
        self._selectedSeriesUID = uids[1]

        # this will be used as a hint to fetch of the number of images to expect
        try:
            try:
                self._selectedSeriesImages = int(curritem.data(2, Qt.UserRole).toString())
            except AttributeError:
                self._selectedSeriesImages = int(curritem.data(2, Qt.UserRole))
        except (TypeError, ValueError):
            self._selectedSeriesImages = -1

        # construct a series name to be used if we want to save a a file
        studyid, seriesno = str(curritem.text(0)), str(curritem.text(2))
        self.series_filename = '%s-%s-%s' % (self._selectedPatID.strip(), studyid.strip(), seriesno.strip())

        # sanity check - nb: _selectedSeriesImages will be -1 if we were not counting them
        if self._selectedSeriesImages < 1 and self._countImages:
            reply = QMessageBox.warning(
                self, "",
                "Series doesn't appear to have any images",
                QMessageBox.Cancel | QMessageBox.Ok
            )
            if reply != QMessageBox.Ok:
                self.fetch_in_progress = False
                return

        self._progbar.setValue(0)
        self._progbarlbl.show()
        self._progbar.show()
        QApplication.processEvents()

        # initial callback
        self.fetchStarting.emit()
        self.free_image_files()
        self._tempdir = tempfile.mkdtemp(prefix='dcmqr-tmp')
        old_cursor = self.cursor()
        self.setCursor(Qt.WaitCursor)
        try:
            fetchiter = self.qinterface.series_level_fetch(
                self.server,
                self._selectedPatID,
                self._selectedStudyUID,
                self._selectedSeriesUID, self._tempdir
            )
            # series_level_fetch should take account of our hint and return sensible values here
            for (ncomplete, nremaining) in fetchiter:
                if nremaining >= 0:
                    # we got a full cget reposonse rather than just a cstore
                    self._selectedSeriesImages = ncomplete + nremaining

                if ncomplete < self._selectedSeriesImages:
                    self._progbar.setValue(100 * ncomplete / self._selectedSeriesImages)
                else:
                    self._progbar.setValue(100)
                self.fetchContinuing.emit()
                QApplication.processEvents()

        except qi.QIError as e:
            QMessageBox.critical(self, "", "Transfer Failed - problem with Dicom Fetch (%s)" % e)
            self.fetchFailed.emit()
            self._progbarlbl.hide()
            self._progbar.hide()
            self.free_image_files()
            self.setCursor(old_cursor)
            self.fetch_in_progress = False
            return

        self.setCursor(old_cursor)

        # get list of image files to return (nb not sorted yet...)
        self._imagefiles = glob(join(self._tempdir, '*'))

        if len(self._imagefiles) < 1:
            QMessageBox.critical(self, "", "No images - problem with Dicom Fetch")
            self.fetchFailed.emit()
            self._progbarlbl.hide()
            self._progbar.hide()
            self._imagefiles = []
            self.fetch_in_progress = False
            return

        self.fetchComplete.emit()

        self._patlist.clear()
        self._serieslist.clear()
        self._seriesListValid = False
        self._patListValid = False
        self._fetchbtn.setEnabled(False)
        self._progbar.setValue(0)
        self._progbarlbl.hide()
        self._progbar.hide()
        self.accept()
        self.fetch_in_progress = False
        return

    def set_count_images(self, enablestate=True):
        '''Enable/disable counting of images using image level queries
        '''
        self._serieslist.setHeaderLabels(self.slbtitlesa if enablestate else self.slbtitlesb)
        self._countImages = enablestate

        if self._seriesListValid:
            self._serieslist.clear()
            self._seriesListValid = False
            self.series_find()

    def set_format_pat_names(self, enablestate=True):
        '''Enable/disable formatting of patient names in "surname, forename" form
        '''
        self._formatPatNames = enablestate

        #
        # load patient list box with results
        #
        self.load_patient_listbox(self._patresponses)

        #
        # default "selection" is first in the list, pat is now valid
        # unless the list is empty
        #
        if len(self._patresponses) > 0:
            # initially selected item is first in list box
            self._selectedPatID = self._patresponses[0].patid
            self._patListValid = True
        else:
            self._patListValid = False

        self._serieslist.clear()
        self._seriesListValid = False

    def enable_fetch(self):
        '''Enable buttons for fetch operation
        '''
        if self._seriesListValid and self._serieslist.currentItem() is not None:
            self._fetchbtn.setEnabled(True)
            self._fetchbtn.setDefault(True)
        else:
            self._fetchbtn.setDefault(False)
            self._findbtn.setDefault(True)

    def load_patient_listbox(self, patresponselist):
        '''Load the patient list box using a list of patient response records
        '''
        self._patlist.clear()
        for patient in patresponselist:
            fields = []
            if self._formatPatNames:
                fields.append(dicom_patname_as_slplan(patient.patname))
            else:
                fields.append(patient.patname)
            fields.append(patient.patid)
            fields.append(dicom_date_as_slplan(patient.dob))
            fields.append(patient.sex)

            # item = QTreeWidgetItem(self._patlist, QStringList(fields))
            item = QTreeWidgetItem(self._patlist, fields)
            item.setData(0, Qt.UserRole, patient.patid)
            self._patlist.addTopLevelItem(item)  # make not selected ?

        for i in range(self._patlist.columnCount()):
            self._patlist.resizeColumnToContents(i)

    def load_series_listbox(self, comboresponselist):
        '''Load the series list box using a list of series (combo) response records
        '''
        self._serieslist.clear()
        for combo in comboresponselist:
            fields = []
            fields.append(combo.studyid)
            fields.append(dicom_date_as_slplan(combo.studydate))
            fields.append('%d' % combo.seriesnumber)
            fields.append(combo.modality)

            if combo.nimages is None:
                fields.append('----')
            elif combo.firstimageno is None or combo.lastimageno is None:
                fields.append("%d" % combo.nimages)
            elif combo.nimages < 1:
                # should happen really but print out anyway
                fields.append("%d" % combo.nimages)
            elif combo.nimages == 1:
                fields.append("%d [%d]" % (combo.nimages, combo.firstimageno))
            else:
                fields.append(
                    "%d [%d-%d]" %
                    (combo.nimages, combo.firstimageno, combo.lastimageno)
                )

            fields.append(combo.description)
            item = QTreeWidgetItem(self._serieslist, fields)
            item.setData(0, Qt.UserRole, combo.studyuid)
            item.setData(1, Qt.UserRole, combo.seriesuid)
            item.setData(2, Qt.UserRole, combo.nimages)
            self._serieslist.addTopLevelItem(item)

        if len(comboresponselist) > 0:
            for i in range(self._serieslist.columnCount()):
                self._serieslist.resizeColumnToContents(i)

    def get_image_files(self):
        '''Return the list of dicom object files obtained from the last fetch operation
        '''
        return self._imagefiles

    def get_thumbnail(self):
        '''Return a thumbnail image representing the last series obtained
        '''
        return None

    def free_image_files(self):
        '''Remove the temporary image files
        '''
        self._imagefiles = []
        if self._tempdir and isdir(self._tempdir):
            rmtree(self._tempdir)
        self._tempdir = None


if __name__ == '__main__':
    import sys
    from zipfile import ZipFile, is_zipfile, ZIP_STORED
    from tempfile import mkdtemp

    print("Testing with python %s" % sys.version)
    app = QApplication(sys.argv)
    dlg = FetchDialog()
    dlg.show()
    app.exec_()
    if dlg.result() == QDialog.Accepted:
        print("Received %d images in %s" % (len(dlg.get_image_files()), dlg._tempdir))
        savedir = mkdtemp()
        arcname = dlg.series_filename
        savefile = join(savedir, arcname + ".zip")
        # Compression causes a sigsegv in anaconda 1.8 with python reverted to 2.7.5=2
        # But if we use 2.7.6=0 or 2.7.5=3 we get an unresolved symbol in cairo.
        # zipf = zipfile.ZipFile(savefile, "w", compression=ZIP_DEFLATED, allowZip64=True)
        zipf = ZipFile(savefile, "w", compression=ZIP_STORED, allowZip64=True)
        for (n, pathelement) in enumerate(dlg.get_image_files()):
            archfile = "%s/%05d.dcm" % (arcname, n + 1)
            zipf.write(pathelement, archfile)
        zipf.close()
        print("Zip written to", savefile)
        assert is_zipfile(savefile)
        zipf = ZipFile(savefile)
        for name in zipf.namelist():
            print(name)
        rmtree(savedir, ignore_errors=True)
    else:
        print('Dialog cancelled')
    dlg.free_image_files()
    print("Done")
