# -*- coding: utf-8 -*-

# Eyegrade: grading multiple choice questions with a webcam
# Copyright (C) 2010-2016 Jesus Arias Fisteus
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/>.
#
from __future__ import division

import gettext
import os.path

from PyQt5.QtGui import (QVBoxLayout, QGroupBox, QCheckBox,
                         QWizard, QWizardPage, QFormLayout,
                         QTabWidget, QWidget, QHBoxLayout,
                         QScrollArea, QGroupBox,
                         QRadioButton, QButtonGroup,
                         QGridLayout, QListWidget, QListWidgetItem, QColor)
from PyQt5.QtCore import Qt

from .. import utils
from . import widgets
from . import dialogs
from . import FileNameFilters

t = gettext.translation('eyegrade', utils.locale_dir(), fallback=True)
_ = t.ugettext


class PageInitial(QWizardPage):
    """First page of WizardNewSession.

    It asks for the directory in which the session has to be stored and
    the exam config file.

    """
    def __init__(self):
        super(PageInitial, self).__init__()
        self.setTitle(_('Full exam or answer sheet'))
        self.setSubTitle(_('You can create a full exam with questions, '
                           'create just the answer sheet '
                           'or export the answer table as an image.'))
        self.radio_full_exam = QRadioButton(parent=self)
        self.radio_answer_sheet = QRadioButton(parent=self)
        self.radio_image = QRadioButton(parent=self)
        self.radio_full_exam.setText(_('Create a full exam from '
                                       'a questions XML file'))
        self.radio_answer_sheet.setText(_('Create just an answer sheet'))
        self.radio_image.setText(_('Export the answer table as image'))
        self.radio_full_exam.setChecked(True)
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.addWidget(self.radio_full_exam)
        layout.addWidget(self.radio_answer_sheet)
        layout.addWidget(self.radio_image)

    def validatePage(self):
        """Called by QWizardPage to check the values of this page."""
        return True

    def nextId(self):
        if (self.radio_answer_sheet.isChecked()
            or self.radio_image.isChecked()):
            return WizardCreateExam.PageAnswerTable
        else:
            return WizardCreateExam.PageExamDirectory


class PageAnswerTable(QWizardPage):
    """Create just an answer sheet

    It asks for several creation options.

    """
    def __init__(self):
        super(PageAnswerTable, self).__init__()
        self.setTitle(_('Answer table options'))
        self.setSubTitle(_('Configure the number of questions, '
                           'number of choices per question '
                           'and number of exam models.'))
        layout = QFormLayout(self)
        self.num_questions = widgets.InputInteger(initial_value=10,
                                                  min_value=1,
                                                  max_value=100)
        self.num_choices = widgets.InputInteger(initial_value=3,
                                                min_value=2,
                                                max_value=8)
        self.num_models = widgets.InputInteger(initial_value=1,
                                               min_value=1,
                                               max_value=8)
        layout.addRow(_('Number of questions'), self.num_questions)
        layout.addRow(_('Number of choices per question'), self.num_choices)
        layout.addRow(_('Number of models of the exam'), self.num_models)

    def nextId(self):
        return WizardCreateExam.PageComponents


class PageComponents(QWizardPage):
    """Create just an answer sheet

    It asks for several creation options.

    """
    def __init__(self):
        super(PageComponents, self).__init__()
        self.setTitle(_('Optional elements and labels'))
        self.setSubTitle(_('Select the optional elements and text labels'))
        self.institution = widgets.LabelGroupBox(self, _('Institution name'))
        self.subject = widgets.LabelGroupBox(self, _('Subject name'))
        self.subtitle_1 = widgets.LabelGroupBox(self, _('Exam subtitle 1'))
        self.subtitle_2 = widgets.LabelGroupBox(self, _('Exam subtitle 2'))
        self.date = widgets.LabelGroupBox(self, _('Date'))
        self.name = widgets.LabelGroupBox( \
                                    self,
                                    _('Student name box'),
                                    checked=True,
                                    default=_('Name:'))
        self.id_number = widgets.LabelGroupBox( \
                                    self,
                                    _('Student id box'),
                                    checked=True,
                                    default=_('ID:'))
        self.id_number.addExtraField('num_digits',
                                     _('Number of digits:'),
                                     widgets.InputInteger(initial_value=8,
                                                          min_value=5))
        self.signature = widgets.LabelGroupBox( \
                                    self,
                                    _('Signature box'),
                                    checked=True,
                                    default=_('Signature:'))
        layout = QVBoxLayout(self)
        layout.addWidget(self.institution)
        layout.addWidget(self.subject)
        layout.addWidget(self.subtitle_1)
        layout.addWidget(self.subtitle_2)
        layout.addWidget(self.date)
        layout.addWidget(self.name)
        layout.addWidget(self.id_number)
        layout.addWidget(self.signature)

    def nextId(self):
        return 0


class WizardCreateExam(QWizard):
    """Wizard for the creation of exams.


    """
    (PageInitial, PageAnswerTable, PageComponents,
     PageExamDirectory, ) = range(4)

    def __init__(self, parent, config_filename=None):
        super(WizardCreateExam, self).__init__(parent)
        self.exam_config = None
        self.setWindowTitle(_('Create an exam'))
        self.page_initial = PageInitial()
        self.page_answer_table = PageAnswerTable()
        self.page_components = PageComponents()
        self.setPage(self.PageInitial, self.page_initial)
        self.setPage(self.PageAnswerTable, self.page_answer_table)
        self.setPage(self.PageComponents, self.page_components)
        self.setStartId(self.PageInitial)

    def values(self):
        values = {}
        return values
