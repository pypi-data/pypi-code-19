# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pytz
from measurements import (
    HOBOWareMeasurement, HOBOLinkMeasurement, SmartThingsMeasurement,
    LCDMeasurement, TMYMeasurement)
import plot
reload(plot)


class Export():
    """
       """

    def __init__(self):
        self.path = str()
        self.data = pd.DataFrame()
        self.tz = str()
        self.app = str()
        self.meas = str()
        self.meas_list = list()
        self.meas_df = pd.DataFrame()
        self.name = str()

    def make_measurements(self, w, **kwargs):
        """
           """
        if self.data.empty:
            print "No raw data stored:"
            print "    " + self.path
        else:
            for column_header in self.data.columns:
                if 'state_logger_labels' in kwargs:
                    m = self.meas.make(self.data[column_header],
                                       self.name.split('_')[0], w,
                                       state_logger_labels=kwargs[
                                       'state_logger_labels'])
                else:
                    m = self.meas.make(self.data[column_header],
                                       self.name.split('_')[0], w)
                self.meas_list.append(m)

    def convert_measurement_tz(self, tz):
        """
           """
        if self.meas_list == list():
            print "No Measurements in measurement list:"
            print "    " + self.path
        else:
            for m in self.meas_list:
                m.data.index = m.data.index.tz_convert(pytz.timezone(tz))
        self.meas_df = pd.DataFrame()
        self.make_df()

    def make_df(self):
        """
           """
        if self.meas_list == list():
            print "No Measurements in measurement list."
        else:
            for m in self.meas_list:
                self.meas_df[m.meas_des] = m.data

    def find_duplicates(self):
        """Give duplicate column names unique identifiers.
           """
        # TODO: Method assumes max of two repeted column names
        for m1 in self.meas_list:
            found = False
            for m2 in self.meas_list:
                if ((m1.name == m2.name) and (m1.quant == m2.quant) and
                   (m1 != m2)):
                    m1.name += 'x1'
                    m2.name += 'x2'
                    m1.meas_des = m1.name + ' ' + m1.quant
                    m2.meas_des = m2.name + ' ' + m2.quant
                    found = True
                    break
            if found:
                break

    def reassign_meas_des(self, path):
        """Re-assign the measuement description of each Measurement in
           Export.meas_list according to work book at path.
           """
        df = pd.read_csv(path, dtype=str)
        for m in self.meas_list:
            site_id = m.name.split('_')[0]
            meter_id = m.name.split('_')[1]
            sensor_id = m.name.split('_')[2]
            quant = m.quant
            site_rows = df[df['Site Label'] == site_id]
            meter_rows = site_rows[site_rows[
                'Meter Serial Number'] == meter_id]
            sensor_rows = meter_rows[meter_rows[
                'Sensor Serial Number'] == sensor_id]
            quantity_rows = sensor_rows[sensor_rows[
                'Quantity (updated)'] == quant]
            if len(quantity_rows) >= 1:
                m.meas_des = (quantity_rows.iloc[0]['Measurement Description'])
            else:
                print ('No Matches in measurement description workbook for: ' +
                       m.name)


