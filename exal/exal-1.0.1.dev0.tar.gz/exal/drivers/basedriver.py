__author__ = 'Kevin'


class BaseDriver(object):
    """ Abstract base-driver """
    def __init__(self):
        """ Constructor """
        super(BaseDriver, self).__init__()

    def open_workbook_from_file(self, filename):
        """

        :param filename: Path af File
        :type filename: str
        :rtype: BaseWorkbook
        """
        raise NotImplementedError()

    def open_workbook(self):
        """

        :rtype: BaseWorkbook
        """
        raise NotImplementedError()

    def shutdown(self):
        """
        Free resources
        :return:
        """
        pass

class BaseWorkbook(object):
    """ Abstract Workbook """
    def __init__(self, driver):
        """ Constructor """
        super(BaseWorkbook, self).__init__()
        self.driver = driver

    def get_sheet(self, name):
        """

        :param name: Name of Sheet
        :type name: str
        :return: Sheet
        :rtype: BaseWorksheet
        """
        raise NotImplementedError()

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
        raise NotImplementedError()

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
        raise NotImplementedError()

    def save_as(self, filepath):
        """
        Saves the Workbook under given Path to Disk.
        :param filepath: Path to save Workbook
        :type filepath: str
        """
        raise NotImplementedError()

    def close(self):
        """
        Close the Workbook
        """
        raise NotImplementedError()

class BaseWorksheet(object):
    """ Abstract Worksheet """
    def __init__(self, workbook):
        """ Constructor """
        super(BaseWorksheet, self).__init__()
        self.workbook = workbook

    @property
    def name(self):
        """

        :return: Name of Sheet
        :rtype: str
        """
        raise NotImplementedError()

    @name.setter
    def name(self, value):
        """
        Sets the Name of the Sheet
        :param value: New name of the Sheet
        :type value: str
        """
        raise NotImplementedError()

    def range(self, start, end):
        """

        :param start: Start position in 2-Dimensions (f. example: (1, 42))
        :type start: tuple of [int]
        :param end: End position in 2-Dimensions (f. example: (1, 42)
        :type end: tuple of [int]
        :return: Range Object
        :rtype: BaseRange
        """
        raise NotImplementedError()

    def cell(self, position):
        """

        :param position: Position in 2-Dimensions (f. example: (1, 42))
        :type position: tuple of [int]
        :return: Cell Object
        :rtype: BaseCell
        """
        raise NotImplementedError()

class BaseRange(object):
    """ Abstract Range """
    def __init__(self, sheet, start, end):
        """ Constructor """
        super(BaseRange, self).__init__()
        self.worksheet = sheet
        self.start = start
        self.end = end

    def cell(self, position):
        """

        :param position: Position in 2-Dimensions (f. example: (1, 42))
        :type position: tuple of [int]
        :return: Cell Object
        :rtype: BaseCell
        """
        raise NotImplementedError()

    @property
    def size(self):
        """

        :return: Size of Range in 2-Dimensions (f. example: (1, 42))
        :rtype: tuple of [int]
        """
        return (self.end[0]-self.start[0], self.end[1] - self.start[1])

    @property
    def value(self):
        """

        :return: Values of all Cells containing in the in 2-Dimensions
        :rtype: tuple of [tuple of [object]]
        """
        raise  NotImplementedError()

    @value.setter
    def value(self, value):
        """

        :param value: Values of all Cells containing in a in 2-Dimensions
        :type value: tuple of [tuple of [object]]
        """
        raise NotImplementedError()

    @property
    def formula(self):
        """

        :return: Formulas of all Cells containing in a in 2-Dimensions
        :rtype: tuple of [tuple of [str]]
        """
        raise NotImplementedError()

    @formula.setter
    def formula(self, value):
        """

        :param value: Formulas of all Cells containing in a in 2-Dimensions
        :type value: tuple of [tuple of [str]]
        """
        raise NotImplementedError()

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

class BaseCell(object):
    """ Abstract Cell """
    def __init__(self, sheet, position):
        """ Constructor """
        super(BaseCell, self).__init__()
        self.worksheet = sheet
        self.position = position

    @property
    def value(self):
        """

        :return: Value inside Cell
        :rtype: object
        """
        raise NotImplementedError()

    @value.setter
    def value(self, value):
        """
        Sets the value inside the Cell
        :param value: New Value
        :type value: object
        """
        raise NotImplementedError()

    @property
    def formula(self):
        """

        :return: Formula inside the Cell
        :rtype: str
        """
        raise NotImplementedError()

    @formula.setter
    def formula(self, value):
        """

        :param value: Formula inside the Cell
        :type value: str
        """
        raise NotImplementedError()

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