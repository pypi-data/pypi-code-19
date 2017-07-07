# -*- coding: utf-8 -*-
from __future__ import absolute_import
import datetime
import logging
import os
import tempfile
import xlwt
import zipfile
from decimal import Decimal
import django
from django.db.models import manager
from django.db.models.fields import Field
from django.template.defaultfilters import slugify
from django.utils import six
from django.utils.encoding import force_unicode
from xlwt.ExcelFormula import Formula
from xlwt.ExcelFormulaParser import FormulaParseException
import csv
import codecs
import cStringIO

from .constants import EXCEL_STYLES
from .settings import MAX_FILENAME_LENGTH

logger = logging.getLogger(__name__)


try:
    from django.http import StreamingHttpResponse
    from wsgiref.util import FileWrapper
except ImportError:
    from django.http import HttpResponse as StreamingHttpResponse
    from wsgiref.util import FileWrapper as WSGIFileWrapper

    class FileWrapper(WSGIFileWrapper):
        def __init__(self, filelike, blksize=8192):
            # print "FileWrapper"
            FileWrapper.__init__(self, filelike, blksize)

        def __getitem__(self, key):
            # print "FileWrapper.__getitem__"
            # return super(FileWrapperEx, self).__getitem__(key)
            return FileWrapper.__getitem__(self, key)

        def __iter__(self):
            # print "FileWrapper.__iter__"
            if hasattr(self.filelike, 'seek') and callable(self.filelike.seek):
                # print "FileWrapper.__iter__: reset"
                self.filelike.seek(0)
            # return super(FileWrapperEx, self).__iter__()
            return FileWrapper.__iter__(self)

        def next(self):
            # print "FileWrapper.next"
            try:
                # return super(FileWrapperEx, self).next()
                return FileWrapper.next(self)
            except StopIteration:
                # print "finished"
                raise


class Hyperlink(object):
    def __init__(self, text, url):
        self.text = text
        self.url = url

    def as_cell(self):
        return Formula(u'HYPERLINK("{0:s}";"{1}")'.format(self.url, self.text or self.url))

    def __unicode__(self):
        return unicode(self.text) or unicode(self.url)
hyperlink = Hyperlink


def get_value_cell_style(value_instance, cell_style=None, force_text=False):
    if force_text and isinstance(value_instance, (datetime.datetime, datetime.date, Decimal)):
        cell_style = EXCEL_STYLES['forced_text']
    elif not cell_style:
        if isinstance(value_instance, datetime.datetime):
            cell_style = EXCEL_STYLES['datetime']
        elif isinstance(value_instance, datetime.date):
            cell_style = EXCEL_STYLES['date']
        elif isinstance(value_instance, datetime.time):
            cell_style = EXCEL_STYLES['time']
        elif isinstance(value_instance, (float, Decimal)):
            cell_style = EXCEL_STYLES['float']
        elif isinstance(value_instance, Hyperlink):
            cell_style = EXCEL_STYLES['hyperlink']
        else:
            cell_style = EXCEL_STYLES['default']

    if value_instance is None or (isinstance(value_instance, six.string_types) and value_instance == ''):
        value = ""
        cell_style = EXCEL_STYLES['forced_text']
    else:
        if isinstance(value_instance, bool):
            value = u"Sì" if value_instance else u"No"
        elif isinstance(value_instance, six.string_types) and value_instance and value_instance[0] == "=":
            try:
                value = xlwt.Formula(value_instance[1:])
                if value_instance[-1] == '%':
                    cell_style = EXCEL_STYLES['percent']
                else:
                    cell_style = EXCEL_STYLES['formula']
            except FormulaParseException:
                value = value_instance
                cell_style = EXCEL_STYLES['forced_text']
        elif isinstance(value_instance, Decimal):
            value = unicode(value_instance).replace('.', ',') if force_text else value_instance
        elif isinstance(value_instance, (datetime.date, datetime.datetime)):
            value = value_instance.strftime('%d/%m/%Y') if force_text else value_instance
        elif isinstance(value_instance, six.string_types + six.integer_types + (float, )):
            value = value_instance
        elif type(value_instance) in (tuple, list):
            value = ', '.join(unicode(x) for x in value_instance)
        elif isinstance(value_instance, manager.Manager):
            value = ', '.join(unicode(x) for x in value_instance.all())
        elif isinstance(value_instance, Hyperlink):
            value = value_instance.as_cell()
        else:
            value = unicode(value_instance)
    return value, cell_style