class HOBOWareExport(Export):
    """
       """

    def __init__(self, path):
        Export.__init__(self)
        self.path = path
        # self.app = 'HOBOWare'
        self.meas = HOBOWareMeasurement

    def read_file(self):
        """
           """
        if '.csv' in self.path:
            self.data = pd.read_csv(self.path, header=1, low_memory=False)
        elif '.h5' in self.path:
            self.data = pd.read_hdf(self.path)
            self.data = self.data.replace('NaN', np.nan)

    def get_name(self):
        """
           """
        self.name = (self.path.split('\\')[-1].split('_')[0] + '_' +
                     self.data.columns[2].split('LGR S/N: ')[1].split(',')[0])

    def get_tz(self):
        """
           """
        self.tz = -int(self.data.columns[1].split('-')[1].split(':')[0])

    def set_index(self):
        """
           """
        self.data.set_index(self.data.columns[1], inplace=True)
        # Files saved in UTF8 format can given a format
        try:
            self.data.index = pd.to_datetime(self.data.index,
                                             format='%m/%d/%y %I:%M:%S %p')
        # Otherwise they need to be infered
        except ValueError:
            self.data.index = pd.to_datetime(self.data.index)
        self.data.index = self.data.index.tz_localize(
            pytz.FixedOffset(self.tz * 60)).tz_convert('UTC')

    def clean_data(self):
        """
           """
        # Delete rows containing the string 'Logged'
        # TODO: only delete rows with 'Logged' and nans
        for column_index in range(len(self.data.columns)):
            series = self.data.ix[:, column_index]
            self.data = self.data[self.data[
                series.name].astype(str).str.contains('Logged') == False]
        extra_columns = ['Batt', 'DewPt', 'Host Connected', 'Button Down',
                         'Button Up', 'Stopped', 'End Of File', 'Calibration',
                         'Host', 'Line Resume', 'Started']
        for column_header in self.data:
            if any(s in column_header for s in extra_columns):
                del self.data[column_header]
        del self.data[self.data.columns[0]]
        self.data.dropna(inplace=True)
        for column_label in self.data.columns:
            if self.data.empty == False:
                self.data[column_label] = pd.to_numeric(
                    self.data[column_label])
        self.data = self.data[self.data > -800]  # Filter -888 errors

    @staticmethod
    def make(path, w, **kwargs):
        """kwargs: state_logger_labels
           """
        e = HOBOWareExport(path)
        e.read_file()
        e.get_name()
        e.get_tz()
        e.set_index()
        e.clean_data()
        if 'state_logger_labels' in kwargs:
            e.make_measurements(
                w, state_logger_labels=kwargs['state_logger_labels'])
        else:
            e.make_measurements(w)
        e.find_duplicates()
        e.make_df()
        return e


class HOBOLinkExport(Export):
    """
       """

    def __init__(self, path, tz):
        Export.__init__(self)
        self.path = path
        # self.app = 'HOBOLink'
        self.meas = HOBOLinkMeasurement
        self.tz = tz            # UTC Offset

    def read_file(self):
        """
           """
        if '.csv' in self.path:
            self.data = pd.read_csv(self.path, low_memory=False)
        elif '.xlsx' in self.path:
            self.data = pd.read_excel(self.path)
        elif '.h5' in self.path:
            self.data = pd.read_hdf(self.path)
            self.data = self.data.replace('NaN', np.nan)

    def get_name(self):
        """
           """
        self.name = (self.path.split('\\')[-1].split('-')[0] + '_' +
                     self.data.columns[3].split(':')[0].split(' ')[-1])

    def pre_clean_data(self):
        """
           """
        self.data.dropna(axis=1, how='all', inplace=True)
        self.data.dropna(axis=0, how='all', inplace=True)
        self.data = self.data[self.data > -800]  # Filter -888 errors

    def set_index(self):
        """
           """
        index = (self.data['Date'].astype(str) + ' ' +
                 self.data['Time'].astype(str))
        self.data.set_index(index, inplace=True)
        self.data.index = pd.to_datetime(self.data.index,
                                         format='%m/%d/%y %H:%M:%S')
        if type(self.tz) == int:
            self.data.index = self.data.index.tz_localize(
                pytz.FixedOffset(self.tz * 60)).tz_convert('UTC')
        elif type(self.tz) == str:
            self.data.index = self.data.index.tz_localize(
                pytz.timezone(self.tz)).tz_convert('UTC')

    def post_clean_data(self):
        """
           """
        extra_columns = ['Line#', 'Dew Point', 'Batter',
                         'Date', 'Time']
        for column_header in self.data:
            if any(s in column_header for s in extra_columns):
                del self.data[column_header]
        for column_label in self.data.columns:
            if self.data.empty == False:
                self.data[column_label] = pd.to_numeric(
                    self.data[column_label])

    @staticmethod
    def make(path, tz, w):
        """
           """
        e = HOBOLinkExport(path, tz)
        e.read_file()
        e.get_name()
        e.pre_clean_data()
        e.set_index()
        e.post_clean_data()
        e.make_measurements(w)
        e.find_duplicates()
        e.make_df()
        return e


