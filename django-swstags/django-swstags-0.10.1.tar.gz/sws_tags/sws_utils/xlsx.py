#!/usr/bin/env python
# encoding: utf-8

import csv
from django.http import HttpResponse, StreamingHttpResponse
from decimal import Decimal
from datetime import date, datetime
from sws_tags.sws_utils.common_utils import *
from sws_tags.sws_utils.messages import *
from sws_tags.sws_utils.cube import *
from sws_tags.sws_utils.pdf_utils import *
import os.path
import traceback

# FOR EXCEL
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from xlsxwriter.workbook import Workbook

# FOR EXCEL GENERATING
import xlwt
ezxf = xlwt.easyxf

from sws_tags.sws_utils.common_utils import *
from sws_tags.sws_utils.messages import *
from sws_tags.sws_utils.cube import *


def getRedirectURL(param_export_file, request, dst_directory='/media'):
    ''' Create a redirect URL depending on the request and wether it is secure or not'''
    if request is not None:
        redirect_url = request.get_host() + '/' + dst_directory + param_export_file['filename']
        redirect_url = redirect_url.replace('//', '/')
        if request.is_secure():
            redirect_url = 'http://' + redirect_url
        else:
            redirect_url = 'https://' + redirect_url
    else:
        redirect_url = dst_directory + param_export_file['filename']

    return redirect_url


class Echo(object):
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


def rounding(cifra, digitos=0, format='Round_up'):
    """Rutina par rounding de cifras decimales como para uso en contabilidad"""
    # Symmetric Arithmetic Rounding for decimal numbers
    if type(cifra) != decimal.Decimal:
        cifra = decimal.Decimal(str(cifra))

    if format == 'Default':
        result = cifra.quantize(decimal.Decimal("1") / (decimal.Decimal('10') ** digitos), decimal.ROUND_HALF_UP)
    elif format == 'Round_up':
        result = cifra.quantize(decimal.Decimal("1") / (decimal.Decimal('10') ** digitos), decimal.ROUND_UP)
    elif format == 'Round_down':
        result = cifra.quantize(decimal.Decimal("1") / (decimal.Decimal('10') ** digitos), decimal.ROUND_DOWN)

    return result


def roundingBill(data, conf):
    new_data = []
    new_total = 0
    new_sum_minutes = 0

    for r in data:
        new_r = {}
        for i in r:
            if i not in conf:
                new_r[i] = r[i]
            elif i == 'sum_total_minutes':
                new_r[i] = rounding(r[i], conf[i][0], conf[i][1])

        for c in conf:
            if c == 'sum_total_income':
                new_sum_total_income = new_r['income'] * new_r['sum_total_minutes']
                new_r[c] = rounding(new_sum_total_income, conf[c][0], conf[c][1])

        new_data.append(new_r)
        new_total = new_total + new_r['sum_total_income']
        new_sum_minutes = new_sum_minutes + new_r['sum_total_minutes']

    sum_data = {}
    sum_data['sum_total_income'] = new_total
    sum_data['sum_total_minutes'] = new_sum_minutes

    return new_data, sum_data


def roundingBillIncome(data, conf):
    new_data = []
    new_total = 0
    new_sum_minutes = 0

    for r in data:

        new_r = {}
        for i in r:
            if i not in conf:
                new_r[i] = r[i]
            elif i == 'minutes':
                new_r[i] = rounding(r[i], conf[i][0], conf[i][1])

        for c in conf:
            if c == 'total_euro':
                new_total_euro = new_r['rate_euro'] * new_r['minutes']
                new_r[c] = rounding(new_total_euro, conf[c][0], conf[c][1])

        new_data.append(new_r)
        new_total = new_total + new_r['total_euro']
        new_sum_minutes = new_sum_minutes + new_r['minutes']

    sum_data = {}
    sum_data['total_euro'] = new_total
    sum_data['minutes'] = new_sum_minutes
    return new_data, sum_data


