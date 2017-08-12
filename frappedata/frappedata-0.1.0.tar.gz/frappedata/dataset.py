import os
import warnings
import pickle
import datetime
import math

import pkg_resources
import numpy as np

import icartt

class Dataset(object):
    '''
    Generic dataset object as parent to both ExtractsDataset and MergesDataset objects
    '''
    def __read_used_file(self, fname):
        config_path = pkg_resources.resource_filename(__name__, 'data')
        species_file = os.path.join(config_path, fname)

        with open(species_file, 'rb') as f:
            species = f.readlines()

        species = [ x.replace("\n","").replace("\r","") for x in species ]

        return species

    @property
    def species_used(self):
        '''
        List chemical observations in dataset that have been determined useful for genBOX processing
        '''
        return self.__read_used_file('species_used.csv')

    @property
    def photrates_used(self):
        '''
        List photolysis rate measurements in dataset that have been determined useful for genBOX processing
        '''
        return self.__read_used_file('photrates_used.csv')

    def get_units(self, vars):
        '''
        Return units of one or several dataset variables (<vars>)
        '''
        if (isinstance(vars, str)):
            vars = [ vars ]

        units = [ self.ict.units(x) for x in vars ]

        if len(units) == 1:
            units = units[0]

        return units

class ExtractsDataset(Dataset):
    @property
    def dataset_used(self):
        return 'expert-selected excerpts from FRAPPE C130 measurement data.'

    @property
    def tags(self):
        '''
        Returns list of tags ('extracts') that are available
        '''
        onlyfiles = [f for f in os.listdir(self.extracts_data_path) if os.path.isfile(os.path.join(self.extracts_data_path, f))]
        onlycsvs  = [f.replace(".csv", "") for f in onlyfiles if '.csv' in f ]

        return onlycsvs

    def __get_header (self, tag):

        tag_file = os.path.join(self.extracts_data_path, tag + '.csv')

        with open( tag_file, 'r' ) as f:
            header = f.readline().replace('\n','').split(',')

        return header

    def valid(self, tag):
        '''
        Is a given tag found in the dataset?
        '''
        tag_file = os.path.join(self.extracts_data_path, tag + '.csv')
        return os.path.isfile(tag_file)

    def get_timestamp(self, **kwargs):
        '''
        Returns average time stamp (datetime.datetime) for the tag
        '''
        jday            = self.get_var('JDAY', avg=True, **kwargs)
        # for averaged data
        jday            = math.floor(jday)

        local_sun_time  = self.get_local_sun_time(**kwargs)

        new_years_day   = self.ict.dateValid.replace(day=1, month=1, hour=0, minute=0, second=0)

        return new_years_day + datetime.timedelta(days=jday-1, hours=local_sun_time)

    def get_data (self, tag, avg=False, **kwargs):
        '''
        Return all data for a given tag, potentially time-averaged (avg=True)
        '''
        tag_file = os.path.join(self.extracts_data_path, tag + '.csv')

        with open( tag_file, 'r' ) as f:
            data = f.readlines()

        for idata,xdata in enumerate(data):
                # Every line contains whitespaces and returns...
            xdata       = xdata.replace(' ','').replace('\n', '')
            # Columns are separated by ","...
            xdata = xdata.split(',')

            if idata > 0:
                for errval in self.ulod_flags:
                    xdata = [ val.replace(errval, 'NaN') for val in xdata ]
                for errval in self.llod_flags:
                    xdata = [ val.replace(errval, '0.0') for val in xdata ]
                for errval in self.miss_flags:
                    xdata = [ val.replace(errval, 'NaN') for val in xdata ]

                xdata = [float(item) for item in xdata]

            data[idata] = xdata

        out = {}
        for i, spec in enumerate(data[0]):
            values = [ row[i] for row in data ][1:]
            if avg:
                # complains if all values are nan...
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    values = float(np.nanmean(values))
            out[spec] = values

        return out

    def get_var(self, varname, tag, avg=True, **kwargs):
        '''
        Return data for a given variable in a given tag, potentially time averaged (avg=True)
        '''
        data = self.get_data(tag, avg=avg)

        var = data[varname]

        return var

    # simplified access to special variables
    def get_temperature(self, tag, avg=True, **kwargs):
        return self.get_var('TEMPERATURE', tag, avg=avg)

    def get_local_sun_time(self, tag, avg=True, **kwargs):
        return self.get_var('LOCAL_SUN_TIME', tag, avg=avg)

    def __init__(self):
        self.extracts_data_path = pkg_resources.resource_filename(__name__,
                                os.path.join('data','extracts'))

        self.merge_file = os.path.join(self.extracts_data_path, 'stub.ict')
        self.ict = icartt.Dataset(self.merge_file, loadData=False)
        self.name = 'FRAPPE'

        #ULOD_FLAG: -777777 (1min merge) / -7777777 (TOGA merge)
        self.ulod_flags   = [ '-777777', '-7777777' ]
        #LLOD_FLAG: -888888 (1min merge) / -8888888 (TOGA merge)
        self.llod_flags   = [ '-888888', '-8888888' ]
        # missing data: -999999 (1min merge) / -9999999 (TOGA merge)
        self.miss_flags   = [ '-999999', '-9999999' ]

