# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import pytz
from measurements import (
    HOBOWareMeasurement, HOBOLinkMeasurement, SmartThingsMeasurement,
    LCDMeasurement, TMYMeasurement)
import plot
reload(plot)
from plot import qc_plots


class MeasurementGroup():
    """Class for merging arbitrary groups of Measurement objects
       """

    def __init__(self):
        self.name = str()
        self.meas_list = list()  # List of Measurement objects
        self.dataframe_list = list()  # List of DataFrames form Export objects
        self.meas_df = pd.DataFrame()  # DataFrame of series from Measurements
        self.meas_grp = str()  # MeasurementGroup subclass
        self.concat_method = str()

    def concat_measurements(self, w, tz):
        """Identify and concatenate Measurement objects representing the same
           physical measurement

           :param str w: Sampling frequency of concatenated Measurements
           :param str tz: Time zone of index of concatenated Measurements
           """
        to_del = list()
        for m1 in self.meas_list:
            for m2 in self.meas_list:
                if ((m1 != m2) and (m1.meas_des == m2.meas_des) and
                   (m1 not in to_del) and (m2 not in to_del)):
                    m1.data = m1.data.combine_first(m2.data)
                    m1.data = m1.data.resample(w).mean()
                    m1.data.index = m1.data.index.tz_convert(tz)
                    to_del.append(m2)
        for m in to_del:
            del self.meas_list[self.meas_list.index(m)]
        self.concat_method = 'concat_measurements'

    def concat_dataframes(self):
        """Concatenate DataFrames from list of Export objects, method assumes
           equal number of columns constant ordering of labels for all
           DataFrames being combind
           """
        if len(self.dataframe_list) > 1:
            self.meas_df = pd.concat(self.dataframe_list)
            self.meas_df.sort_index(inplace=True)
            self.meas_df = self.meas_df.groupby(self.meas_df.index).first()
            self.concat_method = 'concat_dataframes'
        elif len(self.dataframe_list) == 1:
            self.meas_df = self.dataframe_list[0]
            self.meas_df.sort_index(inplace=True)
            self.meas_df = self.meas_df.groupby(self.meas_df.index).first()
            self.concat_method = 'concat_dataframes'
        else:
            print 'No data present'

    def to_df(self):
        """Combine Measurements in measurement list into DataFrame
           """
        data = list()
        for m in self.meas_list:
            data.append(m.data)
        if len(data) > 0:
            self.meas_df = pd.concat(data, axis=1)
            self.meas_df.sort_index(inplace=True)
        else:
            print 'No data present'

    def qc_plots(self, output_dir, start_date, end_date, w, tz):
        """Plot data of Measurement objects and write to PDF

           :param str output_dir: Path to directory to write file
           :param str start_date: Left x-axis bound of time series
           :param str end_date: Right x-axis bound of time series
           :param str concat_method: Method used to concatenate Export data
           """
        qc_plots(self, output_dir, start_date, end_date, w, tz)


class Location(MeasurementGroup):
    """MeasurementGroup subclass, implements methods specific to groupings of
       data sharing a geographic location
       """

    def __init__(self):
        MeasurementGroup.__init__(self)
        self.meas_grp = Location  # MeasurementGroup subclass
        self.address = str()

    def get_weather_data(self, input_dir, output_dir, w, season):
        """Download and process historical and normal weather data

           :param str input_dir: Path to directory containing 'options.csv'
                                 and 'stations.csv'
           :param str output_dir: Path to directory where weather data will be
                                  written
           :param str w: sampling frequency (ex: '1Min')
           :param str season: 'heating' or 'cooling' or ''
        """
        print 'Method broken by updated NOAA API'
        # # TODO: The heating and cooling seasons will vary by location,
        # #       here assumes NE, also need to pull year from input data
        # if season == 'heating':
        #     start_date = '11/01/' + str(self.meas_df.index[0].year)
        #     end_date = '04/30/' + str(self.meas_df.index[-1].year)
        # elif season == 'cooling':
        #     start_date = '05/01/' + str(self.meas_df.index[0].year)
        #     end_date = '09/30/' + str(self.meas_df.index[-1].year)
        # # Get historical weather data
        # ht, hrh = get_historical_weather(input_dir, output_dir, self.name,
        #                                  self.address, start_date,
        #                                  end_date, w)
        # m = Measurement(ht, self.name, w)
        # m.quant = 'Historical Temperature'
        # m.dim = 'F'
        # m.meas_des = m.name + ' ' + m.quant
        # self.meas_list.append(m)
        # m = Measurement(hrh, self.name, w)
        # m.quant = 'Historical Relative Humidity'
        # m.dim = '%'
        # m.meas_des = m.name + ' ' + m.quant
        # self.meas_list.append(m)
        # # Get normal weather data
        # nt, nrh = get_normal_weather(self.name, start_date, end_date,
        #                              output_dir, w)
        # m = Measurement(nt, self.name, w)
        # m.quant = 'Normal Temperature'
        # m.dim = 'F'
        # m.meas_des = m.name + ' ' + m.quant
        # self.meas_list.append(m)
        # m = Measurement(nrh, self.name, w)
        # m.quant = 'Normal Relative Humidity'
        # m.dim = '%'
        # m.meas_des = m.name + ' ' + m.quant
        # self.meas_list.append(m)

    @staticmethod
    def make(export_list, location_id, concat_method, w, tz):
        """Static way of calling all routine methods of Location class

           :param list export_list: List of Export objects
           :param str location_id: Location object ID
           :param str concat_method: Method used to concatenate Export data
           :return: Location object with merged Export data
           :rtype: Location
           """
        loc = Location()
        for e in export_list:
            loc.meas_list.extend(e.meas_list)
            loc.dataframe_list.append(e.meas_df)
        if concat_method == 'concat_measurements':
            loc.concat_measurements(w, tz)
            loc.to_df()
        elif concat_method == 'concat_dataframes':
            loc.concat_dataframes()
        loc.name = location_id
        return loc