def new_style_to_be_forced(style_new, style_old):
    return style_old == EXCEL_STYLES['default'] and style_new != style_old


class DataItem(object):
    FIELD = 0
    ATTRIBUTE = 1
    CALLABLE = 2
    RELATED = 3
    NONE = -1
    TYPES = (FIELD, ATTRIBUTE, CALLABLE, RELATED)

    def __init__(self, model, obj, obj_type=None):
        if not obj_type:
            if isinstance(obj, Field):
                self.type = DataItem.FIELD
            elif isinstance(obj, six.string_types):
                if hasattr(model, obj):
                    attr = getattr(model, obj)
                    if callable(attr):
                        self.type = DataItem.CALLABLE
                    else:
                        self.type = DataItem.ATTRIBUTE  # ha senso?
                elif '__' in obj and hasattr(model, obj.split('__', 1)[0]):
                    self.type = DataItem.RELATED
                else:
                    self.type = DataItem.NONE
            else:
                raise ValueError(u"Tipo di attributo non previsto: {0:s}".format(type(obj)))
        else:
            if obj_type not in self.TYPES:
                raise ValueError(u"Tipo DataItem non riconosciuto: '{0:s}'".format(obj_type))
            self.type = obj_type
            # non verifica che il tipo dichiarato corrisponda
        self.model = model
        self.source = obj
        self.style = None
        if self.type == DataItem.FIELD:
            self.is_pk = self.source == model._meta.pk
        else:
            self.is_pk = False

    def __unicode__(self):
        retval = u"%s DataItem" % {
            self.FIELD: "Field",
            self.ATTRIBUTE: "Attribute",
            self.CALLABLE: "Callable",
            self.RELATED: "Related"}.get(self.type, "Unknown")
        if self.model:
            retval += " %s" % self.model.__name__
        if self.source:
            retval += " (%s)" % getattr(self.source, 'name', unicode(self.source))
        return retval

    def __repr__(self):
        return u"<%s>" % unicode(self)

    def get_value(self, instance):
        if self.type == DataItem.FIELD:
            if hasattr(instance, 'get_{}_display'.format(self.source.name)):
                return getattr(instance, 'get_{}_display'.format(self.source.name))()
            return getattr(instance, self.source.name)
        elif self.type == DataItem.CALLABLE:
            value = getattr(instance, self.source)()
            if isinstance(value, (tuple, list, set)):
                return ', '.join(value)
            return value
        elif self.type == DataItem.ATTRIBUTE:
            return getattr(instance, self.source)
        elif self.type == DataItem.RELATED:
            lst = self.source.split('__')
            if len(lst) <= 2:
                if hasattr(instance, lst[0]):
                    r = getattr(instance, lst[0])
                    if len(lst) == 1:
                        return r.pk if hasattr(r, 'pk') else r
                    else:
                        return getattr(r, lst[1]) if hasattr(r, lst[1]) else u''
            else:
                raise NotImplementedError(self.source)
        elif self.type == DataItem.NONE:
            return u''
        else:
            raise ValueError(u"Tipo DataItem non riconosciuto: '{0:s}'".format(self.type))

    def get_value_cell_style(self, instance, force_text=False):
        value, style = get_value_cell_style(self.get_value(instance), self.style, force_text=force_text)
        if not self.style or new_style_to_be_forced(style, self.style):
            if value:
                self.style = style
        return value, style

    def get_title(self):
        title = u""
        if self.type == DataItem.FIELD:
            title = self.source.verbose_name or self.source.name
        elif self.type in (DataItem.CALLABLE, DataItem.ATTRIBUTE):
            obj = getattr(self.model, self.source)
            if hasattr(obj, 'short_description'):
                title = obj.short_description
            else:
                title = self.source
                if title.startswith('get_'):
                    title = title[4:]
                title = title.replace('_', ' ').capitalize()
        elif self.type == DataItem.RELATED:
            title = self.source.split('__')[-1]
        elif self.type == DataItem.NONE:
            pass
        else:
            raise ValueError(u"Tipo DataItem non riconosciuto: '{0:s}'".format(self.type))
        return title

    @classmethod
    def from_model(cls, model):
        def get_related_items(field, attr):
            if django.VERSION >= (1, 8):
                parent_model = field.related.related_model
            else:
                parent_model = field.related.parent_model
            return [DataItem(model, '%s__%s' % (field.name, f), DataItem.RELATED)
                    for f in getattr(parent_model, attr, [])]

        if hasattr(model, '_export_fields'):
            fld = dict([(f.name, f) for f in model._meta.fields])
            retval = [DataItem(model, fld[fname] if fname in fld else fname) for fname in model._export_fields]
        else:
            retval = []
            for f in model._meta.fields:
                appended = []
                if hasattr(f, 'related'):
                    retval += get_related_items(f, '_export_prepend_when_related')
                    appended = get_related_items(f, '_export_append_when_related')
                retval.append(DataItem(model, f, DataItem.FIELD))
                retval += appended
            if hasattr(model, '_export_fields_add'):
                fld = dict([(f.name, f) for f in model._meta.fields])
                for fname in model._export_fields_add:
                    retval.append(DataItem(model, fld[fname] if fname in fld else fname))
        # print [d.source.name if isinstance(d.source, Field) else d.source
        #     for d in retval]
        return retval


