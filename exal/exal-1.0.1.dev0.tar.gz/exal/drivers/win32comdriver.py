__author__ = 'Kevin'

from basedriver import *
import win32com.client
from win32com.client import DispatchEx
from .. import helper


def _close_excel_by_force(excel):
    import win32process
    import win32gui
    import win32api
    import win32con
    import time

    # Get the window's process id's
    hwnd = excel.Hwnd
    t, p = win32process.GetWindowThreadProcessId(hwnd)
    # Ask window nicely to close
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    # Allow some time for app to close
    time.sleep(1)
    # If the application didn't close, force close
    try:
        handle = win32api.OpenProcess(win32con.PROCESS_TERMINATE, 0, p)
        if handle:
            win32api.TerminateProcess(handle, 0)
            win32api.CloseHandle(handle)
    except:
        pass

class Win32ComDriver(BaseDriver):
    """ Abstract base-driver """
    def __init__(self):
        """ Constructor """
        super(Win32ComDriver, self).__init__()
        #self.xl = DispatchEx("Excel.application")
        try:
            self.xl = win32com.client.gencache.EnsureDispatch("Excel.Application")
        except:
            self.xl = win32com.client.Dispatch("Excel.Application")

        self.xl.Interactive = False
        self.xl.Visible = True

    def open_workbook_from_file(self, filename):
        """

        :param filename: Path af File
        :type filename: str
        :rtype: BaseWorkbook
        """
        self.xl.Visible = True
        wb = self.xl.Workbooks.Open(filename)
        return Win32ComWorkbook(self, wb)

    def open_workbook(self):
        """

        :rtype: BaseWorkbook
        """
        raise NotImplementedError()

    def __del__(self):
        pass
        #self.xl.Application.Quit()
        #_close_excel_by_force(self.xl)

    def shutdown(self):
        _close_excel_by_force(self.xl)

class Win32ComWorkbook(BaseWorkbook):
    """ Abstract Workbook """
    def __init__(self, driver, workbook):
        """ Constructor """
        super(Win32ComWorkbook, self).__init__(driver)
        self.workbook = workbook

    def get_sheet(self, name):
        """

        :param name: Name of Sheet
        :type name: str
        :return: Sheet
        :rtype: BaseWorksheet
        """
        return Win32ComWorksheet(self, self.workbook.Worksheets[name])

    @property
    def sheets(self):
        """

        :return: Tuple of containing sheets
        :rtype: tuple of [BaseWorksheet]
        """
        raise NotImplementedError()

    @property
    def name(self):
        """

        :return: Name of Workbook
        :rtype: str
        """
        return self.workbook.Name

    @property
    def path(self):
        """

        :return: Path of Workbook
        :rtype: str
        """
        raise NotImplementedError()

    def save(self):
        """
        Saves the Workbook to Disk.
        """
        self.workbook.Save()

    def save_as(self, filepath):
        """
        Saves the Workbook under given Path to Disk.
        :param filepath: Path to save Workbook
        :type filepath: str
        """
        self.workbook.SaveAs(filepath)

    def close(self):
        """
        Close the Workbook
        """
        self.workbook.Close(SaveChanges=False)

class Win32ComWorksheet(BaseWorksheet):
    """ Abstract Worksheet """
    def __init__(self, workbook, worksheet):
        """ Constructor """
        super(Win32ComWorksheet, self).__init__(workbook)
        self.worksheet = worksheet

    @property
    def name(self):
        """

        :return: Name of Sheet
        :rtype: str
        """
        return self.worksheet.Name

    @name.setter
    def name(self, value):
        """
        Sets the Name of the Sheet
        :param value: New name of the Sheet
        :type value: str
        """
        self.worksheet.Name = value

    def range(self, start, end):
        """

        :param start: Start position in 2-Dimensions (f. example: (1, 42))
        :type start: tuple of [int]
        :param end: End position in 2-Dimensions (f. example: (1, 42)
        :type end: tuple of [int]
        :return: Range Object
        :rtype: BaseRange
        """
        start_addr = helper.pos2address(*start)
        end_addr = helper.pos2address(*end)
        return Win32ComRange(self, start, end,  self.worksheet.Range(start_addr, end_addr))

    def cell(self, position):
        """

        :param position: Position in 2-Dimensions (f. example: (1, 42))
        :type position: tuple of [int]
        :return: Cell Object
        :rtype: BaseCell
        """
        return Win32ComCell(self, position, self.worksheet.Cells(*position))

class Win32ComRange(BaseRange):
    """ Abstract Range """
    def __init__(self, sheet, start, end, range):
        """ Constructor """
        super(Win32ComRange, self).__init__(sheet, start, end)
        self.range = range

    def cell(self, position):
        """

        :param position: Position in 2-Dimensions (f. example: (1, 42))
        :type position: tuple of [int]
        :return: Cell Object
        :rtype: BaseCell
        """
        return Win32ComCell(self, position, self.range.Cells(*position))

    @property
    def size(self):
        """

        :return: Size of Range in 2-Dimensions (f. example: (1, 42))
        :rtype: tuple of [int]
        """
        i, j = self.end[0] - self.start[0] + 1, self.end[1] - self.start[1] + 1
        return (i, j)

    @property
    def value(self):
        """

        :return: Values of all Cells containing in the in 2-Dimensions
        :rtype: tuple of [tuple of [object]]
        """
        return helper.reduce_dimensions(self.range.Value2, *self.size)

    @value.setter
    def value(self, value):
        """

        :param value: Values of all Cells containing in a in 2-Dimensions
        :type value: tuple of [tuple of [object]]
        """
        self.range.Value2 = value


    @property
    def formula(self):
        """

        :return: Formulas of all Cells containing in a in 2-Dimensions
        :rtype: tuple of [tuple of [str]]
        """
        return helper.reduce_dimensions(self.range.Formula, *self.size)

    @formula.setter
    def formula(self, value):
        """

        :param value: Formulas of all Cells containing in a in 2-Dimensions
        :type value: tuple of [tuple of [str]]
        """
        self.range.Formula = value

    def resize(self, heigth=0, width=0):
        """
        Resizes the Range by given Offsets
        :param heigth: Height offset
        :type heigth: int
        :param width: Width offset
        :type width: int
        :return: New, resized Range
        :rtype: BaseRange
        """
        raise NotImplementedError()

class Win32ComCell(BaseCell):
    """ Abstract Cell """
    def __init__(self, sheet, position, cell):
        """ Constructor """
        super(Win32ComCell, self).__init__(sheet, position)
        self.cell = cell

    @property
    def value(self):
        """

        :return: Value inside Cell
        :rtype: object
        """
        return self.cell.Value2

    @value.setter
    def value(self, value):
        """
        Sets the value inside the Cell
        :param value: New Value
        :type value: object
        """
        self.cell.Value2 = value

    @property
    def formula(self):
        """

        :return: Formula inside the Cell
        :rtype: str
        """
        return self.cell.Formula

    @formula.setter
    def formula(self, value):
        """

        :param value: Formula inside the Cell
        :type value: str
        """
        self.cell.Formula = value

    @property
    def comment(self):
        """

        :return: Comment of Cell
        :rtype: str
        """
        if self.cell.Comment is not None:
            return self.cell.Comment.Text()
        return None

    @comment.setter
    def comment(self, value):
        """
        Sets the comment of the Cell
        :param value: Comment of the Cell
        :type value: str
        """
        if self.cell.Comment is not None:
            self.cell.Comment.Text(value)
        else:
            self.cell.AddComment(value)