class Measurement():
    """Class for operating on a single column of time series data
       """

    def __init__(self, data, name, w):
        self.data = data
        self.label = str()
        self.quant = str()  # Quantity being measured
        self.dim = str()  # Dimensions of quantity
        self.name = name
        self.w = w  # Sampling frequency
        self.meas_des = str()  # Unique measurment description
        self.state_logger_labels = list()  # List of labels of state loggers

    # TODO: Finish documentation of this method
    def interpolate_count(self):
        """Pulse count interpolation method

           Notes
           -----
           Method calculates time delta between values
           """
        df = pd.DataFrame()
        df['count'] = self.data
        df['time'] = self.data.index
        # Calculate time difference between values in minutes
        df['diff'] = df['time'].diff()
        # Use of 'diff int' is a misnomer, values are not always integers
        df['diff int'] = df['diff'].astype('timedelta64[s]') / 60.0
        del df['time'], df['diff']
        df = df[pd.notnull(df['diff int'])]
        # Sampling interval dictionary
        # Three cases for interpolation
        #    1. Sampling frequency is equal to desired frequency
        #    2. Sampling frequency is higher than desired
        #    3. Sampling frequency is lower than desired
        # Typical sampling intervals used
        sd = {'1Min': 1, '30S': 0.5, 'H': 60, 'S': 1 / 60.}
        # Case 1
        df0 = df[df['diff int'] == sd[self.w]]
        df0 = df0.resample(self.w).last()
        # Case 2
        df1 = df[df['diff int'] > sd[self.w]]
        df1 = df1.resample(self.w).last()
        # Limit interpolation based on sampling frequency
        if self.w == '1Min':
            inter_lim = 16
        elif self.w == '1S':
            inter_lim = 60
        else:
            inter_lim = 1
        # Case 2
        if df1.empty == False:
            df1.fillna(method='backfill', limit=inter_lim, inplace=True)
        df1['scaled count'] = df1['count'] / df1['diff int']
        # Case 3
        df2 = df[df['diff int'] < sd[self.w]]
        df2 = df2.resample(self.w).sum()
        del df['count']
        df = df.resample(self.w).last()
        df['df0'] = df0['count']
        df['df1'] = df1['scaled count']
        df['df2'] = df2['count']
        self.data = df.df1.add(df.df2, fill_value=0).add(
            df.df0, fill_value=0)
        # Drop duplicates from index
        self.data = self.data.groupby(self.data.index).first()
        self.data.name = self.meas_des

    def interpolate_state(self):
        """Interpolate binary values from state loggers by resampling
           and filling forward, minimum resolution of sampling frequency
           """
        self.data = self.data.resample(self.w).last()
        self.data.fillna(method='ffill', inplace=True)
        # Drop duplicates from index
        self.data = self.data.groupby(self.data.index).first()

    def interpolate_linear(self):
        """Linear interpolation with built in limits

           :param str x: Not a param
           """
        try:
            self.data = self.data.resample(self.w).last()
        except:
            # This resample throws an ambiguous time error when near Fall DST,
            # issue apperas to be closed on github (#8744) but I'm still
            # having to resolve with tz_convert to UTC
            self.data = self.data.tz_convert('UTC').resample(
                self.w).last()
        if self.w == '1Min':
            inter_lim = 61
        elif self.w == '1S':
            inter_lim = 60
        else:
            inter_lim = 1
        self.data.interpolate(inplace=True,
                              limit=inter_lim, limit_direction='both')
        # Drop duplicates from index
        self.data = self.data.groupby(self.data.index).first()

    def interpolate(self):
        """Method to decide which type of interpolation to perform based on
           measurement quantity
           """
        if self.data.empty:
            print 'No data to interpolate'
        else:
            if self.quant == 'Counts':
                self.interpolate_count()
            elif (('State' in self.quant) or ('Light' in self.quant) or
                  (self.quant in self.state_logger_labels)):
                self.interpolate_state()
            else:
                self.interpolate_linear()