class MergesDataset(Dataset):
    @property
    def dataset_used(self):
        return os.path.basename(self.merge_file)

    def __get_var_indices(self, vars):
        if (isinstance(vars, str)):
            vars = [ vars ]

        idx = []
        for var in vars:
            idx += [ self.ict.index(var) ]

        if len(idx) == 1:
            idx = idx[0]

        return idx

    def __get_data_by_index(self, i):
        return [ row[i] for row in self._data ][1:]

    def __get_data_by_name(self, var):
        return self.__get_data_by_index(self.__get_var_indices(var))

    def __make_timemask(self, starttime=None, endtime=None, **kwargs):
        if starttime is None:
            starttime = min(self.times)
        if endtime is None:
            endtime = max(self.times)
        return [ s >= starttime and s <= endtime for s in self.times ]

    def get_timestamp(self, starttime=None, endtime=None, **kwargs):
        '''
        Returns average time stamp (datetime.datetime) for the selected time frame
        or the whole dataset if no time frame is given
        '''
        timemask = self.__make_timemask(starttime=starttime, endtime=endtime)
        masked_times = [ self.times[i] for i in range(0, len(self.times)) if timemask[i] ]
        masked_times.sort()

        idx = int(len(masked_times)/2)
        return masked_times[idx]

    def valid(self, starttime, endtime, **kwargs):
        '''
        Checks whether at least one data line falls within the time frame
        '''
        timemask = self.__make_timemask(starttime=starttime, endtime=endtime)
        masked_times = [ self.times[i] for i in range(0, len(self.times)) if timemask[i] ]
        masked_times.sort()
        return len(masked_times) > 0

    def get_var(self, spec, starttime=None, endtime=None, avg=True, **kwargs):
        '''
        Return data for a given variable (for a given time frame), potentially time averaged (avg=True)
        '''
        values = self.get_data(starttime=starttime, endtime=endtime, avg=avg, specs=[ spec ])
        return values

    # simplified access to special variables
    def get_temperature(self, starttime=None, endtime=None, avg=True, **kwargs):
        return self.get_var('TEMPERATURE', starttime=starttime, endtime=endtime, avg=avg)
    def get_local_sun_time(self, starttime=None, endtime=None, avg=True, **kwargs):
        return self.get_var('LOCAL_SUN_TIME', starttime=starttime, endtime=endtime, avg=avg)


    def get_data(self, starttime=None, endtime=None, specs=None, avg=False, **kwargs):
        '''
        Return all data (for a given time frame), potentially time-averaged (avg=True)
        '''
        timemask = self.__make_timemask(starttime=starttime, endtime=endtime)

        if specs is None:
            specs = self.ict.varnames

        out = {}
        for spec in specs:
            values = self.__get_data_by_name(spec)
            values = [ values[i] for i in range(0, len(values)) if timemask[i] ]
            if avg:
                # complains if all values are nan...
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    values = float(np.nanmean(values))
            out[spec] = values

        if len(specs) == 1:
            out = out[specs[0]]

        return out

    def __init__(self, merge_file):
        '''
        :param str merge_file: Absolute path to the FRAPPE merge file
        '''
        self.merge_file = merge_file
        self.ict = icartt.Dataset(self.merge_file, loadData=False)
        self.name = 'FRAPPE'

        cache_file = self.merge_file + ".cached"
        if os.path.isfile(cache_file):
            if os.path.getmtime(self.merge_file) > os.path.getmtime(cache_file):
                os.remove(cache_file)
        if not os.path.isfile(cache_file):
            print('Caching merge file...')
            self.ict.read()
            data = np.array(self.ict.data)
            with open(cache_file, 'wb') as f:
                pickle.dump( data , f)

        dmp = pickle.load(open(cache_file, 'rb'))

        self._data  = dmp

        #ULOD_FLAG: -777777 (1min merge) / -7777777 (TOGA merge)
        self.ulod_flags   = [ -777777.0, -7777777,0 ]
        #LLOD_FLAG: -888888 (1min merge) / -8888888 (TOGA merge)
        self.llod_flags   = [ -888888.0, -8888888.0 ]
        # missing data: -999999 (1min merge) / -9999999 (TOGA merge)
        self.miss_flags   = [ -999999.0, -9999999.0 ]

        for errval in self.ulod_flags:
            self._data[ np.where( self._data == errval) ] = np.nan
        for errval in self.llod_flags:
            self._data[ np.where( self._data == errval) ] = 0.0
        for errval in self.miss_flags:
            self._data[ np.where( self._data == errval) ] = np.nan

        new_years_day   = self.ict.dateValid.replace(day=1, month=1, hour=0, minute=0, second=0)
        jday = self.__get_data_by_name('JDAY')
        utc  = self.__get_data_by_name('UTC')
        self.times = [ new_years_day + datetime.timedelta(days=d-1, seconds = s) for s, d in zip(utc, jday) ]

