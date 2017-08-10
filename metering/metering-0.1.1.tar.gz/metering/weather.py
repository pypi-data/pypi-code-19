# -*- coding: utf-8 -*-
import GeoFunctions as geo
import DataFunctions as data
import urllib
import sys
import pandas as pd
import numpy as np
reload(data)
reload(geo)

"""
NOAA's API changed and the LCD API is under development and requires manual
download
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


def download_tmy_weather_data(usaf_id, dst_path):
    """Download TMY3 weather data from NREL and save csv file

       :param str usaf_id: US Airforce weather station identifier
       :param str dst_path: Path do directory to write downloaded csv file
       """
    src_path = (
        'http://rredc.nrel.gov/solar/old_data/nsrdb/1991-2005/data/tmy3/' +
        usaf_id + 'TYA.csv')
    file_name = usaf_id + '.csv'
    dst_path = dst_path + '\\' + file_name
    urllib.urlretrieve(src_path, dst_path)