class ExcelOutFile(xlwt.Workbook):

    CHAR_WIDTH = 0x100
    MAX_COLUMN_WIDTH = CHAR_WIDTH * 80
    MAX_ROWS_PER_SHEET = 60000

    def __init__(self, encoding='utf8', style_compression=0, workbook_name=None, **kwargs):
        self.count = 0
        self.worksheets_count = 0
        if workbook_name and not workbook_name.lower().endswith(".xls"):
            workbook_name += '.xls'
        self.workbook_name = workbook_name
        self.force_text = kwargs.pop('force_text', False)
        self.__included_models = set()
        super(ExcelOutFile, self).__init__(encoding=encoding, style_compression=style_compression, **kwargs)

    def add_sheet(self, sheetname, cell_overwrite_ok=False):
        self.worksheets_count += 1
        return super(ExcelOutFile, self).add_sheet(sheetname, cell_overwrite_ok)

    def adapt_column(self, column, value):
        if not isinstance(column, xlwt.Column):
            column = self.get_sheet(self.active_sheet).col(column)
        if isinstance(value, xlwt.Formula):
            wd = self.CHAR_WIDTH * 15
        else:
            wd = self.CHAR_WIDTH * len(unicode(value))
        if column.width < wd:
            column.width = min(wd, self.MAX_COLUMN_WIDTH)

    def include_model(self, model):
        try:
            modelname = model._meta.verbose_name_plural
        except Exception:
            modelname = model.__name__
        self.__included_models.add(slugify(modelname))

    def dump_list(self, model, queryset=None, headers=None, list_obj=None, sheetbasename=None, adapt=True):
        pk = model._meta.pk
        fields = DataItem.from_model(model)

        self.include_model(model)

        def set_headers(sheet, adapt):
            """Sets worksheet headers"""
            title_style = EXCEL_STYLES['title']
            if not headers:
                if getattr(model, '_export_skip_pk', False):
                    hdrs = []
                else:
                    hdrs = [force_unicode(pk.verbose_name) or pk.name, ]
                for fld in fields:
                    if not fld.is_pk:
                        hdrs.append(force_unicode(fld.get_title()))
            else:
                hdrs = list(headers)
            for col, header in enumerate(hdrs):
                sheet.write(0, col, force_unicode(header), style=title_style)
                if adapt:
                    self.adapt_column(sheet.col(col), header)

        def set_style(sheet, column_styles):
            """Write column styles"""
            # for c, col in sheet.get_cols().items():
            #     col.set_style(column_styles[c])
            return

        if list_obj is None:
            # Set list_obj from queryset
            assert queryset
            list_obj = queryset.order_by(model._meta.pk.name).iterator()

        sheet_index = 0
        sheet = None
        EACH_ROW = 1000
        r = self.MAX_ROWS_PER_SHEET
        count = 0
        column_styled = False
        column_styles = []
        at_least_one = False
        for obj in list_obj:
            style_forced = False
            at_least_one = True
            count += 1
            r += 1
            if r >= self.MAX_ROWS_PER_SHEET:
                r = 0
                sheetname = sheetbasename or model.__name__
                if sheet_index > 0:
                    sheetname += '_%d' % sheet_index
                    set_style(sheet, column_styles)
                sheet_index += 1
                sheet = self.add_sheet(sheetname)
                set_headers(sheet, adapt)
            if type(obj) in (list, tuple):
                for c, value_instance in enumerate(obj):
                    value, cell_style = get_value_cell_style(value_instance, force_text=self.force_text)
                    if value == '' and cell_style == EXCEL_STYLES['forced_text']:
                        # forza una cella di testo vuota
                        sheet.row(r + 1).set_cell_text(c, '', cell_style)
                    else:
                        sheet.write(r + 1, c, value, style=cell_style)
                    if not column_styled:
                        column_styles.append(cell_style)
                    elif new_style_to_be_forced(cell_style, column_styles[c]):
                        style_forced = True
                        column_styles[c] = cell_style
                    if adapt:
                        self.adapt_column(sheet.col(c), value)
            else:
                c = 0
                if not getattr(model, '_export_skip_pk', False):
                    value = unicode(getattr(obj, pk.name))
                    sheet.write(r + 1, c, value)
                    if adapt:
                        self.adapt_column(sheet.col(c), value)
                    c += 1
                for field in fields:
                    if field.is_pk:
                        continue
                    value, cell_style = field.get_value_cell_style(obj, force_text=self.force_text)
                    if value == '' and cell_style == EXCEL_STYLES['forced_text']:
                        # forza una cella di testo vuota
                        sheet.row(r + 1).set_cell_text(c, '', cell_style)
                    else:
                        sheet.write(r + 1, c, value, style=cell_style)
                    if not column_styled:
                        column_styles.append(cell_style)
                    elif new_style_to_be_forced(cell_style, column_styles[c - 1]):
                        style_forced = True
                        column_styles[c - 1] = cell_style
                    if adapt and value:
                        self.adapt_column(sheet.col(c), value)
                    c += 1
            column_styled = True
            if r:
                if r % EACH_ROW == 0 or style_forced:
                    set_style(sheet, column_styles)
                    if not r % EACH_ROW:
                        sheet.flush_row_data()
        if not at_least_one:
            sheetname = sheetbasename or model.__name__
            sheet = self.add_sheet(sheetname)
            sheet.write(0, 0, u"Nessun record presente")
        self.count += count
        return count

    # def save(self, filename, adapt = True):
    #     super(ExcelOutFile, self).save(filename)

    def get_filename(self, filename_prefix=None):
        if self.workbook_name:
            retval = self.workbook_name
        else:
            suffix = ".%s.xls" % datetime.datetime.today().strftime('%Y%m%d-%H%M')
            if filename_prefix:
                retval = filename_prefix
            elif len(self.__included_models) > 0:
                retval = '_'.join(sorted(list(self.__included_models)))
                if len(retval) > MAX_FILENAME_LENGTH - len(suffix):
                    retval = "misc_data"
            else:
                retval = "exported_data"
            retval += suffix
        return retval

    def as_file(self, filename_prefix=None, zip=False):
        tex = tempfile.NamedTemporaryFile(prefix='binexl', suffix='.xls')
        self.save(tex)
        if zip:
            fname = self.get_filename(filename_prefix)
            try:
                # Apre il buffer per lo zip
                zbuf = tempfile.NamedTemporaryFile(prefix='binxlz', suffix='.xlz')
                z = zipfile.ZipFile(zbuf, 'w', zipfile.ZIP_DEFLATED)
                tex.seek(0)
                z.writestr(fname.encode('ascii', 'ignore'), tex.read())
                z.close()
                tex.close()
            except:
                logger.exception("Errore esportazione xls")
                raise
            retval = zbuf
        else:
            retval = tex

        retval.filesize = retval.tell()
        retval.seek(0)
        retval.count = self.count
        return retval

    def as_http_response(self, filename_prefix=None, attachment=True, zip=False):
        fname = '{0:s}{1}'.format(self.get_filename(filename_prefix), '.zip' if zip else '')
        tmpfile = self.as_file(filename_prefix=filename_prefix, zip=zip)
        content_type = 'application/{0}'.format('zip' if zip else 'vnd.ms-excel')
        response = StreamingHttpResponse(FileWrapper(tmpfile), content_type=content_type)
        response['Content-Disposition'] = '{0}filename={1}'.format('attachment; ' if attachment else '', fname)
        response['Content-Length'] = os.path.getsize(tmpfile.name)
        return response