class HOBOWareMeasurement(Measurement):
    """Measurement subclass, specific to data exported from HOBOWare
       """

    def __init__(self, data, name, w):
        Measurement.__init__(self, data, name, w)

    def scale_mV(self):
        """If a logger wasn't configured properly, the output from HOBOWare
           may contain dimensions of mV instead of A when measuring current,
           the data can be 'scaled' by dividing by 333.0
           """
        if 'mV' in self.data.name.split(',')[0]:
            self.data = self.data / 333.0
            self.data.name = self.data.name.replace('mV', 'Current')

    def scale_Voltage_RMS(self):
        """Same issue as in scale_mV method can occur as
           'Voltage RMS,' corrected in same way
           """
        if 'Voltage RMS, A' in self.data.name.split('(')[0]:
            self.data.name = self.data.name.replace('Voltage RMS', 'Current')
        elif 'Voltage RMS, mV' in self.data.name.split('(')[0]:
            self.data = self.data / 333.0
            self.data.name = self.data.name.replace('Voltage RMS', 'Current')

    def get_lable(self):
        """When launching a logger with HOBOWare, an optional label field is
           provided to describe what is being measured, this method parses that
           input if present
           """
        if 'LBL' in self.data.name:
            self.label = self.data.name.split('LBL:')[1].split(')')[0].strip()

    def get_quant(self):
        """Parse the quantity measured from column label, if the logger was
           measuring state (on/off) then HOBOWare allows this value to be
           manually changed by the individual launching the logger, in these
           cases, the manually entered labels must be combiled into a list so
           the correct for of interpolation is applied, this list is inputted
           using the kwarg 'state_logger_labels'
           """
        self.state_logger_labels.append('Hawkeye')
        self.state_logger_labels.append('Light')
        if (self.data.name.split('(')[0].split(',')[0].rstrip() in
           self.state_logger_labels):
            self.quant = 'State'
            self.label = (self.label + ', ' +
                          self.data.name.split('(')[0].split(',')[0].rstrip())
        else:
            self.quant = self.data.name.split('(')[0].split(',')[0].rstrip()

    def get_dim(self):
        """Parse dimensions of quantity measured from column label
           """
        if ('State' in self.quant):
            self.dim = 'On/Off'
        else:
            try:
                self.dim = unicode(
                    self.data.name.split('(')[0].split(',')[1].strip(),
                    errors='replace')
            except IndexError:
                print ("Couldn't parse measurement dimensions: " +
                       self.data.name)
                self.dim = 'could not parse'

    # TODO: Figure out how name attribute is used by other functions
    def get_name(self):
        """
           """
        self.name = (self.name + '_' +
                     self.data.name.split('LGR S/N: ')[1].split(',')[0] + '_' +
                     self.data.name.split('SEN S/N: ')[1].split(',')[0].split(
                         ')')[0])

    def get_meas_des(self):
        """Unique identifier for a specific measurement, allows for
           measurements to be merged across multiply files
           """
        self.meas_des = self.name + ' ' + self.quant
        self.data.name = self.meas_des + ' ' + self.label

    @staticmethod
    def make(data, name, w, **kwargs):
        """Static way of calling all routine methods and returning instance
           """
        m = HOBOWareMeasurement(data, name, w)
        if 'state_logger_labels' in kwargs:
            m.state_logger_labels = kwargs['state_logger_labels']
        m.scale_mV()
        m.scale_Voltage_RMS()
        m.get_lable()
        m.get_quant()
        m.get_dim()
        m.get_name()
        m.get_meas_des()
        m.interpolate()
        return m


