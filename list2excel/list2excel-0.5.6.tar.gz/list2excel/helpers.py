# -*- coding: utf-8 -*-
from core import ExcelOutFile, CsvOutFile


def list2excel(model, queryset=None, headers=None, list_obj=None, workbook_name=None, sheetbasename=None, force_text=False, csv_format=False):
    if csv_format:
        xl = CsvOutFile()
        xl.dump_list(model=model, queryset=queryset, headers=headers, list_obj=list_obj)
    else:
        xl = ExcelOutFile(workbook_name=workbook_name, force_text=force_text)
        xl.dump_list(model=model, queryset=queryset, headers=headers, list_obj=list_obj, sheetbasename=sheetbasename)
    return xl
