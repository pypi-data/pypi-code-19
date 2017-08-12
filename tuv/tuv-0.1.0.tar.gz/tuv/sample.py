import os
import datetime

import pkg_resources

from . import translator

class DB(translator.Translator):
    '''
    A TUV translator based on a sample file
    '''
    def _read_TUV_header(self):

        with open( self.output_sample_file, 'r' ) as f:
            # First line contains: "Photolysis rate coefficients, s-1"
            _ = f.readline()

            # Photolysis reaction: "<column number> = <reaction>" -> read until no
            # <column number is found>:
            TUV_head = ['time']; idx='0'
            while idx.isdigit():
                # Remove blanks and split at first occurence of '=':
                line = f.readline().replace(' ','')
                idx, xTUV_head = line.split('=',1)
                TUV_head.append( xTUV_head.strip() )

        # With the while-loop above one line too much is read ...
        return TUV_head[:-1]

    def _read_TUV_output(self):

        from numpy import genfromtxt, delete

        # Read column names:
        TUV_head = self._read_TUV_header( )
        # The header includes one line for each photolysis reaction (=len(TUV_head)) plus the
        # line with "Photolysis rate coefficients, s-1", the line "values at z = <zout> km",
        # and the line "Columns: time, sza, photo-reactions" (-> 3):
        header_lines = len( TUV_head ) + 3

        # Load from file (last line: "--------------" -> skip_footer=1):
        TUV_data = genfromtxt( self.output_sample_file, dtype=float, skip_header=header_lines, skip_footer=1 )

        # Delete column "sza":
        TUV_data = delete( TUV_data, 1, axis=1 )

        # Create a dictionary:
        # { <photolysis reaction> : <time series of coefficients in s^-1 }
        TUV_data = { x:TUV_data[:,i] for i,x in enumerate(TUV_head)}

        return TUV_data

    def get_default_settings(self):
        '''
        Get the default settings for the TUV DB
        '''
        # stub
        db_default_settings = \
                {# dimension:      FRAPPE variable:  default values:   Units of FRAPPE variables:
                       'date'  :  ['JDAY'          ,             213] , # day of year
                       'time'  :  ['LOCAL_SUN_TIME',            12.0] , # hours since midnight
                     'height'  :  ['GPS_ALT'       ,             5.5] , # in km above sea surface
                      'o3col'  :  ['O3COLUMN'      ,           300.0] , # in DU
                        'lat'  :  ['LATITUDE'      ,            40.0]   # in degrees
                }

        return db_default_settings


    def get_phot_rates( self, time_requested, lat=40.0, height=1.7, o3col=300.0 ):
        '''
        Get photolysis rates for a given time
        '''
        # lat, height, o3col unused in this stub version

        from numpy import linspace, zeros, interp, floor, ceil

        TUV_head = self._read_TUV_header( )

        # Time in hours and fractions:
        time_hours = time_requested.hour + time_requested.minute/60.0 + time_requested.second/3600.0

        # Dictionary: { <photolysis reaction> : <hourly time series of photolysis rates in s^-1> }
        TUV_data_dc = self._read_TUV_output( )

        tuv_times = TUV_data_dc['time']
        # which time array index corresponds to the time requested?
        i_exact = interp(time_hours, tuv_times, range(len(tuv_times)))
        i_hi = int(min( [ ceil(i_exact), len(tuv_times) ] ))
        i_lo = int(max( [ floor(i_exact), 0 ] ))

        # Dictionary: { <photolysis reaction> : <photolysis rate in s^-1> }
        TUV_data = { key : ( TUV_data_dc[key][i_lo] * (1.0 - (i_exact - i_lo)) + TUV_data_dc[key][i_hi] * (i_exact - i_lo) ) for key in TUV_data_dc.keys() }

        return TUV_data, TUV_data_dc

    def __init__(self, output_sample_file = None, translator_file = None):
        self.output_sample_file = output_sample_file
        data_dir                 = pkg_resources.resource_filename(__name__, 'data')

        if output_sample_file is None:
            self.output_sample_file  = os.path.join(data_dir, 'TUV_output_sample.txt')

        super(DB, self).__init__(translator_file=translator_file)