def ExportFile(qs, param_export_file, request=None):
    def read_and_flush():
        output.seek(0)
        data = output.read()
        output.seek(0)
        output.truncate()
        return data

    def writeInStream():
            row = 0
            col = 0
            for h in headers:
                sheet.write(row, col, h, bold)
                col += 1
            row = 1
            col = 0
            for trr in queryset:
                for c in col_name:
                    if type(trr[c]) == datetime:
                        try:
                            trr[c] = param_export_file['tz'].normalize(trr[c]).strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            trr[c] = str(trr[c])
                    sheet.write(row, col, trr[c])
                    col += 1
                row += 1
                col = 0
                data = read_and_flush()
                yield data

            book.close()
            data = read_and_flush()
            yield data

    def writeBillInStream():
        # //////////////////////////////////////////////   STYLE ///////////////////////////////////
        bold = book.add_format({'bold': 1})
        yellow_bg = book.add_format({'bg_color': '#FFFFFF'})
        grey_bg = book.add_format({'bg_color': '#F7F7F7'})

        grey_dark_bg_bold = book.add_format({'bg_color': '#D7D6D2', 'bold': 1})

        flesh_color_bg = book.add_format({'bg_color': '#FFE8E8'})
        flesh_color_bg_bold = book.add_format({'bg_color': '#FFE8E8', 'bold': 1})

        merge_format_border = book.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#FFE8E8',
            })

        merge_format = book.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#FFE8E8',
            })

        red_format = book.add_format({
            'bold': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#FFB3B3',
            # 'border_color':'#FF3636',
            # 'border':6
            })

        # money = book.add_format({'num_format': '#.##'+param_export_file['data_bill']['type_money'], 'bold': 1})
        # money_grey_bg = book.add_format({'num_format': '#.##'+param_export_file['data_bill']['type_money'], 'bold': 1, 'bg_color': '#F7F7F7'})
        # money_grey_bg_0 = book.add_format({'num_format': '0.####'+param_export_file['data_bill']['type_money'], 'bold': 1, 'bg_color': '#F7F7F7'})
        # money_yellow_bg = book.add_format({'num_format': '#.####'+param_export_file['data_bill']['type_money'], 'bold': 1, 'bg_color': '#FBE067'})
        # money_yellow_bg_0 = book.add_format({'num_format': '0.####'+param_export_file['data_bill']['type_money'], 'bold': 1, 'bg_color': '#FBE067'})

        # minute_grey_bg = book.add_format({'num_format': '#.#', 'bg_color': '#F7F7F7'})
        # minute_grey_bg_0 = book.add_format({'num_format': '0.#', 'bg_color': '#F7F7F7'})
        # minute_yellow_bg = book.add_format({'num_format': '#.#', 'bg_color': '#FBE067'})
        # minute_yellow_bg_0 = book.add_format({'num_format': '0.#', 'bg_color': '#FBE067'})

        # date_format = book.add_format({'num_format': 'mmmm d yyyy'})
        # italic = book.add_format({'italic': True})

        # ///////////////////////////////////////////    DECLARATION /////////////////////////////////////////////
        pattern = xlwt.Pattern()  # Create the Pattern
        pattern.pattern = xlwt.Pattern.SOLID_PATTERN
        style = xlwt.XFStyle()  # Create the Pattern
        style.pattern = pattern

        queryset = param_export_file['data_bill']['raw_cdrts']
        total = param_export_file['data_bill']['cdrt_subtotal']

        col_name = ['destination', 'minutes', 'rate_euro', 'total_euro']
        headers = ['Destination', 'Total Minutes', 'EUR/min', 'Total']

        sheet.set_column('A:A', 5)
        sheet.set_column('B:B', 30)
        sheet.set_column('C:C', 15)
        sheet.set_column('D:D', 15)
        sheet.set_column('E:E', 15)

        sheet.set_column('G:G', 15)

        try:
            sheet.write(1, 1, param_export_file['data_bill']['issuing_company_name'], bold)
            sheet.write(2, 1, param_export_file['data_bill']['issuing_company_address'], bold)
            sheet.write(3, 1, param_export_file['data_bill']['issuing_company_CIF'], bold)
            sheet.insert_image('A1', param_export_file['data_bill']['url_img'], {'x_offset': 260, 'y_offset': 15})
            sheet.merge_range('D2:E4', 'BILL: '+param_export_file['data_bill']['invoice_number'], red_format)
        except:
            pass

        # ///////////////////////////////////////  BILL /////////////////////////////////////////////
        row = 5
        col = 1
        for h in headers:
            sheet.write(row, col, h, grey_dark_bg_bold)
            col += 1
        row = 6
        col = 1

        col_max = len(col_name)
        for trr in queryset:
            for c in col_name:
                if type(trr[c]) == datetime:
                    try:
                        trr[c] = param_export_file['tz'].normalize(trr[c]).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        trr[c] = str(trr[c])
                if row % 2 != 0:
                    sheet.write(row, col, trr[c], yellow_bg)
                else:
                    sheet.write(row, col, trr[c], grey_bg)

                col += 1
            row += 1
            col = 1
            data = read_and_flush()
            yield data

        # /////////////////////////////////////////////// TOTAL ////////////////////////////////////////
        row = row+1
        sheet.write(row, col_max-3, 'Total Minutes', grey_bg)
        sheet.write(row, col_max-2, total['minutes'], grey_bg)
        sheet.write(row, col_max-1, 'Total', grey_bg)
        sheet.write(row, col_max, total['total_euro'], money_grey_bg)
        row = row+1
        sheet.write(row, col_max-1, 'IVA ' + str(param_export_file['data_bill']['VAT']) + '%', grey_bg)
        iva = float(total['total_euro']) * float(param_export_file['data_bill']['VAT'])/100
        sheet.write(row, col_max, iva, money_grey_bg)
        row = row+1
        sheet.write(row, col_max-1, 'Total + IVA', money_grey_bg)
        total_iva = float(total['total_euro']) * (1 + float(param_export_file['data_bill']['VAT'])/100)
        sheet.write(row, col_max, total_iva, money_grey_bg)

        # /////////////////////////////////////////////  FOOTER DATA ////////////////////////////////////////
        row = row + 3
        coordinate = 'B'+str(row)+':E'+str(row)
        period = 'Issue Date: ' + str(param_export_file['data_bill']['issue_date']) + '      Due Date: '+str(param_export_file['data_bill']['due_date'])
        sheet.merge_range(coordinate, period, merge_format_border)
        row = row + 2
        coordinate = 'B'+str(row)+':E'+str(row)
        period = 'Period From: ' + str(param_export_file['data_bill']['from_date']) + '      Period To: '+str(param_export_file['data_bill']['to_date'])
        sheet.merge_range(coordinate, period, merge_format_border)
        row = row + 2

        coordinate = 'B'+str(row)+':E'+str(row)
        period = 'Payment info for client: ' + str(param_export_file['data_bill']['payment'])
        sheet.merge_range(coordinate, period, merge_format)

        row = row-1

        sheet.write(row+1, 1, 'Bank Name:', flesh_color_bg_bold)
        sheet.write(row+2, 1, 'Account:', flesh_color_bg_bold)
        sheet.write(row+3, 1, 'IBAN:', flesh_color_bg_bold)
        sheet.write(row+4, 1, 'SWIFT:', flesh_color_bg_bold)

        sheet.write(row+1, 2, param_export_file['data_bill']['bank_name'], flesh_color_bg)
        sheet.write(row+2, 2, param_export_file['data_bill']['account'], flesh_color_bg)
        sheet.write(row+3, 2, param_export_file['data_bill']['IBAN'], flesh_color_bg)
        sheet.write(row+4, 2, param_export_file['data_bill']['SWIFT'], flesh_color_bg)

        sheet.write(row+1, 3, 'Company:', flesh_color_bg_bold)
        sheet.write(row+2, 3, 'CIF:', flesh_color_bg_bold)
        sheet.write(row+3, 3, 'Adress:', flesh_color_bg_bold)
        sheet.write(row+4, 3, 'Email:', flesh_color_bg_bold)
        sheet.write(row+5, 3, 'Phone:', flesh_color_bg_bold)

        sheet.write(row+1, 4, param_export_file['data_bill']['company'], flesh_color_bg)
        sheet.write(row+2, 4, param_export_file['data_bill']['company_number'], flesh_color_bg)
        sheet.write(row+3, 4, param_export_file['data_bill']['company_address'], flesh_color_bg)
        sheet.write(row+4, 4, param_export_file['data_bill']['company_email'], flesh_color_bg)
        sheet.write(row+5, 4, param_export_file['data_bill']['company_phone'], flesh_color_bg)

        book.close()

        data = read_and_flush()
        yield data

    if 'format' not in param_export_file:
        param_export_file['format'] = 'bill_pdf'

    if 'filename' not in param_export_file:
        param_export_file['filename'] = 'income_provider.pdf'

    if 'multisheet' in param_export_file:
        multisheet = param_export_file['multisheet']
    else:
        multisheet = False

    if param_export_file['format'] == 'excel':
        if multisheet is False:
            param_export_file['filename'] = param_export_file['filename']+'_' + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))+'.xlsx'

            queryset = qs
            headers = param_export_file['headers']
            col_name = param_export_file['col_name']
            filename = param_export_file['filename']

            if type(queryset) is not list:
                queryset = queryset.iterator()
            try:
                output = StringIO.StringIO()
                filename = param_export_file['STATIC_URL'] + '/excel_csv/' + param_export_file['filename']
                book = Workbook(output, {'constant_memory': True})
                sheet = book.add_worksheet('test')
                bold = book.add_format({'bold': 1})
                col = 0
                row = 0
                for h in headers:
                        sheet.write(row, col, h, bold)
                        col += 1
                row = 1
                col = 0
                for trr in queryset:
                    for c in col_name:
                        if c in trr:
                            if type(trr[c]) == datetime:
                                try:
                                    trr[c] = param_export_file['tz'].normalize(trr[c]).strftime('%Y-%m-%d %H:%M:%S')
                                except:
                                    trr[c] = str(trr[c])

                            if type(trr[c]) is tuple:
                                sheet.write(row, col, trr[c][0], book.add_format(trr[c][1]))
                            else:
                                sheet.write(row, col, trr[c])
                        col += 1
                    row += 1
                    col = 0
                book.close()

            except Exception:
                swslog('error', 'Error in create Excel: ', traceback.format_exc())
            output.seek(0)
            response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = "attachment; filename="+param_export_file['filename']
        else:
            param_export_file['filename'] = param_export_file['filename']+'_' + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))+'.xlsx'

            queryset = param_export_file['queryset']
            headers = param_export_file['headers']
            col_name = param_export_file['col_name']
            filename = param_export_file['filename']
            validation = param_export_file['validation']

            try:
                output = StringIO.StringIO()
                filename = param_export_file['STATIC_URL']+'/excel_csv/' + param_export_file['filename']
                book = Workbook(filename, {'constant_memory': True})

                for i in range(0, len(headers)):
                    sheet = book.add_worksheet(param_export_file['sheet'][i])
                    sheet.set_column('A:A', 30)
                    sheet.set_column('B:B', 30)

                    bold = book.add_format({'bold': 1})
                    col = 0
                    row = 0
                    for h in headers[i]:
                            sheet.write(row, col, h, bold)
                            col += 1
                    row = 1
                    col = 0

                    for trr in queryset[i]:
                        for c in col_name[i]:
                            if c in trr:
                                if type(trr[c]) == datetime:
                                    try:
                                        trr[c] = param_export_file['tz'].normalize(trr[c]).strftime('%Y-%m-%d %H:%M:%S')
                                    except:
                                        trr[c] = str(trr[c])

                                sheet.write(row, col, trr[c])
                            col += 1
                        row += 1
                        col = 0
                #sheet.data_validation('$B$2:$B$10000', {'validate': 'list','source': '=Destinations!$A$2:$A$10000'})
                sheet.data_validation(validation[0], validation[1])
                book.close()
            except:
                swslog('error', 'Error in create Excel: ', traceback.format_exc())

            output.seek(0)
            response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = "attachment; filename="+param_export_file['filename']
        return response

    # CSV case
    elif param_export_file['format'] == 'csv':
        param_export_file['filename'] = param_export_file['filename']+'_'+str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))+'.csv'
        try:
            col_title = param_export_file.get('headers', None)
            col_name = param_export_file['col_name']
        except:
            try:
                col_name = param_export_file['col_name']
            except:
                col_name = None
        csv_writer = csv.writer(Echo(), dialect='excel', quoting=csv.QUOTE_MINIMAL, delimiter='|')

        response = StreamingHttpResponse((csv_writer.writerow(row) for row in get_csv_query(param_export_file['request_data'], qs, param_export_file['STATIC_URL'] + '/excel_csv/' + param_export_file['filename'], col_name, col_title, tz=param_export_file['tz'])), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=' + param_export_file['filename']
        return response

    elif param_export_file['format'] == 'bill':

        param_export_file['filename'] = param_export_file['filename']+'_' + str(datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))+'.xlsx'
        filename = param_export_file['filename']
        output = StringIO.StringIO()

        book = Workbook(output)
        sheet = book.add_worksheet('data')

        book.set_properties({
            'title':    param_export_file['filename'],
            'subject':  'Bill',
            'author':   param_export_file['autor'],
            'manager':  'StoneWorkSolutions',
            'company':  'StoneWorkSolutions',
            'category': 'Bill and risk',
            'keywords': 'Bill',
            'comments': 'Created in portal international'})

        response = HttpResponse(writeBillInStream(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = "attachment; filename=" + filename
        return response
    elif param_export_file['format'] == 'bill_pdf':
        render_to_pdf_result = render_to_pdf('tags/pdf_format.html', context_instance=param_export_file, header_template=None, footer_template='tags/tag_footer.html', filename=param_export_file['filename'])
        if param_export_file['filename']:
            if not os.path.isfile(param_export_file['filename']):
                raise Exception('File {0} couldn\'t be created'.format(param_export_file['filename']))
        return render_to_pdf_result


def get_csv_query(request, queryset, filename, col_order=None, col_title=None, in_stream=False, tz=None):
    try:
        if type(queryset) is not list:
            # Get field names
            field_names = []
            if col_order:
                field_names = col_order
            else:
                for f in queryset._fields:
                    field_names.append(unicode(getFieldVerboseName(queryset, f)))
                for f in getattr(queryset, 'aggregate_names', []):
                    field_names.append(f)

            # Get field types
            field_types = []
            for f in queryset._fields:
                field_types.append(unicode(getFieldType(queryset, f)))
            for f in getattr(queryset, 'aggregate_names', []):
                try:
                    field_types.append(unicode(getFieldType(queryset, f)))
                except:
                    field_types.append(u'FloatField')
            cont = 0
            first_it = True
            for q in queryset.iterator():
                if first_it:
                    first_it = False
                    if col_title:
                        yield col_title
                    else:
                        yield field_names
                aux = []
                i = 0
                for f in field_names:

                    if field_types[i] == 'DateTimeField':
                        try:
                            aux.append(pytz.utc.normalize(q[f]).astimezone(tz).strftime('%Y-%m-%d %H:%M:%S'))
                        except:
                            aux.append(q[f])
                    else:
                        aux.append(q[f])
                    i += 1
                for f in getattr(queryset, 'aggregate_names', []):
                    aux.append(q[f])
                cont += 1
                yield aux

        else:
            field_names = []

            if col_order:
                field_names = col_order
            else:
                for k, v in queryset[0].items():
                    field_names.append(unicode(k))

            first = True
            cont = 0
            # v_data.append(q[k])
            for i in range(-1, len(queryset)):
                if first:
                    first = False
                    yield col_title
                else:
                    v_data = []
                    for k in field_names:
                        if k in queryset[i]:
                            v_data.append(queryset[i][k])
                    cont += 1
                    yield v_data

    except Exception, e:
        swslog('error', 'get_csv_query', e)
        yield None


def get_field_types(fields):
    field_types = []
    found = False
    for lf in fields:
        found = False
        if type(lf) == unicode:
            field_types.append('text')
            found = True
        elif type(lf) == long:
            field_types.append('int')
            found = True
        elif type(lf) == int:
            field_types.append('int')
            found = True
        elif type(lf) == bool:
            field_types.append('boolean')
            found = True
        elif type(lf) == float:
            field_types.append('price')
            found = True
        elif type(lf) == Decimal:
            field_types.append('price')
            found = True
        elif type(lf) == date:
            field_types.append('date')
            found = True
        elif type(lf) == datetime:
            field_types.append('date')
            found = True
        if found is not True:
            field_types.append('text')
    return field_types


def listToExport(main_fields, remove_fields=None, seconds=None):
    '''Remove fields which must not be in export_file
    :param main_fields: all fields of the grid
    :type main_fields: list
    :param remove_fields: fields to remove
    :type remove_fields: list
    :param seconds: repeated fields, we only want to remove the second, defaults to []
    :type seconds: list, optional
    :returns: the fields which will appear in the file to export
    :rtype: {list}
    '''
    if not remove_fields:
        remove_fields = []
    if not seconds:
        seconds = []
    for remove_field in remove_fields:
        if remove_field in seconds:
            main_fields.reverse()
        try:
            main_fields.remove(remove_field)
        except ValueError:
            pass
        if remove_field in seconds:
            main_fields.reverse()
    return main_fields
