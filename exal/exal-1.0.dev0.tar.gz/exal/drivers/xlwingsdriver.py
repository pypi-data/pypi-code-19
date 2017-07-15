from fileinput import filename

__author__ = 'Kevin'

from basedriver import *
import xlwings
import os
import time

class XLWingsDriver(BaseDriver):
    """  """
    def __init__(self):
        """ Constructor """
        super(XLWingsDriver, self).__init__()


    def open_workbook_from_file(self, filename):
        """

        :param filename: Path af File
        :type filename: str
        :rtype: BaseWorkbook
        """
        name = os.path.basename(filename)
        ret =  XLWingsWorkbook(self, name, xlwings.Book(os.path.abspath(filename)))
        time.sleep(0.2) # Wait a bit, so the File can be loaded
        return ret

    def open_workbook(self):
        """

        :rtype: BaseWorkbook
        """
        return XLWingsWorkbook(self,'NONAME', xlwings.Book()) #.Workbook())

class XLWingsWorkbook(BaseWorkbook):
    """ Abstract Workbook """
    def __init__(self, driver, name, workbook):
        """

        :param driver:
        :type driver: XLWingsDriver
        :param workbook:
        :type workbook: xlwings.Workbook
        :return:
        """
        super(XLWingsWorkbook, self).__init__(driver)
        self._name = name
        self.workbook = workbook

    def get_sheet(self, name):
        """

        :param name: Name of Sheet
        :type name: str
        :return: Sheet
        :rtype: BaseWorksheet
        """
        return XLWingsWorksheet(self, name)

    @property
    def sheets(self):
        """

        :return: Tuple of containing sheets
        :rtype: tuple of [BaseWorksheet]
        """
        names = [sh.name for sh in self.workbook.sheets]
        return [XLWingsWorksheet(self, n) for n in names]

    @property
    def name(self):
        """

        :return: Name of Workbook
        :rtype: str
        """
        return self._name

    @property
    def path(self):
        """

        :return: Path of Workbook
        :rtype: str
        """
        return self.workbook.fullname

    def save(self):
        """
        Saves the Workbook to Disk.
        """
        self.workbook.save()

    def save_as(self, filepath):
        """
        Saves the Workbook under given Path to Disk.
        :param filepath: Path to save Workbook
        :type filepath: str
        """
        self.workbook.save(os.path.abspath(filepath))

    def close(self):
        """
        Close the Workbook
        """
        self.workbook.close()

class XLWingsWorksheet(BaseWorksheet):
    """ Abstract Worksheet """
    def __init__(self, workbook, name):
        """

        :param workbook:
        :type workbook: XLWingsWorkbook
        :param name:
        :type name: str
        :return:
        """
        super(XLWingsWorksheet, self).__init__(workbook)
        self._name = name
        self.__sheet__ = workbook.workbook.sheets['name']

    @property
    def name(self):
        """

        :return: Name of Sheet
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, value):
        """
        Sets the Name of the Sheet
        :param value: New name of the Sheet
        :type value: str
        """
        self._name = value
        self.__sheet__.name = value

    def range(self, start, end):
        """

        :param start: Start position in 2-Dimensions (f. example: (1, 42))
        :type start: tuple of [int]
        :param end: End position in 2-Dimensions (f. example: (1, 42)
        :type end: tuple of [int]
        :return: Range Object
        :rtype: BaseRange
        """
        return XLWingsRange(self, start, end)

    def cell(self, position):
        """

        :param position: Position in 2-Dimensions (f. example: (1, 42))
        :type position: tuple of [int]
        :return: Cell Object
        :rtype: BaseCell
        """
        return XLWingsCell(self, position)

class XLWingsRange(BaseRange):
    """ Abstract Range """
    def __init__(self, sheet, start, end):
        """ Constructor """
        super(XLWingsRange, self).__init__(sheet, start, end)
        self.__range__ = sheet.__sheet__.range(start, end)

    def cell(self, position):
        """

        :param position: Position in 2-Dimensions (f. example: (1, 42))
        :type position: tuple of [int]
        :return: Cell Object
        :rtype: BaseCell
        """
        i, j = self.start[0] + position[0], self.start[1] + position[1]
        return XLWingsCell(self.worksheet, (i, j))

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

        :return: Values of all Cells containing in 2 or 1 Dimensions
        :rtype: tuple of [tuple of [object]]
        """
        return self.__range__.value

    @value.setter
    def value(self, value):
        """

        :param value: Values of all Cells containing in a in 2-Dimensions
        :type value: tuple of [tuple of [object]]
        """
        self.__range__.value = value

    @property
    def formula(self):
        """

        :return: Formulas of all Cells containing in a in 2-Dimensions
        :rtype: tuple of [tuple of [str]]
        """
        return self.__range__.formula

    @formula.setter
    def formula(self, value):
        """

        :param value: Formulas of all Cells containing in a in 2-Dimensions
        :type value: tuple of [tuple of [str]]
        """
        self.__range__.formula = value

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
        (i, k) = self.end[0] + heigth, self.end[1] + width
        return XLWingsRange(self.worksheet, self.start, (i, k))

class XLWingsCell(BaseCell):
    """ Abstract Cell """
    def __init__(self, sheet, position):
        """ Constructor """
        super(XLWingsCell, self).__init__(sheet, position)
        self.__cell__ = sheet.__sheet__.range(position)

    @property
    def value(self):
        """

        :return: Value inside Cell
        :rtype: object
        """
        return self.__cell__.value

    @value.setter
    def value(self, value):
        """
        Sets the value inside the Cell
        :param value: New Value
        :type value: object
        """
        self.__cell__.value = value

    @property
    def formula(self):
        """

        :return: Formula inside the Cell
        :rtype: str
        """
        return self.__cell__.formula

    @formula.setter
    def formula(self, value):
        """

        :param value: Formula inside the Cell
        :type value: str
        """
        self.__cell__.formula = value

    @property
    def comment(self):
        """

        :return: Comment of Cell
        :rtype: str
        """
        raise NotImplementedError()

    @comment.setter
    def comment(self, value):
        """
        Sets the comment of the Cell
        :param value: Comment of the Cell
        :type value: str
        """
        raise NotImplementedError()