class SmartThingsExport(Export):
    """
       """

    def __init__(self, file_path):
        Export.__init__(self)
        self.path = file_path
        # self.app = 'SmartThings'
        self.meas = SmartThingsMeasurement
        self.tz = 0             # UTC Offset

    def read_file(self):
        file_ext = self.path.split('\\')[-1].split('.')[1].lower()
        if file_ext == 'xlsx':
            self.data = pd.read_excel(self.path)
        elif file_ext == 'csv':
            self.data = pd.read_csv(self.path)
        elif file_ext == 'h5':
            self.data = pd.read_hdf(self.path)

    def get_name(self):
        """
           """
        self.name = (self.path.split('\\')[-1].split('-')[0] + ' ' +
                     self.path.split('\\')[-1].split('-')[1].split('.')[0])

    def pre_clean_data(self):
        """
           """
        self.data.dropna(axis=1, how='all', inplace=True)
        self.data.dropna(axis=0, how='all', inplace=True)

    def set_index(self):
        """
           """
        index = (self.data.created_at.str.split(' ').str[0] + ' ' +
                 self.data.created_at.str.split(' ').str[1])
        self.data.set_index(index, inplace=True)
        self.data.index = pd.to_datetime(self.data.index,
                                         format='%Y-%m-%d %H:%M:%S')
        self.data.index = self.data.index.tz_localize(
            pytz.FixedOffset(self.tz * 60)).tz_convert('UTC')

    def post_clean_data(self):
        """
           """
        for column_name in self.data.columns:
            if (column_name != 'field1') and (column_name != 'field2'):
                del self.data[column_name]
        # Not sure why this throws na invalid type comp error, but catch here
        try:
            self.data = self.data[self.data['field2'] != 'null']
        except TypeError:
            pass
        try:
            self.data = self.data[self.data['field1'] != 'null']
        except TypeError:
            pass
        for column_label in self.data.columns:
            if self.data.empty == False:
                self.data[column_label] = pd.to_numeric(
                    self.data[column_label])
        # Filter data for periods of constant values
        # (see empower jupyter notebook)
        # Power constant for one hour
        df = self.data.copy()
        for i in range(1, 61, 1):
            df['field1 (' + str(i) + ')'] = df['field1'].shift(i)
            df['field2 (diff)'] = df['field2'].diff()
        # Energy constant for twenty minutes
        for i in range(1, 21, 1):
            df['field2 (diff ' + str(i) + ')'] = df[
                    'field2 (diff)'].shift(i)
        # Apply filter
        df['field1'] = np.where(
            (df['field1'] == df['field1 (1)']) &
            (df['field1'] == df['field1 (2)']) &
            (df['field1'] == df['field1 (3)']) &
            (df['field1'] == df['field1 (4)']) &
            (df['field1'] == df['field1 (5)']) &
            (df['field1'] == df['field1 (6)']) &
            (df['field1'] == df['field1 (7)']) &
            (df['field1'] == df['field1 (8)']) &
            (df['field1'] == df['field1 (9)']) &
            (df['field1'] == df['field1 (10)']) &
            (df['field1'] == df['field1 (11)']) &
            (df['field1'] == df['field1 (12)']) &
            (df['field1'] == df['field1 (13)']) &
            (df['field1'] == df['field1 (14)']) &
            (df['field1'] == df['field1 (15)']) &
            (df['field1'] == df['field1 (16)']) &
            (df['field1'] == df['field1 (17)']) &
            (df['field1'] == df['field1 (18)']) &
            (df['field1'] == df['field1 (19)']) &
            (df['field1'] == df['field1 (20)']) &
            (df['field1'] == df['field1 (21)']) &
            (df['field1'] == df['field1 (22)']) &
            (df['field1'] == df['field1 (23)']) &
            (df['field1'] == df['field1 (24)']) &
            (df['field1'] == df['field1 (25)']) &
            (df['field1'] == df['field1 (26)']) &
            (df['field1'] == df['field1 (27)']) &
            (df['field1'] == df['field1 (28)']) &
            (df['field1'] == df['field1 (29)']) &
            (df['field1'] == df['field1 (30)']) &
            (df['field1'] == df['field1 (31)']) &
            (df['field1'] == df['field1 (32)']) &
            (df['field1'] == df['field1 (33)']) &
            (df['field1'] == df['field1 (34)']) &
            (df['field1'] == df['field1 (35)']) &
            (df['field1'] == df['field1 (36)']) &
            (df['field1'] == df['field1 (37)']) &
            (df['field1'] == df['field1 (38)']) &
            (df['field1'] == df['field1 (39)']) &
            (df['field1'] == df['field1 (40)']) &
            (df['field1'] == df['field1 (41)']) &
            (df['field1'] == df['field1 (42)']) &
            (df['field1'] == df['field1 (43)']) &
            (df['field1'] == df['field1 (44)']) &
            (df['field1'] == df['field1 (45)']) &
            (df['field1'] == df['field1 (46)']) &
            (df['field1'] == df['field1 (47)']) &
            (df['field1'] == df['field1 (48)']) &
            (df['field1'] == df['field1 (49)']) &
            (df['field1'] == df['field1 (50)']) &
            (df['field1'] == df['field1 (51)']) &
            (df['field1'] == df['field1 (52)']) &
            (df['field1'] == df['field1 (53)']) &
            (df['field1'] == df['field1 (54)']) &
            (df['field1'] == df['field1 (55)']) &
            (df['field1'] == df['field1 (56)']) &
            (df['field1'] == df['field1 (57)']) &
            (df['field1'] == df['field1 (58)']) &
            (df['field1'] == df['field1 (59)']) &
            (df['field2 (diff)'] == df['field2 (diff 1)']) &
            (df['field2 (diff)'] == df['field2 (diff 2)']) &
            (df['field2 (diff)'] == df['field2 (diff 3)']) &
            (df['field2 (diff)'] == df['field2 (diff 4)']) &
            (df['field2 (diff)'] == df['field2 (diff 5)']) &
            (df['field2 (diff)'] == df['field2 (diff 6)']) &
            (df['field2 (diff)'] == df['field2 (diff 7)']) &
            (df['field2 (diff)'] == df['field2 (diff 8)']) &
            (df['field2 (diff)'] == df['field2 (diff 9)']) &
            (df['field2 (diff)'] == df['field2 (diff 10)']) &
            (df['field2 (diff)'] == df['field2 (diff 11)']) &
            (df['field2 (diff)'] == df['field2 (diff 12)']) &
            (df['field2 (diff)'] == df['field2 (diff 13)']) &
            (df['field2 (diff)'] == df['field2 (diff 14)']) &
            (df['field2 (diff)'] == df['field2 (diff 15)']) &
            (df['field2 (diff)'] == df['field2 (diff 16)']) &
            (df['field2 (diff)'] == df['field2 (diff 17)']) &
            (df['field2 (diff)'] == df['field2 (diff 18)']) &
            (df['field2 (diff)'] == df['field2 (diff 19)']) &
            (df['field2 (diff)'] == df['field2 (diff 20)']) &
            (df['field2 (diff)'] == 0),
            np.nan, df['field1'])
        self.data = df
        for column_label in self.data.columns:
            if column_label != 'field1':
                del self.data[column_label]
        self.data.dropna(inplace=True)
        for column_label in self.data.columns:
            if self.data.empty == False:
                self.data[column_label] = pd.to_numeric(
                    self.data[column_label])

    @staticmethod
    def make(path, w):
        """
           """
        e = SmartThingsExport(path)
        e.read_file()
        e.get_name()
        e.pre_clean_data()
        e.set_index()
        e.post_clean_data()
        e.make_measurements(w)
        e.find_duplicates()
        e.make_df()
        return e


