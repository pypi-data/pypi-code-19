# -*- coding: utf-8 -*-
import GeoFunctions as geo
import DataFunctions as data
import os
import sys
import pandas as pd
import numpy as np
import pytz
reload(data)
reload(geo)

"""
Since NOAA's API changed and the LCD API is under development, this module will
be re-implemented with LCD and TMY export classes in expors.py
"""


def get_stations(geo_name):
    """Locate nearest weather station designated as  TMY3, AWOS, ASOS, or METAR

       :param str geo_name: Geographic description of location (e.g. zip code,
                            town/city and state, etc.)
       :return: Matched station USAF and WBAN ids
       :rtype: tuple str
       """
    input_dir = str()
    for s in sys.path:
        if s.split('\\')[-1] == 'site-packages':
            input_dir = s + '\\metering\\data\\weather\\input'
    stations_file = input_dir + '\\stations.csv'
    options_file = input_dir + '\\options.csv'
    all_stations = geo.import_station_df(stations_file)
    x = np.nan
    addresses = pd.DataFrame(data=[['loc', x, x, x, x, x, x, geo_name, x,
                                    x, '2016-01-01', '2016-01-31',
                                    'hourly', x]],
                             columns=['Site ID', 'Unformatted Address',
                                      'Street Address', 'City', 'State',
                                      'ZIP', 'ZIP+4', 'Lookup Address',
                                      'Lat', 'Lon', 'Start Date', 'End Date',
                                      'Data Period', 'Preferred Station WBAN'])
    addresses['Start Date'] = pd.to_datetime(
        addresses['Start Date']).dt.tz_localize('US/Eastern')
    addresses['End Date'] = pd.to_datetime(
        addresses['End Date']).dt.tz_localize('US/Eastern')
    options = pd.read_csv(
        options_file, dtype={'Station Type': str, 'Include': bool})
    options.index = options['Station Type']
    del options['Station Type']
    options = options.iloc[0:6]['Include'].to_dict()
    # Initialize the geocoder
    geocoder = geo.initiate_geolocator()
    # Geocode the addresses and match to nearest station
    coded_addresses = geo.geocode_addresses(addresses, geocoder)
    match_stations = geo.get_eligible_stations(all_stations, options)
    coded_addresses = geo.find_stations(coded_addresses, match_stations)
    return (coded_addresses['TMY3 USAF ID'].iloc[0],
            coded_addresses['Matched WBAN'].iloc[0])


def get_normal_weather(usaf, start_date, end_date, w):
    """
       """
    usaf_ids = usaf
    usaf_ids = usaf_ids + 'TY.csv'
    tmy_path = r'\\cadmusgroup.org\energy\weather$\TMY3\station files'
    for station_id in os.listdir(tmy_path):
        if station_id == usaf_ids:
            df = pd.read_csv(tmy_path + '\\' + station_id,
                             low_memory=False,
                             header=1)
            # TODO: haven't finished, not sure what frames are doing
            # return df
            # TODO: Need to return df here, add TMYExport class to preform
            #       the rest of this processing
            for column_id in df.columns:
                keep = ['Date (MM/DD/YYYY)', 'Time (HH:MM)',
                        'Dry-bulb (C)', 'RHum (%)', 'Wspd (m/s)']
                if column_id not in keep:
                    del df[column_id]
            # TODO: replace with pd.DataFrame.set_value()
            df['Time (HH:MM)'][
                df['Time (HH:MM)'] == '24:00'] = '00:00'
            frames = list()
            start_year = int(start_date.split('/')[2])
            end_year = int(end_date.split('/')[2])
            for i in np.arange(start_year, end_year + 1, 1):
                temp_df = df.copy()
                temp_df['Date (MM/DD/YYYY)'] = temp_df[
                    'Date (MM/DD/YYYY)'].str[0:6] + str(i)
                frames.append(temp_df)
            df = pd.concat(frames)
            df.index = df['Date (MM/DD/YYYY)'] + ' ' + df[
                'Time (HH:MM)']
            del df['Date (MM/DD/YYYY)'], df['Time (HH:MM)']
            df.index = pd.to_datetime(
                df.index, format='%m/%d/%Y %H:%M')
            df.index = df.index.tz_localize(
                pytz.FixedOffset(-5 * 60)).tz_convert('UTC')
            df = df.astype(float)
            df = df.resample(w).mean()
            if (w == '1Min') or (w == 'T'):
                inter_lim = 61
            elif w == 'H':
                inter_lim = 2
            df.interpolate(inplace=True,
                           limit=inter_lim, limit_direction='both')
            df = df.ix[start_date:end_date]
            df['Dry-bulb (C)'] = df['Dry-bulb (C)'] * 9 / 5. + 32.
            df['Wspd (m/s)'] = df['Wspd (m/s)'] * 2.237
            df.columns = ['Tdb [deg F]', 'RH [%]', 'Wind Speed [mi/h]']
            norm_t = df['Tdb [deg F]']
            norm_rh = df['RH [%]']
            norm_ws = df['Wind Speed [mi/h]']
            return norm_t, norm_rh, norm_ws
