"""
The monitoring module contains the PerformanceMonitoring class used to run
quality control tests and store results.
"""
import pandas as pd
import numpy as np
import re
import logging

none_list = ['','none','None','NONE', None, [], {}]

logger = logging.getLogger(__name__)

class PerformanceMonitoring(object):

    def __init__(self):
        """
        PerformanceMonitoring class
        """
        self.df = pd.DataFrame()
        self.trans = {}
        self.tfilter = pd.Series()
        self.test_results = pd.DataFrame(columns=['System Name', 'Variable Name',
                                                'Start Date', 'End Date',
                                                'Timesteps', 'Error Flag'])

    def add_dataframe(self, df, system_name, add_identity_translation_dictionary=False):
        """
        Add DataFrame to the PerformanceMonitoring object.

        Parameters
        -----------
        df : pd.Dataframe
            Dataframe to add to the PerformanceMonitoring object

        system_name : string
            System name

        add_identity_translation_dictionary : boolean (optional)
            Add a 1:1 translation dictionary to the PerformanceMonitoring object
            using all column names in df, default = False
        """
        temp = df.copy()

        # Combine variable name with system name (System: Variable)
        temp.columns = [system_name + ':' + s  for s in temp.columns]

        if self.df is not None:
            self.df = self.df.combine_first(temp)
        else:
            self.df = temp.copy()

        # define identity translation
        if add_identity_translation_dictionary:
            trans = {}
            for col in df.columns:
                trans[col] = [col]

            self.add_translation_dictionary(trans, system_name)

    def add_translation_dictionary(self, trans, system_name):
        """
        Add translation dictionary to the PerformanceMonitoring object.

        Parameters
        -----------
        trans : dictionary
            Translation dictionary

        system_name : string
            System name
        """
        # Combine variable name with system name (System: Variable)
        for key, values in trans.items():
            self.trans[key] = []
            for value in values:
                self.trans[key].append(system_name + ':' + value)

    def add_time_filter(self, time_filter):
        """
        Add a time filter to the PerformanceMonitoring object.

        Parameters
        ----------
        time_filter : pd.DataFrame with a single column or pd.Series
            Time filter containing boolean values for each time index
        """
        if isinstance(time_filter, pd.DataFrame):
            self.tfilter = pd.Series(data = time_filter.values[:,0], index = self.df.index)
        else:
            self.tfilter = time_filter

    def add_signal(self, col_name, data):
        """
        Add signal to the PerformanceMonitoring DataFrame.

        Parameters
        -----------
        col_name : string
            Column name to add to translation dictionary

        data : pd.DataFarame or pd.Series
            Data to add to df
        """
        if type(data) is pd.core.series.Series:
            data = data.to_frame(col_name)
        if type(data) is not pd.core.frame.DataFrame:
            logger.warning("Add signal failed")
            return

        if col_name in self.trans.keys():
            logger.info(col_name + ' already exists in trans')
            return
        for col in data.columns.values.tolist():
            if col in self.df.columns.values.tolist():
                logger.info(col + ' already exists in df')
                return
        try:
            self.trans[col_name] = data.columns.values.tolist()
            #self.df[df.columns] = df
            for col in data.columns:
                self.df[col] = data[col]
        except:
            logger.warning("Add signal failed: " + col_name)
            return

    def append_test_results(self, mask, error_msg, min_failures=1, use_mask_only=False): 
        """
        Append QC results to the PerformanceMonitoring object.

        Parameters
        ----------
        mask : pd.Dataframe
            Result from quality control test, boolean values

        error_msg : string
            Error message to store with the QC results

        min_failures : int (optional)
            Minimum number of consecutive failures required for reporting, default = 1

        use_mask_only : boolean  (optional)
            When True, the mask is used directly to determine test 
            results and the system/variable name is not included in the test_results.
            When False, the mask is used in combination with pm.df
            to extract test results. Default = False
        """
        if use_mask_only:
            sub_df = mask 
        else:
            sub_df = self.df[mask.columns]

        # Find blocks
        order = 'col'
        if order == 'col':
            mask = mask.T

        np_mask = mask.values

        start_nans_mask = np.hstack((np.resize(np_mask[:,0],(mask.shape[0],1)),
                                     np.logical_and(np.logical_not(np_mask[:,:-1]), np_mask[:,1:])
                                     ))
        stop_nans_mask = np.hstack((np.logical_and(np_mask[:,:-1], np.logical_not(np_mask[:,1:])),
                                    np.resize(np_mask[:,-1], (mask.shape[0],1))
                                    ))

        start_row_idx,start_col_idx = np.where(start_nans_mask)
        stop_row_idx,stop_col_idx = np.where(stop_nans_mask)

        if order == 'col':
            temp = start_row_idx; start_row_idx = start_col_idx; start_col_idx = temp
            temp = stop_row_idx; stop_row_idx = stop_col_idx; stop_col_idx = temp
            #mask = mask.T

        block = {'Start Row': list(start_row_idx),
                 'Start Col': list(start_col_idx),
                 'Stop Row': list(stop_row_idx),
                 'Stop Col': list(stop_col_idx)}

        #if sub_df is None:
        #    sub_df = self.df

        for i in range(len(block['Start Col'])):
            length = block['Stop Row'][i] - block['Start Row'][i] + 1
            if length >= min_failures:
                if use_mask_only:
                    var_name = ''
                    system_name = ''
                else:
                    var_name = sub_df.iloc[:,block['Start Col'][i]].name #sub_df.icol(block['Start Col'][i]).name
                    system_name = ''
                    temp = var_name.split(':')
                    if len(temp) == 2:
                        var_name = temp[1]
                        system_name = temp[0]
                    
                frame = pd.DataFrame([system_name, var_name,
                                      sub_df.index[block['Start Row'][i]],
                                      sub_df.index[block['Stop Row'][i]],
                                      length, error_msg],
                                      index=['System Name', 'Variable Name', 'Start Date', 'End Date', 'Timesteps', 'Error Flag'])
                frame_t = frame.transpose()
                self.test_results = self.test_results.append(frame_t, ignore_index=True)

    def check_timestamp(self, frequency, expected_start_time=None,
                        expected_end_time=None, min_failures=1,
                        exact_times=True):
        """
        Check time series for missing, non-monotonic and duplicate
        timestamps.

        Parameters
        ----------
        frequency : int
            Expected time series frequency, in seconds

        expected_start_time : Timestamp (optional)
            Expected start time. If not specified, the minimum timestamp
            is used

        expected_end_time : Timestamp (optional)
            Expected end time. If not specified, the maximum timestamp
            is used

        min_failures : int (optional)
            Minimum number of consecutive failures required for
            reporting, default = 1

        exact_times : bool (optional)
            Controls how missing times are checked. 
            If True, times are expected to occur at regular intervals 
            (specified in frequency) and the dataframe is reindexed to match the 
            expected frequency.
            If False, times only need to occur once or more within each interval 
            (specified in frequency) and the dataframe is not reindexed.
        """
        logger.info("Check timestamp")

        if self.df.empty:
            logger.info("Empty database")
            return
        if expected_start_time is None:
            expected_start_time = min(self.df.index)
        if expected_end_time is None:
            expected_end_time = max(self.df.index)

        rng = pd.date_range(start=expected_start_time, end=expected_end_time,
                            freq=str(frequency) + 's')

        # Check to see if timestamp is monotonic