class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, dialect=csv.excel_tab, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([unicode(s).encode("utf-8") for s in row])

    def save(self, stream):
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        stream.write(data)
        # empty queue
        self.queue.truncate(0)


class CsvOutFile(object):
    def __init__(self):
        self.count = 0
        self.worksheets_count = 1
        self.force_text = True
        self.__included_models = set()
        self.csv_writer = UnicodeWriter()

    def get_filename(self, filename_prefix=None):
        suffix = ".%s.csv" % datetime.datetime.today().strftime('%Y%m%d-%H%M')
        if filename_prefix:
            retval = filename_prefix
        else:
            retval = '_'.join(sorted(list(self.__included_models)))
        retval += suffix
        return retval

    def as_http_response(self, filename_prefix=None, attachment=True, zip=False):
        fname = '{0:s}{1}'.format(self.get_filename(filename_prefix), '.zip' if zip else '')
        tmpfile = self.as_file(filename_prefix=filename_prefix, zip=zip)
        content_type = 'application/{0}'.format('zip' if zip else 'vnd.ms-excel')
        response = StreamingHttpResponse(FileWrapper(tmpfile), content_type=content_type)
        response['Content-Disposition'] = '{0}filename={1}'.format('attachment; ' if attachment else '', fname)
        response['Content-Length'] = os.path.getsize(tmpfile.name)
        return response

    def as_file(self, filename_prefix=None, zip=False):
        tex = tempfile.NamedTemporaryFile(prefix='csvexl', suffix='.csv')
        self.csv_writer.save(tex)
        if zip:
            fname = self.get_filename(filename_prefix)
            try:
                # Apre il buffer per lo zip
                zbuf = tempfile.NamedTemporaryFile(prefix='csvz', suffix='.xlz')
                z = zipfile.ZipFile(zbuf, 'w', zipfile.ZIP_DEFLATED)
                tex.seek(0)
                z.writestr(fname.encode('ascii', 'ignore'), tex.read())
                z.close()
                tex.close()
            except:
                logger.exception("Errore esportazione xls")
                raise
            retval = zbuf
        else:
            retval = tex

        retval.filesize = retval.tell()
        retval.seek(0)
        retval.count = self.count
        return retval

    def dump_list(self, model, queryset=None, headers=None, list_obj=None):
        fields = DataItem.from_model(model)

        try:
            modelname = model._meta.verbose_name_plural
        except Exception:
            modelname = model.__name__
        self.__included_models.add(slugify(modelname))

        if list_obj is None:
            # Set list_obj from queryset
            assert queryset
            list_obj = queryset.order_by(model._meta.pk.name).iterator()

        self.csv_writer.writerow(headers)

        for obj in list_obj:
            self.count += 1
            if type(obj) in (list, tuple):
                values = []
                for c, value_instance in enumerate(obj):
                    value, cell_style = get_value_cell_style(value_instance, force_text=self.force_text)
                    values.append(value)
                self.csv_writer.writerow(values)
            else:
                values = []
                for field in fields:
                    if field.is_pk:
                        continue
                    value, cell_style = field.get_value_cell_style(obj, force_text=self.force_text)
                    values.append(value)
                self.csv_writer.writerow(obj)
        return self.count