class HOBOLinkMeasurement(Measurement):
    """Measurement subclass, specific to data exported from HOBOLink
       """

    def __init__(self, data, name, w):
        Measurement.__init__(self, data, name, w)

    def scale_mV(self):
        """If a logger wasn't configured properly, the output from HOBOLink
           may contain dimensions of mV instead of A when measuring current,
           the data can be 'scaled' by dividing by 333.0
           """
        if 'mV' in self.data.name.split('(')[0]:
            self.data = self.data / 333.0
            self.data.name = self.data.name.replace('mV', 'Current')

    def scale_Voltage_RMS(self):
        """Same issue as in scale_mV method can occur as
           'Voltage RMS,' corrected in same way
           """
        if (('Voltage RMS' in self.data.name.split('(')[0]) and
           ('mV' in self.data.name.split(',')[1])):
            self.data = self.data / 333.0
            self.data.name = self.data.name.replace('Voltage RMS', 'Current')

    def get_label(self):
        """When launching a logger with HOBOLink, an optional label field is
           provided to describe what is being measured, this method parses that
           input if present
           """
        self.label = self.data.name.split(',')[-1].strip()

    def get_quant(self):
        """Parse the quantity measured from column label
           """
        self.quant = self.data.name.split('(')[0].strip()
        if self.quant == 'A':
            self.quant = 'Current'

    def get_dim(self):
        """Parse dimensions of quantity measured from column label
           """
        self.dim = self.data.name.split(',')[1].strip()

    def get_name(self):
        """
           """
        self.name = (self.name + '_' +
                     self.data.name.split(':')[0].split(' ')[-1] + '_' +
                     self.data.name.split(':')[1].split(')')[0])
        # TODO: Using Cool Smart convention for now, need to reevaluate
        if self.quant != 'Current':
            self.name = self.name.split('-')[0]
        else:
            self.name = self.name.replace('-', 'x')

    def get_meas_des(self):
        """Unique identifier for a specific measurement, allows for
           measurements to be merged across multiply files
           """
        self.meas_des = self.name + ' ' + self.quant
        self.data.name = self.meas_des + ' ' + self.label

    @staticmethod
    def make(data, name, w):
        """Static way of calling all routine methods and returning instance
           """
        m = HOBOLinkMeasurement(data, name, w)
        m.scale_mV()
        m.scale_Voltage_RMS()
        m.get_label()
        m.get_quant()
        m.get_dim()
        m.get_name()
        m.get_meas_des()
        m.interpolate()
        return m


class SmartThingsMeasurement(Measurement):
    """Measurement subclass, specific to data exported from SmartThings

       May need to rename ThinkSpeak, not sure yet, also need to pull in API
       from James, Chase, and Alex, this class only works with data manually
       pulled from the website
       """

    def __init__(self, data, name, w):
        Measurement.__init__(self, data, name, w)

    def scale_power(self):
        """Convert W to kW
           """
        self.data = self.data / 1000.0  # W to kW

    def get_quant(self):
        """Set measurement quantity
           """
        self.quant = 'Power'

    def get_dim(self):
        """Set measurement dimensions
           """
        self.dim = 'kW'

    def get_label(self):
        """
           """
        self.label = ' '.join(self.name.split(' ')[1:]).split('(')[0].strip()

    def get_name(self):
        """
           """
        self.name = self.name.split(' ')[0]

    def get_meas_des(self):
        """Unique identifier for a specific measurement, allows for
           measurements to be merged across multiply files
           """
        self.meas_des = self.name + ' ' + self.label + ' ' + self.quant
        self.data.name = self.meas_des

    @staticmethod
    def make(data, name, w):
        """Static way of calling all routine methods and returning instance
           """
        m = SmartThingsMeasurement(data, name, w)
        m.scale_power()
        m.get_quant()
        m.get_dim()
        m.get_label()
        m.get_name()
        m.get_meas_des()
        m.interpolate()
        return m


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
        """
           """
        file_ext = self.path.split('.')[1].lower()
        if file_ext == 'xlsx':
            self.data = pd.read_excel(self.path)
        elif file_ext == 'csv':
            self.data = pd.read_csv(self.path)

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
        self.name = (self.path.split('\\')[-1].split('.')[0] +
                     '_LCD')

    def read_data(self):
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

    def __init__(self, path):
        Export.__init__(self)
        self.meas = TMYMeasurement
        self.path = path

    def read_data(self):
        self.data = pd.read_hdf(self.path)

    def get_name(self):
        self.name = (self.path.split('\\')[-1].split('.')[0] +
                     '_TMY')

    def get_tz(self):
        self.tz = -5

    def pre_clean_data(self):
        keep = ['Date (MM/DD/YYYY)', 'Time (HH:MM)', 'Dry-bulb (C)',
                'RHum (%)', 'Wspd (m/s)']
        for column_name in self.data.columns:
            if column_name not in keep:
                del self.data[column_name]
        self.data['Time (HH:MM)'][
            self.data['Time (HH:MM)'] == '24:00'] = '00:00'

    def set_index(self):
        pass

    def post_clean_data(self):
        self.data = self.data.apply(pd.to_numeric)

    @staticmethod
    def make(path, w):
        e = TMYExport(path)
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