class LCDExport(Export):
    """Local Climatological Data (LCD) export class
       """

    def __init__(self, path):
        Export.__init__(self)
        self.meas = LCDMeasurement
        self.path = path

    def get_name(self):
        self.name = ('WBAN: ' + self.path.split('\\')[-1].split('.')[0] +
                     '_LCD')

    def read_data(self):
        file_ext = self.path.split('\\')[-1].split('.')[1].lower()
        if file_ext == 'xlsx':
            self.data = pd.read_excel(self.path)
        elif file_ext == 'csv':
            self.data = pd.read_csv(self.path)
        elif file_ext == 'h5':
            self.data = pd.read_hdf(self.path)

    def get_tz(self):
        self.tz = -5

    def pre_clean_data(self):
        keep = ['HOURLYDRYBULBTEMPF', 'HOURLYRelativeHumidity',
                'HOURLYWindSpeed', 'DATE']
        for column_name in self.data.columns:
            if column_name not in keep:
                del self.data[column_name]

    def set_index(self):
        self.data.index = self.data['DATE'].values
        del self.data['DATE']
        self.data.index = pd.to_datetime(self.data.index)
        self.data.index = self.data.index.tz_localize(
            pytz.FixedOffset(self.tz * 60)).tz_convert('UTC')

    def post_clean_data(self):
        for column_name in self.data.columns:
            self.data[column_name] = (
                self.data[column_name].str.replace('s', ''))
            self.data[column_name] = (
                self.data[column_name][self.data[column_name] != '*'])
        self.data = self.data.apply(pd.to_numeric)

    @staticmethod
    def make(path, w):
        e = LCDExport(path)
        e.read_data()
        e.get_name()
        e.get_tz()
        e.pre_clean_data()
        e.set_index()
        e.post_clean_data()
        e.make_measurements(w)
        e.find_duplicates()
        e.make_df()
        return e


