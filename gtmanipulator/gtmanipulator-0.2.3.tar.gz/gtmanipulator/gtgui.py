try:
    import sys
    import gtmanipulator as gt
    import datetime
    from PyQt5 import QtCore
    from PyQt5 import QtGui
    from PyQt5 import QtWidgets
except ImportError:
    print("Verify that PyQt5 and the gtmanipulator packages are" 
          " properly installed or download\n"
          "the compiled executable version of this program.")

class GtGui(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.action_log = []
        self.last_action = -1
        self.active_file = None
        self.data = None
        self.worker = None
        # Main Window Setup
        self.setWindowTitle("GtGUI - New Project")
        self.resize(600, 400)
        self.main_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.main_widget)
        self.top_menu_bar = self.menuBar()
        self.status_bar = self.statusBar()

        # Layout Setup
        self.main_layout = QtWidgets.QGridLayout(self.main_widget)
        self.button_layout = QtWidgets.QGridLayout()
        self.busy_layout = QtWidgets.QGridLayout()

        # I/O Setup
        self.file_menu = self.top_menu_bar.addMenu("File")
        self.edit_menu = self.top_menu_bar.addMenu("Edit")

        self.open_action = QtWidgets.QAction("Open")
        self.open_action.setShortcut("Ctrl+O")
        self.open_action.setStatusTip("Load A New File Or Open A Previous Project")
        self.open_action.triggered.connect(self.open_file)

        self.save_as_action = QtWidgets.QAction("Save As")
        self.save_as_action.setShortcut("Ctrl+F")
        self.save_as_action.setStatusTip("Save Current Data To New File")
        self.save_as_action.setEnabled(False)
        self.save_as_action.triggered.connect(self.saveas)

        self.save_action = QtWidgets.QAction("Save")
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.setStatusTip("Save Current Data")
        self.save_action.setEnabled(False)
        self.save_action.triggered.connect(lambda: self.open_dialog("Overwrite File?", 
                                                                    "Replace Data In Active File?", 
                                                                     0))

        self.quit_action = QtWidgets.QAction("Quit")
        self.quit_action.setShortcut("Ctrl+Q")
        self.quit_action.setStatusTip("Quit GtGUI")
        self.quit_action.triggered.connect(self.close)

        self.undo_action = QtWidgets.QAction("Undo")
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.setStatusTip("Undo Last Action")
        self.undo_action.triggered.connect(self.undo)
        self.undo_action.setEnabled(False)

        self.redo_action = QtWidgets.QAction("Redo")
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.setStatusTip("Redo Next Action")
        self.redo_action.triggered.connect(self.redo)
        self.redo_action.setEnabled(False)

        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_as_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.quit_action)

        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)

        self.log_area = QtWidgets.QTextEdit(self.main_widget)
        self.log_area.setReadOnly(True)
        self.main_layout.addWidget(self.log_area, 0, 0)

        self.open_button = QtWidgets.QPushButton("Open")
        self.open_button.setStatusTip("Load A New File Or Open A Previous Project")
        self.open_button.clicked.connect(self.open_file)

        self.summarize_button = QtWidgets.QPushButton("Summarize")
        self.summarize_button.setStatusTip("Generate Counts For All Alleles")
        self.summarize_button.setEnabled(False)
        self.summarize_button.clicked.connect(lambda: self.launch_thread(1))

        self.frequencies_button = QtWidgets.QPushButton("Calculate Frequencies")
        self.frequencies_button.setStatusTip("Calculate Major And Minor Homozygous "
                                             "And Heterozygous Alleles")
        self.frequencies_button.setEnabled(False)
        self.frequencies_button.clicked.connect(lambda: self.launch_thread(2))

        self.morphisms_button = QtWidgets.QPushButton("Determine Morphisms")
        self.morphisms_button.setStatusTip("Assign Morphisms To Each SNP")
        self.morphisms_button.setEnabled(False)
        self.morphisms_button.clicked.connect(self.get_moprhisms_input)
        self.morphisms_button.clicked.connect(lambda: self.morphisms_button.setEnabled(False))

        self.busy_dialog = QtWidgets.QDialog(self.main_widget)
        self.busy_dialog.setModal(True)
        self.busy_dialog.setLayout(self.busy_layout)
        self.busy_bar = QtWidgets.QProgressBar()
        self.busy_bar.setMinimum(0)
        self.busy_bar.setMaximum(0)
        self.busy_layout.addWidget(self.busy_bar, 0, 1)

        self.button_layout.addWidget(self.open_button, 0, 0) 
        self.button_layout.addWidget(self.summarize_button, 0, 1)
        self.button_layout.addWidget(self.frequencies_button, 0, 2)
        self.button_layout.addWidget(self.morphisms_button, 0, 3)
        self.main_layout.addLayout(self.button_layout, 1, 0)

    def open_file(self, redo=False):
        filename = QtWidgets.QFileDialog.getOpenFileName(self, "Select File To Open Or Load")

        if filename[0]:
            self.active_file = filename[0]
            self.setWindowTitle("GtGUI - " + filename[0].split("/")[-1])
            self.setEnabled(False)
            self.busy_dialog.setWindowTitle("Opening/Loading File/Project")
            self.busy_dialog.show()
            self.worker = WorkingThead(0, filename[0], redo)
            self.worker.finished.connect(lambda: self.setEnabled(True))
            self.worker.finished.connect(self.busy_dialog.close)
            self.worker.finished.connect(lambda: self.save_as_action.setEnabled(True))
            self.worker.emit_error.connect(self.busy_dialog.close)
            self.worker.emit_data.connect(self.update_data)
            self.worker.emit_error.connect(self.update_log)
            self.worker.start()

    def get_moprhisms_input(self, redo=False):

        def _add_morphism():
            row_layout = QtWidgets.QHBoxLayout()
            type_line = QtWidgets.QLineEdit("Type n")
            type_line.resize(type_line.minimumSize())
            row_layout.addWidget(type_line)

            for i in range(3):
                value = QtWidgets.QDoubleSpinBox()
                value.setRange(0.0, 1.0)
                value.setValue(0.50)
                value.setSingleStep(0.01)
                value.setWrapping(True)
                op_select = QtWidgets.QComboBox()
                op_select.addItems([">", "<", ">=", "<=", "=="])
                row_layout.addWidget(op_select)
                row_layout.addWidget(value)

            return row_layout

        def _remove_morphisms(layout):
            children_len = len(layout.findChildren(QtWidgets.QLayout))-1

            if children_len >= 0:
                layout.removeRow(children_len)

        def _submit(layout1, layout2):
            curr_key = None
            failed = None
            mono = None
            poly_parms = {}
            comp_ops = {}
            try:
                for i, widget in enumerate((layout1.itemAt(i).widget() for i in range(layout1.count()))):
                    if isinstance(widget, QtWidgets.QDoubleSpinBox):
                        if i == 1:
                            failed = widget.value()
                        elif i == 5:
                            mono = widget.value()

                for layout in (layout2.children()):
                    curr_key = None
                    for widget in (layout.itemAt(i).widget() for i in range(layout.count())):
                        if isinstance(widget, QtWidgets.QLineEdit):
                            curr_key = widget.text()
                            if curr_key in poly_parms or curr_key in comp_ops:
                                raise ValueError("Duplicates in types/keys for morphisms.")
                            else:
                                poly_parms[curr_key] = []
                                comp_ops[curr_key] = []
                        elif isinstance(widget, QtWidgets.QDoubleSpinBox):
                            poly_parms[curr_key].append(widget.value())
                        elif isinstance(widget, QtWidgets.QComboBox):
                            comp_ops[curr_key].append(widget.currentText())
                self.launch_thread(3, redo, failed, mono, poly_parms, comp_ops)
            except Exception as error:
                self.update_log(3, error)
                self.morphisms_button.setEnabled(True)

        dialog = QtWidgets.QDialog(self.main_widget)
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        dialog.setWindowFlags(dialog.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        dialog.setWindowTitle("Set Morphism Parameters")
        dialog.setFixedWidth(430)
        dialog_layout = QtWidgets.QVBoxLayout(dialog)
        top_inner_layout = QtWidgets.QGridLayout()
        top_header_layout = QtWidgets.QGridLayout()
        bot_inner_layout = QtWidgets.QFormLayout()
        add_button = QtWidgets.QPushButton("Add Morphism")
        remove_button = QtWidgets.QPushButton("Remove Morphism")
        okay_button = QtWidgets.QPushButton("Okay")
        cancel_button = QtWidgets.QPushButton("Cancel")
        add_button.clicked.connect(lambda: bot_inner_layout.addRow(_add_morphism()))
        remove_button.clicked.connect(lambda: _remove_morphisms(bot_inner_layout))
        remove_button.clicked.connect(lambda: dialog.resize(dialog.sizeHint()))
        okay_button.clicked.connect(lambda: _submit(top_inner_layout, bot_inner_layout))
        okay_button.clicked.connect(dialog.close)
        cancel_button.clicked.connect(dialog.close)
        cancel_button.clicked.connect(lambda: self.morphisms_button.setEnabled(True))

        for i, j in enumerate(["Type", "MajorHomo", 
                               "MinorHomo", "MajorHet"]):
            temp_label = QtWidgets.QLabel(j)
            temp_label.setAlignment(QtCore.Qt.AlignCenter)
            top_header_layout.addWidget(temp_label, 0, i)

        failure_line = QtWidgets.QLineEdit("Failed")
        mono_line = QtWidgets.QLineEdit("Mono")
        failure_value = QtWidgets.QDoubleSpinBox()
        failure_value.setRange(0.0, 1.0)
        failure_value.setValue(0.20)
        failure_value.setSingleStep(0.01)
        failure_value.setWrapping(True)
        mono_value = QtWidgets.QDoubleSpinBox()
        mono_value.setRange(0.0, 1.0)
        mono_value.setValue(0.80)
        mono_value.setSingleStep(0.01)
        mono_value.setWrapping(True)

        for i in range(3):
            bot_inner_layout.addRow(_add_morphism())

        top_inner_layout.addWidget(failure_line, 0, 0)
        top_inner_layout.addWidget(failure_value, 0, 1)
        top_inner_layout.addWidget(add_button, 0, 2)
        top_inner_layout.addWidget(okay_button, 0, 3)
        top_inner_layout.addWidget(mono_line, 1, 0)
        top_inner_layout.addWidget(mono_value, 1, 1)
        top_inner_layout.addWidget(remove_button, 1, 2)
        top_inner_layout.addWidget(cancel_button, 1, 3)
        dialog_layout.addLayout(top_inner_layout)
        dialog_layout.addLayout(top_header_layout)
        dialog_layout.addLayout(bot_inner_layout)
        dialog.show()

    def launch_thread(self, selector, redo=False, *args):
        self.busy_dialog.show()
        self.setEnabled(False)

        if selector == 1:
            self.busy_dialog.setWindowTitle("Summarizing Data")
            self.worker = WorkingThead(1, self.data, redo)
        elif selector == 2:
            self.busy_dialog.setWindowTitle("Calculating Frequencies")
            self.worker = WorkingThead(2, self.data, redo)
        elif selector == 3:
            self.busy_dialog.setWindowTitle("Determining Morphisms")
            self.worker = WorkingThead(3, self.data, redo, *args)

        self.worker.finished.connect(lambda: self.setEnabled(True))
        self.worker.finished.connect(self.busy_dialog.close)
        self.worker.emit_error.connect(self.busy_dialog.close)
        self.worker.emit_data.connect(self.update_data)
        self.worker.emit_error.connect(self.update_log)
        self.worker.start()

    def update_data(self, data, method, redo=False):
        self.data = data
        self.update_log(method)
        if not redo:
            self.action_log.append(method)
        if self.last_action + 1 >= len(self.action_log)-1:
            self.last_action = len(self.action_log)-1
            self.redo_action.setEnabled(False)
        else:
            self.last_action += 1 
        if not self.undo_action.isEnabled():
            self.undo_action.setEnabled(True)

    def save(self):
        self.data.save(self.active_file)

    def saveas(self):
        filename = QtWidgets.QFileDialog.getSaveFileName(self, "Save File")

        if filename[0]:
            self.data.save(filename[0])
            self.active_file = filename[0]
            self.save_action.setEnabled(True)

    def undo(self):
        try:
            if self.action_log[self.last_action] == 0:
                self.open_dialog("Undo Error", "Can't Undo Open/Load File/Project")
                return
            elif self.action_log[self.last_action] == 1:
                self.data.data.drop(self.data.count_cols, 1, inplace=True)
                self.data.count_cols = None
                self.data.summarized = False
                self.summarize_button.setEnabled(True)
                self.frequencies_button.setEnabled(False)
                self.update_log(1, undo=True)
            elif self.action_log[self.last_action] == 2:
                self.data.data.drop(["MajorHomo", "MajorHomoCount", 
                                     "MinorHomo", "MinorHomoCount",
                                     "MajorHet", "MajorHetCount",
                                     "MissingCount", "TotalNotMissing"],
                                    axis=1, inplace=True)
                self.data.frequencies = False
                self.frequencies_button.setEnabled(True)
                self.morphisms_button.setEnabled(False)
                self.update_log(2, undo=True)
            elif self.action_log[self.last_action] == 3:
                self.data.data.drop("Morphism", axis=1, inplace=True)
                self.data.morphed = False
                self.morphisms_button.setEnabled(True)
                self.update_log(3, undo=True)
        except Exception as error:
            self.update_log(-1, error)
            return

        if self.last_action - 1 >= 0:
            self.last_action -= 1
        else:
            self.last_action = 0

        if self.last_action < len(self.action_log)-1:
            self.redo_action.setEnabled(True)
        else:
            self.redo_action.setEnabled(False)

    def redo(self):
        if self.action_log[self.last_action+1] == 3:
            self.get_moprhisms_input(redo=True)
        else:
            self.launch_thread(self.action_log[self.last_action+1], redo=True)

    def update_log(self, method, error=None, undo=False):
        self.log_area.moveCursor(QtGui.QTextCursor.End)
        now = datetime.datetime.now()
        now = (str(now.month) + "-" + str(now.day) +
              "-" + str(now.year) + ", " + str(now.time()))
        message = "<html><body><font size=\"4\" face=\"Sans-Serif\""

        if not undo and error is None:
            message += ("color=\"#00b386\"><b>Success At:</b> " 
                        + now + "<br><b>For:</b> ")
        elif error is not None:
            message += ("color=\"#ff0000\"><b>Failure At:</b> " 
                        + now + "<br><b>Reason:</b> " 
                        + str(error) + " - ")
        elif undo:
            message += ("color=\"#006bb3\"><b>Success At:</b> " 
                        + now + "<br><b>Action Undone:</b> ")
        
        if method == 0:
            message += "File/Project Opening/Loading"
            self.summarize_button.setEnabled(True)
            self.frequencies_button.setEnabled(False)
            self.morphisms_button.setEnabled(False)
            self.undo_action.setEnabled(True)
        elif method == 1:
            message += "Summarizing Data"
            if not undo:
                self.frequencies_button.setEnabled(True)
                self.summarize_button.setEnabled(False)
        elif method == 2:
            message += "Calculating Allelic Frequencies"
            if not undo:
                self.frequencies_button.setEnabled(False)
                self.morphisms_button.setEnabled(True)
        elif method == 3:
            message += "Determining Morphisms"

        message += "<br><br></font></body></html>"
        self.log_area.insertHtml(message)

    def open_dialog(self, title, message, specifier=None):
        if specifier == 0:
            save = QtWidgets.QMessageBox.critical(self.main_widget, title, message,
                                                  QtWidgets.QMessageBox.Save, 
                                                  QtWidgets.QMessageBox.Cancel)
            if save == QtWidgets.QMessageBox.Save:
                self.save()
        else:
            QtWidgets.QMessageBox.critical(self.main_widget, title, message)


class WorkingThead(QtCore.QThread):
    emit_data = QtCore.pyqtSignal(gt.GtManipulator, int, bool)
    emit_error = QtCore.pyqtSignal(int, Exception)

    def __init__(self, selector, data, redo=False, *args):
        super().__init__()
        self.selector = selector
        self.data = data
        self.redo = redo
        self.args = args

    def __del__(self):
        self.wait()

    def run(self):
        try:
            if self.selector == 0:
                manipulator = gt.GtManipulator(file=self.data)
                self.data = manipulator
            elif self.selector == 1:
                self.data.summarize()
            elif self.selector == 2:
                self.data.calc_frequencies()
            elif self.selector == 3:
                self.data.determine_morphisms(self.args[0], self.args[1], 
                                              self.args[2], self.args[3])
            if not self.redo:
                self.emit_data.emit(self.data, self.selector, False)
            elif self.redo:
                self.emit_data.emit(self.data, self.selector, True)
        except Exception as error:
            self.emit_error.emit(-1, error)


if __name__ == "__main__":
    application = QtWidgets.QApplication(sys.argv)
    mainGui = GtGui()
    mainGui.show()
    sys.exit(application.exec_())

