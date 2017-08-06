import os
import configparser
from collections import defaultdict, OrderedDict, namedtuple
from itertools import count
from huanexus import Workspace
from xlsxwriter import Workbook
from huanexus import Workspace


class DictExcel:

    _default_format = {"font_name": "Arial",
                      "font_size": 10,
                      "align": "center",
                      "valign": "vcenter",
                      "text_wrap": 1,
                      "num_format": 0,
                      "bold": 0,
                      "border": 0
                      }

    _format_key = {
        "int": "font_size text_wrap bold border left right top bottom"
        }

    columns = [6, 4, 11, 32, 13, 18]

    def __init__(self, workbook, worksheet, columns = None):
        self.workbook = workbook
        self.worksheet = worksheet
        if columns is None:
            columns = self.columns
        self.columns = columns
        for col, width in enumerate(self.columns):
            self.worksheet.set_column(col, col, width)


    def normalize_format(self, _format=None):
        default_format = dict(self._default_format)        
        if _format is None:
            _format = {}
        default_format.update(_format)
        
        new_format = OrderedDict()
        for key, value in sorted(default_format.items()):
            for klass, keys in self._format_key.items():
                klass = eval(klass)
                keys = keys.split()
                if key in keys:
                    new_format[key] = klass(value)
            if key not in new_format:
                new_format[key] = value                    
        return new_format


    def get_border(self, section, text_cell_key):
        text_cell = "text-cell"
        border_cell = "border-cell"
        row_col = text_cell_key.replace(text_cell, "").strip("-")
        row, col = [int(v) for v in row_col.split("-")]
        border_cell_key = text_cell_key.replace(text_cell, border_cell)
        try:
            border_cell_text = section[border_cell_key]
        except KeyError:
            try:
                border_cell_text = section["%s-r-%s" %(border_cell, col)]
            except KeyError:
                try:
                    border_cell_text = section["%s-r-c" %border_cell]
                except KeyError:
                    return {}

        border_cell_dict = {}
        styles = [v.strip() for v in border_cell_text.split(";")]
        for style in styles:
            if style:
                key, value = style.split()
                border_cell_dict[key] = int(value)
        return border_cell_dict


    def get_merge(self, section, text_cell_key):
        text_cell = "text-cell"
        merge_cell = "merge-cell"
        row_col = text_cell_key.replace(text_cell, "").strip("-")
        row, col = [int(v) for v in row_col.split("-")]
        merge_cell_key = text_cell_key.replace(text_cell, merge_cell)
        try:
            merge_cell_text = section[merge_cell_key]
        except KeyError:
            try:
                merge_cell_text = section["%s-r-%s" %(merge_cell, col)]
            except KeyError:
                try:
                    merge_cell_text = section["%s-r-c" %merge_cell]
                except KeyError:
                    merge_cell_text = "1 1"
        nrow, ncol = [int(v) for v in merge_cell_text.split()]        
        return nrow, ncol



    def get_format(self, section, text_cell_key):
        
        text_cell = "text-cell"
        format_cell = "format-cell"
        row_col = text_cell_key.replace(text_cell, "").strip("-")
        row, col = [int(v) for v in row_col.split("-")]
        format_cell_key = text_cell_key.replace(text_cell, format_cell)
        try:
            format_cell_text = section[format_cell_key]
        except KeyError:
            try:
                format_cell_text = section["%s-r-%s" %(format_cell, col)]
            except KeyError:
                try:
                    format_cell_text = section["%s-r-c" %format_cell]
                except KeyError:
                    format_cell_text = ""

        format_cell_dict = {}
        styles = [v.strip() for v in format_cell_text.split(";")]
        for style in styles:
            if style:
                key, value = style.split()              
                format_cell_dict[key] = value
        format_cell_dict = self.normalize_format(format_cell_dict)
        return row, col, format_cell_dict    


    def write_layout(self, adict, first_row=0, first_col=0):
        workbook, worksheet = self.workbook, self.worksheet
        section = adict
        r0 = section.get("r0", 0) 
        c0 = section.get("c0", 0)
        r0, c0 = int(r0)+first_row, int(c0)+first_col        
        start_col=0        
        start_row =  self.worksheet.dim_rowmax
        if start_row is None:
            start_row = -1
        start_row += 1
        for key, text in section.items():
            if not key.startswith("text-cell"):
                continue
            row, col, rc_format_dict = self.get_format(section, key)
            rc_border_dict = self.get_border(section, key)
            nrow, ncol = self.get_merge(section, key)
            merge = not (nrow == 1 and ncol == 1)
            format_key = tuple(rc_format_dict.items())
            cell_format = self.workbook.add_format(rc_format_dict)
            for border, border_value in rc_border_dict.items():
                getattr(cell_format, "set_%s" % border)(border_value)
            row = row + start_row+r0
            col = col + start_col+c0
            text = text.replace("|", "\n")
            if merge:
                worksheet.merge_range(row, col, row+nrow-1, col+ncol-1, text, cell_format)                        
            else:
                worksheet.write(row, col, text, cell_format)


    def close(self):
        self.workbook.close()