class TMYExport(Export):
    """Typical Meteorological Year 3 (TMY/TMY3) export class
       """

    def __init__(self, path, start_date, end_date):
        Export.__init__(self)
        self.meas = TMYMeasurement
        self.path = path
        self.start_date = start_date
        self.end_date = end_date

    def read_data(self):
        self.data = pd.read_csv(self.path, header=1)

    def get_name(self):
        self.name = ('USAF: ' + self.path.split('\\')[-1].split('.')[0] +
                     '_TMY')

    def get_tz(self):
        tmp_df = pd.read_csv(self.path)
        self.tz = float(tmp_df.columns[3])

    def pre_clean_data(self):
        # Delete unwanted columns
        for column_id in self.data.columns:
            keep = ['Date (MM/DD/YYYY)', 'Time (HH:MM)',
                    'Dry-bulb (C)', 'RHum (%)', 'Wspd (m/s)']
            if column_id not in keep:
                del self.data[column_id]
        # Convert to engilsh units
        self.data['Dry-bulb (C)'] = self.data['Dry-bulb (C)'] * 9 / 5. + 32.
        self.data['Wspd (m/s)'] = self.data['Wspd (m/s)'] * 2.237
        # Rename columns
        self.data.columns = [
            'Date (MM/DD/YYYY)', 'Time (HH:MM)',
            'Tdb [deg F]', 'RH [%]', 'Wind Speed [mi/h]']
        tmp_hr = self.data[
            'Time (HH:MM)'].str.split(':', expand=True)[0].apply(pd.to_numeric)
        tmp_min = self.data[
            'Time (HH:MM)'].str.split(':', expand=True)[1]
        tmp_hr -= 1
        tmp_hr = tmp_hr.apply(str).str.zfill(2)
        self.data['Time (HH:MM)'] = tmp_hr + ':' + tmp_min

    def set_index(self):
        # Correcting for varying years of TMY data
        frames = list()
        start_year = int(self.start_date.split('/')[2])
        end_year = int(self.end_date.split('/')[2])
        for i in np.arange(start_year, end_year + 1, 1):
            temp_df = self.data.copy()
            temp_df['Date (MM/DD/YYYY)'] = temp_df[
                'Date (MM/DD/YYYY)'].str[0:6] + str(i)
            frames.append(temp_df)
        self.data = pd.concat(frames)
        self.data.index = self.data['Date (MM/DD/YYYY)'] + ' ' + self.data[
            'Time (HH:MM)']
        del self.data['Date (MM/DD/YYYY)'], self.data['Time (HH:MM)']
        self.data.index = pd.to_datetime(
            self.data.index, format='%m/%d/%Y %H:%M')
        self.data.index = self.data.index.tz_localize(
            pytz.FixedOffset(self.tz * 60)).tz_convert('UTC')

    def post_clean_data(self):
        self.data = self.data.apply(pd.to_numeric)
        self.data = self.data.loc[self.start_date:self.end_date]

    @staticmethod
    def make(path, start_date, end_date, w):
        e = TMYExport(path, start_date, end_date)
        e.read_data()
        e.get_name()
        e.get_tz()
        e.pre_clean_data()
        e.set_index()
        e.post_clean_data()
        e.make_measurements(w)
        e.find_duplicates()
        e.make_df()
        return e
