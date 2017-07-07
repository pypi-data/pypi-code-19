# -*- coding: utf-8 -*-
import xlwt

EXCEL_STYLES = {
    'datetime': xlwt.easyxf(num_format_str='dd/mm/yyyy hh:mm:ss'),
    'date': xlwt.easyxf(num_format_str='dd/mm/yyyy'),
    'time': xlwt.easyxf(num_format_str='hh:mm:ss'),
    'float': xlwt.easyxf(num_format_str='#,##0.00'),
    'default': xlwt.Style.default_style,
    'title': xlwt.easyxf('font: bold on'),
    'percent': xlwt.easyxf(num_format_str='0.00%'),
    'formula': xlwt.easyxf('font: italic on; pattern: pattern solid, fore_colour gray25', num_format_str='#,##0.00'),
    'hyperlink': xlwt.easyxf('font: underline single, colour_index blue'),
    'forced_text': xlwt.easyxf(num_format_str='@')
}

MAX_FILENAME_LENGTH = 64