class ExcelWriter:

    __book__ = defaultdict(None)
    __sheet__ = defaultdict(dict)
    __counter__ = defaultdict(count)
    __rowcursor__ = defaultdict(count)
    __fields__ = defaultdict(dict)
    __firstrow__ = defaultdict(int)
    __firstcol__ = defaultdict(int)
    __lastrow__ = defaultdict(int)
    __lastcol__ = defaultdict(int)
    __data__ = OrderedDict()
    __fmt__ = defaultdict(dict)
    __pattern__ = defaultdict(dict)
    __wb_format__ = defaultdict(dict)
    __sheetordered__ = False

    _default_format = {"font_name": "Arial",
                      "font_size": 10,
                      "align": "center",
                      "valign": "vcenter",
                      "text_wrap": 1,
                      "num_format": 0,
                      "bold": 0,
                      "border": 0
                      }

    _format_key = {
        "int": "font_size text_wrap bold border left right top bottom"
        }

    columns = [6, 4, 11, 32, 13, 18]

    workbook_format = defaultdict(dict)

    def __init__(self, book, sheet, job, columns = None):
        workbooks = self.__book__
        sheets = self.__sheet__
        self.counter = defaultdict(count)
        self.rowcursor = self.__rowcursor__[(book, sheet)]
        try:
            worksheet = sheets[book][sheet]
        except KeyError:
            if book not in workbooks:
                workbook = workbooks[book] = Workbook('%s.xlsx' % book, {'strings_to_numbers': True})
            sheets[book][sheet] = workbooks[book].add_worksheet(sheet)
            worksheet = sheets[book][sheet]

        self.book = book
        self.sheet = sheet
        self.workbook = workbooks[book]
        self.worksheet = sheets[book][sheet]
        workspace = Workspace()
        config_path = workspace("workbook")
        config_file = os.path.join(config_path, job+".ini")
        config = configparser.ConfigParser()
        config._interpolation = configparser.ExtendedInterpolation()
        config.read(config_file)
        self.config = config

        if columns is None:
            columns = self.columns
        self.columns = columns
        for col, width in enumerate(self.columns):
            self.worksheet.set_column(col, col, width)


    def normalize_format(self, _format=None):
        default_format = dict(self._default_format)        
        if _format is None:
            _format = {}
        default_format.update(_format)
        
        new_format = OrderedDict()
        for key, value in sorted(default_format.items()):
            for klass, keys in self._format_key.items():
                klass = eval(klass)
                keys = keys.split()
                if key in keys:
                    new_format[key] = klass(value)
            if key not in new_format:
                new_format[key] = value                    
        return new_format


    def get_border(self, section, text_cell_key):
        text_cell = "text-cell"
        border_cell = "border-cell"
        row_col = text_cell_key.replace(text_cell, "").strip("-")
        row, col = [int(v) for v in row_col.split("-")]
        border_cell_key = text_cell_key.replace(text_cell, border_cell)
        try:
            border_cell_text = section[border_cell_key]
        except KeyError:
            try:
                border_cell_text = section["%s-r-%s" %(border_cell, col)]
            except KeyError:
                try:
                    border_cell_text = section["%s-r-c" %border_cell]
                except KeyError:
                    return {}

        border_cell_dict = {}
        styles = [v.strip() for v in border_cell_text.split(";")]
        for style in styles:
            if style:
                key, value = style.split()
                border_cell_dict[key] = int(value)
        return border_cell_dict


    def get_merge(self, section, text_cell_key):
        text_cell = "text-cell"
        merge_cell = "merge-cell"
        row_col = text_cell_key.replace(text_cell, "").strip("-")
        row, col = [int(v) for v in row_col.split("-")]
        merge_cell_key = text_cell_key.replace(text_cell, merge_cell)
        try:
            merge_cell_text = section[merge_cell_key]
        except KeyError:
            try:
                merge_cell_text = section["%s-r-%s" %(merge_cell, col)]
            except KeyError:
                try:
                    merge_cell_text = section["%s-r-c" %merge_cell]
                except KeyError:
                    merge_cell_text = "1 1"
        nrow, ncol = [int(v) for v in merge_cell_text.split()]        
        return nrow, ncol



    def get_format(self, section, text_cell_key):
        
        text_cell = "text-cell"
        format_cell = "format-cell"
        row_col = text_cell_key.replace(text_cell, "").strip("-")
        row, col = [int(v) for v in row_col.split("-")]
        format_cell_key = text_cell_key.replace(text_cell, format_cell)
        try:
            format_cell_text = section[format_cell_key]
        except KeyError:
            try:
                format_cell_text = section["%s-r-%s" %(format_cell, col)]
            except KeyError:
                try:
                    format_cell_text = section["%s-r-c" %format_cell]
                except KeyError:
                    format_cell_text = ""

        format_cell_dict = {}
        styles = [v.strip() for v in format_cell_text.split(";")]
        for style in styles:
            if style:
                key, value = style.split()              
                format_cell_dict[key] = value
        format_cell_dict = self.normalize_format(format_cell_dict)
        return row, col, format_cell_dict    


    def write_layout(self, adict, first_row=0, first_col=0):
        workbook, worksheet = self.workbook, self.worksheet
        section = adict
        r0 = section.get("r0", 0) 
        c0 = section.get("c0", 0)
        r0, c0 = int(r0)+first_row, int(c0)+first_col        
        start_col=0        
        start_row =  self.worksheet.dim_rowmax
        if start_row is None:
            start_row = -1
        start_row += 1
        for key, text in section.items():
            if not key.startswith("text-cell"):
                continue
            row, col, rc_format_dict = self.get_format(section, key)
            rc_border_dict = self.get_border(section, key)
            nrow, ncol = self.get_merge(section, key)
            merge = not (nrow == 1 and ncol == 1)
            format_key = tuple(rc_format_dict.items())
            cell_format = self.workbook.add_format(rc_format_dict)
            for border, border_value in rc_border_dict.items():
                getattr(cell_format, "set_%s" % border)(border_value)
            row = row + start_row+r0
            col = col + start_col+c0
            text = text.replace("|", "\n")
            if merge:
                worksheet.merge_range(row, col, row+nrow-1, col+ncol-1, text, cell_format)                        
            else:
                worksheet.write(row, col, text, cell_format)


    @classmethod
    def print_area(cls, rows=None, cols=None):
        for book, sheets in cls.__sheet__.items():
            for sheet, ws in sheets.items():
                dim_rowmax = ws.dim_rowmax
                dim_colmax = ws.dim_colmax
                print_rows = rows or dim_rowmax
                print_cols = cols or dim_rowmax
                ws.print_area(0, 0, print_rows, print_cols)
            

    @classmethod
    def close(cls):
        for book, workbook in cls.__book__.items():
            workbook.close()
        
def main():
    excel = ExcelWriter("book", "sheet", "price")
    config = excel.config
    for section in config.sections():
        adict = dict(config[section])
        if section == "a-i-2-0":
            adict["r0"] = 8
        excel.write_layout(adict)
    ExcelWriter.close()

if __name__ == "__main__":
    main()