#        mask = pd.TimeSeries(self.df.index).diff() < 0
        mask = pd.Series(self.df.index).diff() < pd.Timedelta('0 days 00:00:00')
        mask.index = self.df.index
        mask[mask.index[0]] = False
        mask = pd.DataFrame(mask)
        mask.columns = [0]

        self.append_test_results(mask, 'Nonmonotonic timestamp',
                                 use_mask_only=True,
                                 min_failures=min_failures)

        # If not monotonic, sort df by timestamp
        if not self.df.index.is_monotonic:
            self.df = self.df.sort_index()

        # Check for duplicate timestamps
#        mask = pd.TimeSeries(self.df.index).diff() == 0
        mask = pd.Series(self.df.index).diff() == pd.Timedelta('0 days 00:00:00')
        mask.index = self.df.index
        mask[mask.index[0]] = False
        mask = pd.DataFrame(mask)
        mask.columns = [0]
        mask['TEMP'] = mask.index # remove duplicates in the mask
        mask.drop_duplicates(subset='TEMP', keep='last', inplace=True)
        del mask['TEMP']

        # Drop duplicate timestamps (this has to be done before the
        # results are appended)
        self.df['TEMP'] = self.df.index
        #self.df.drop_duplicates(subset='TEMP', take_last=False, inplace=True)
        self.df.drop_duplicates(subset='TEMP', keep='first', inplace=True)

        self.append_test_results(mask, 'Duplicate timestamp',
                                 use_mask_only=True,
                                 min_failures=min_failures)
        del self.df['TEMP']
        
        if exact_times:
            temp = pd.Index(rng)
            missing = temp.difference(self.df.index).tolist()
            # reindex dataframe
            self.df = self.df.reindex(index=rng)
            mask = pd.DataFrame(data=self.df.shape[0]*[False],
                                index=self.df.index)
            mask.loc[missing] = True
            self.append_test_results(mask, 'Missing timestamp',
                                 use_mask_only=True,
                                 min_failures=min_failures)
        else:
            # uses pandas >= 0.18 resample syntax
            df_index = pd.DataFrame(index=self.df.index)
            df_index[0]=1 # populate with placeholder values
            mask = df_index.resample('{}s'.format(frequency)).count() == 0
            self.append_test_results(mask, 'Missing timestamp',
                                 use_mask_only=True,
                                 min_failures=min_failures)
        
    def check_range(self, bound, key=None, specs={}, rolling_mean=0, min_failures=1):
        """
        Check bounds on data.

        Parameters
        ----------
        bound : list of floats
            [lower bound, upper bound], None can be used in place of a lower or upper bound

        key : string (optional)
            Translation dictionary key.  If not specified, all columns are used in the test.

        specs : dictionary (optional)
            Constants used in bound

        rolling_mean : int (optional)
            Size of the moving window (in seconds) used to smooth data using a
            rolling mean before the test is run, default = 0 (i.e., not used)

        min_failures : int (optional)
            Minimum number of consecutive failures required for reporting, default = 1
        """
        logger.info("Check data range")

        if self.df.empty:
            logger.info("Empty database")
            return

        tfilter = self.tfilter

        # Isolate subset if key is not None
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Range: " + key)
                return
        else:
            df = self.df

        # Compute moving average
        if rolling_mean > 0:
            rolling_mean_str = str(rolling_mean) + 's' 
            df = df.rolling(rolling_mean_str).mean()

        # Evaluate strings for bound values
        for i in range(len(bound)):
            if bound[i] in none_list:
                bound[i] = None
            elif type(bound[i]) is str:
                bound[i] = self.evaluate_string('', bound[i], specs)

        # Lower Bound
        if bound[0] is not None:
            mask = (df < bound[0])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                self.append_test_results(mask, 'Data < lower bound, '+str(bound[0]), min_failures=min_failures) 

        # Upper Bound
        if bound[1] is not None:
            mask = (df > bound[1])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                self.append_test_results(mask, 'Data > upper bound, '+str(bound[1]), min_failures=min_failures)

    def check_increment(self, bound, key=None, specs={}, increment=1, 
                        absolute_value=True, rolling_mean=0, min_failures=1):
        """
        Check bounds on the difference between data values separated by a set increment.

        Parameters
        ----------
        bound : list of floats
            [lower bound, upper bound], None can be used in place of a lower or upper bound

        key : string (optional)
            Translation dictionary key. If not specified, all columns are used in the test.

        specs : dictionary (optional)
            Constants used in bound

        increment : int (optional)
            Time step shift used to compute difference, default = 1

        absolute_value : boolean (optional)
            Take the absolute value of the increment data, default = True

        rolling_mean : int (optional)
            Size of the moving window (in seconds) used to smooth data using a
            rolling mean before the test is run, default = 0 (i.e., not used)

        min_failures : int (optional)
            Minimum number of consecutive failures required for reporting, default = 1
        """
        logger.info("Check increment range")

        if self.df.empty:
            logger.info("Empty database")
            return

        tfilter = self.tfilter

        # Isolate subset if key is not None
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Increment: " + key)
                return
        else:
            df = self.df

        # Compute moving average
        if rolling_mean > 0:
            rolling_mean_str = str(rolling_mean) + 's' 
            df = df.rolling(rolling_mean_str).mean()

        # Compute interval
        if absolute_value:
            df = np.abs(df.diff(periods=increment))
        else:
            df = df.diff(periods=increment)

        # Evaluate strings for bound values
        for i in range(len(bound)):
            if bound[i] in none_list:
                bound[i] = None
            elif type(bound[i]) is str:
                bound[i] = self.evaluate_string('', bound[i], specs)
        
        if absolute_value:
            error_flag_prefix = '|Increment|'
        else:
            error_flag_prefix = 'Increment'
            
        # Lower Bound
        if bound[0] is not None:
            mask = (df < bound[0])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                self.append_test_results(mask, error_flag_prefix+' < lower bound, '+str(bound[0]), min_failures=min_failures) 

        # Upper Bound
        if bound[1] is not None:
            mask = (df > bound[1])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                self.append_test_results(mask, error_flag_prefix+' > upper bound, '+str(bound[1]), min_failures=min_failures) 

    def check_delta(self, bound, key=None, specs={}, window=3600, 
                    absolute_value=True, rolling_mean=0, min_failures=1):
        """
        Check bounds on the difference between max and min data values within 
		 a rolling window (Note, this method is currently NOT efficient for large 
        data sets (> 100000 pts) because it uses df.rolling().apply() to find 
        the position of the min and max).

        Parameters
        ----------
        bound : list of floats
            [lower bound, upper bound], None can be used in place of a lower 
            or upper bound

        key : string (optional)
            Translation dictionary key. If not specified, all columns are used 
            in the test.

        specs : dictionary (optional)
            Constants used in bound

        window : int (optional)
            Size of the moving window (in seconds) used to compute delta, 
            default = 3600

        absolute_value : boolean (optional)
            Take the absolute value of delta, default = True

        rolling_mean : int (optional)
            Size of the moving window (in seconds) used to smooth data using a
            rolling mean before the test is run, default = 0 (i.e., not used)

        min_failures : int (optional)
            Minimum number of consecutive failures required for reporting, 
            default = 1
        """
        logger.info("Check delta (max-min) range")

        if self.df.empty:
            logger.info("Empty database")
            return

        tfilter = self.tfilter

        # Isolate subset if key is not None
        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Increment: " + key)
                return
        else:
            df = self.df

        # Compute moving average
        if rolling_mean > 0:
            rolling_mean_str = str(rolling_mean) + 's' 
            df = df.rolling(rolling_mean_str).mean()
        
        window_str = str(window) + 's' 

        # Extract the max/min position in each window
        argmax_df = df.rolling(window_str).apply(np.nanargmax) 
        argmin_df = df.rolling(window_str).apply(np.nanargmin) 
        # Replace nan with 0
        argmax_df[argmax_df.isnull()] = 0 
        argmin_df[argmin_df.isnull()] = 0               
        # Shift the position to account for the moving window
        rng = pd.date_range(df.index[0], periods=2, freq=window_str)
        nshift = (df.index < rng[1]).sum()
        index_shift = pd.Series(np.append(np.zeros(nshift-1), np.arange(len(df)-(nshift-1))), index=df.index)
        argmax_df = argmax_df.add(index_shift, axis=0)
        argmin_df = argmin_df.add(index_shift, axis=0)
         # Convert to int
        argmax_df = argmax_df.astype(int)
        argmin_df = argmin_df.astype(int)
        
        # Extract the max/min time in each window
        tmax_df = pd.DataFrame(argmax_df.index[argmax_df], 
                               columns=argmax_df.columns, index=argmax_df.index)
        tmin_df = pd.DataFrame(argmin_df.index[argmin_df], 
                               columns=argmin_df.columns, index=argmin_df.index)
        
        # Compute max difference in each window
        diff_df = df.rolling(window_str).max() - df.rolling(window_str).min() # ignores nan
        diff_df.iloc[0:nshift-1,:] = np.nan # reset values without full window to nan
        if not absolute_value:
            reverse_order = tmax_df < tmin_df 
            diff_df[reverse_order] = -diff_df[reverse_order]
            
        def extract_exact_position(mask1, tmin_df, tmax_df):
            mask2 = pd.DataFrame(False, columns=mask1.columns, index=mask1.index)
            # Loop over t, col in mask1 where condition is True
            for t,col in list(mask1[mask1 > 0].stack().index): 
                # set the initially flaged location to False
                mask2.loc[t,col] = False 
                # extract the start and end time
                start_time = tmin_df.loc[t,col]
                end_time = tmax_df.loc[t,col]
                # update mask2
                if start_time < end_time:
                    mask2.loc[start_time:end_time,col] = True # set the time between max and min to true
                else:
                    mask2.loc[end_time:start_time,col] = True # set the time between max and min to true
            return mask2
        
        # Evaluate strings for bound values
        for i in range(len(bound)):
            if bound[i] in none_list:
                bound[i] = None
            elif type(bound[i]) is str:
                bound[i] = self.evaluate_string('', bound[i], specs)
        
        if absolute_value:
            error_flag_prefix = '|Delta|'
        else:
            error_flag_prefix = 'Delta'
        
        # Lower Bound
        if bound[0] is not None:
            mask = (diff_df < bound[0])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                mask = extract_exact_position(mask, tmin_df, tmax_df)
                self.append_test_results(mask, error_flag_prefix+' < lower bound, '+str(bound[0]), 
                                         min_failures=min_failures) 

        # Upper Bound
        if bound[1] is not None:
            mask = (diff_df > bound[1])
            if not tfilter.empty:
                mask[~tfilter] = False
            if mask.sum(axis=1).sum(axis=0) > 0:
                mask = extract_exact_position(mask, tmin_df, tmax_df)
                self.append_test_results(mask, error_flag_prefix+' > upper bound, '+str(bound[1]), 
                                         min_failures=min_failures) 

    def check_missing(self, key=None, min_failures=1):
        """
        Check for missing data

        Parameters
        ----------
        key : string (optional)
            Translation dictionary key. If not specified, all columns are used in the test.

        min_failures : int (optional)
            Minimum number of consecutive failures required for reporting, default = 1
        """
        logger.info("Check for missing data")

        if self.df.empty:
            logger.info("Empty database")
            return

        tfilter = self.tfilter

        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Missing: " + key)
                return
        else:
            df = self.df

        mask = pd.isnull(df) # checks for np.nan, np.inf

        missing_timestamps = self.test_results[self.test_results['Error Flag'] == 'Missing timestamp']
        for index, row in missing_timestamps.iterrows():
            mask.loc[row['Start Date']:row['End Date']] = False

        if not tfilter.empty:
            mask[~tfilter] = False

        if mask.sum(axis=1).sum(axis=0) > 0:
            self.append_test_results(mask, 'Missing data', min_failures=min_failures)

    def check_corrupt(self, corrupt_values, key=None, min_failures=1):
        """
        Check for corrupt data.

        Parameters
        ----------
        corrupt_values : list of floats
            List of corrupt data values

        key : string (optional)
            Translation dictionary key. If not specified, all columns are used in the test.

        min_failures : int (optional)
            Minimum number of consecutive failures required for reporting, default = 1
        """
        logger.info("Check for corrupt data")

        if self.df.empty:
            logger.info("Empty database")
            return

        tfilter = self.tfilter

        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Insufficient data for Check Corrupt: " + key)
                return
        else:
            df = self.df

        mask = pd.DataFrame(data = np.zeros(df.shape), index = df.index, columns = df.columns, dtype = bool) # all False
        for i in corrupt_values:
            mask = mask | (df == i)

        if not tfilter.empty:
            mask[~tfilter] = False

        if mask.sum(axis=1).sum(axis=0) > 0:
            self.df[mask] = np.nan
            self.append_test_results(mask, 'Corrupt data', min_failures=min_failures)

    def evaluate_string(self, col_name, string_to_eval, specs={}):
        """
        Returns the evaluated Python equation written as a string (BETA).
        For each {keyword} in string_to_eval,
        {keyword} is first expanded to self.df[self.trans[keyword]],
        if that fails, then {keyword} is expanded to specs[keyword].

        Parameters
        ----------
        col_name : string
            Column name for the new signal

        string_to_eval : string
            String to evaluate

        specs : dictionary (optional)
            Constants used as keywords

        Returns
        --------
        signal : pd.DataFrame or pd.Series
            DataFrame or Series with results of the evaluated string
        """

        match = re.findall(r"\{(.*?)\}", string_to_eval)
        for m in set(match):
            m = m.replace('[','') # check for list

            if m == 'ELAPSED_TIME':
                ELAPSED_TIME = self.get_elapsed_time()
                string_to_eval = string_to_eval.replace("{"+m+"}",m)
            elif m == 'CLOCK_TIME':
                CLOCK_TIME = self.get_clock_time()
                string_to_eval = string_to_eval.replace("{"+m+"}",m)
            else:
                try:
                    self.df[self.trans[m]]
                    datastr = "self.df[self.trans['" + m + "']]"
                    string_to_eval = string_to_eval.replace("{"+m+"}",datastr)
                except:
                    try:
                        specs[m]
                        datastr = "specs['" + m + "']"
                        string_to_eval = string_to_eval.replace("{"+m+"}",datastr)
                    except:
                        pass

        try:
            signal = eval(string_to_eval)
            if type(signal) is tuple:
                col_name = [col_name + " " + str(i+1)  for i in range(len(signal))]
                signal = pd.concat(signal, axis=1)
                signal.columns = [col_name]
                signal.index = self.df.index
            elif type(signal) is float:
                signal = signal
            else:
                signal = pd.DataFrame(signal)
                if len(signal.columns) == 1:
                    signal.columns = [col_name]
                else:
                    signal.columns = [col_name + " " + str(i+1)  for i in range(signal.shape[1])]
                signal.index = self.df.index
        except:
            signal = None
            logger.warning("Insufficient data for Composite Signals: " + col_name + ' -- ' + string_to_eval)

        return signal

    def get_elapsed_time(self):
        """
        Returns the elapsed time in seconds for each Timestamp in the DataFrame index.

        Returns
        --------
        elapsed_time : pd.DataFrame
            Elapsed time of the DataFrame index
        """
        elapsed_time = ((self.df.index - self.df.index[0]).values)/1000000000 # convert ns to s
        elapsed_time = pd.DataFrame(data=elapsed_time, index=self.df.index, dtype=int)

        return elapsed_time

    def get_clock_time(self):
        """
        Returns the time of day in seconds past midnight for each Timestamp in the DataFrame index.

        Returns
        --------
        clock_time : pd.DataFrame
            Clock time of the DataFrame index
        """

        secofday = self.df.index.hour*3600 + \
                   self.df.index.minute*60 + \
                   self.df.index.second + \
                   self.df.index.microsecond/1000000.0
        clock_time = pd.DataFrame(secofday, index=self.df.index)

        return clock_time

    def get_test_results_mask(self, key=None):
        """
        Return a mask of data-times that failed a quality control test.

        Parameters
        -----------
        key : string (optional)
            Translation dictionary key. If not specified, all columns are used

        Returns
        --------
        test_results_mask : pd.DataFrame
            DataFrame containing boolean values for each data point, True =
            data point pass all tests, False = data point did not pass at least one test.
        """
        if self.df.empty:
            logger.info("Empty database")
            return

        if key is not None:
            try:
                df = self.df[self.trans[key]]
            except:
                logger.warning("Key not in DataFrame")
                return
        else:
            df = self.df

        test_results_mask = ~pd.isnull(df)
        for i in self.test_results.index:
            system = self.test_results.loc[i, 'System Name']
            variable = self.test_results.loc[i, 'Variable Name']
            start_date = self.test_results.loc[i, 'Start Date']
            end_date = self.test_results.loc[i, 'End Date']
            error_flag = self.test_results.loc[i, 'Error Flag']
            if error_flag in ['Nonmonotonic timestamp', 'Duplicate timestamp']:
                continue
            if variable == '': # occurs when data is missing
                test_results_mask.loc[start_date:end_date] = False
            else:
                if system == '': # occurs when data is a composite signal
                    column_name = variable
                else:
                    column_name = system + ':'+ variable
                test_results_mask.loc[start_date:end_date,column_name] = False

        return test_results_mask
