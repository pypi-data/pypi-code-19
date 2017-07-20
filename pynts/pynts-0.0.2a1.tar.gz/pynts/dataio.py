"""
BSD 3-Clause License

Copyright (c) 2017, Gilberto Pastorello
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

pynts.dataio: data input/output functions for timeseries data

@author: Gilberto Pastorello
@contact: gzpastorello@lbl.gov
@date: 2017-07-17
"""
import os
import logging
import numpy

from datetime import datetime
from pynts import PyntsError

_log = logging.getLogger(__name__)


def get_headers(filename, headerline=1):
    """
    Parse headers format and returns
    list of strings with header labels.
    Must have at least two columns, one with timestamps.
    
    :param filename: name of the file to be loaded
    :type filename: str
    :param headerline: line number for column headers (starting from 1)
    :type headerline: int
    """
    with open(filename, 'r') as f:
        lnum = 0
        while lnum < headerline:
            line = f.readline()
            lnum += 1
    headers = line.strip().split(',')
    if len(headers) < 2:
        raise PyntsError("Headers too short: '{h}'".format(h=line))
    headers = [i.strip() for i in headers]
    _log.debug("Got headers: {h}".format(h=headers))
    return headers


STRTEST_STANDARD = ['TIMESTAMP', 'TIMESTAMP_START', 'TIMESTAMP_END']
def get_dtype(variable, strtest=STRTEST_STANDARD):
    """
    Returns data type based on variable label (case insensitive).
    Timestamp variables are str, and all others 64bit/8byte floats
    
    :param variable: variable label
    :type variable: str
    :param strtest: list of strings containing timestamps (str data tyope will be used)
    :type: list
    """
    for s in strtest:
        if s.lower() in variable.lower():
            return 'a25'
    return 'f8'


def get_fill_value(dtype):
    """
    Returns string fill value based on data type.
    
    :param dtype: data type for variable
    :type dtype: str
    """
    if dtype == 'a25':
        return ''
    elif dtype == 'i8':
        return -9999
    else:
        return numpy.NaN


def get_timestamp_format_from_resolution(sample):
    """
    Returns strptime/strftime compatible format based on sample ISO timestamp
    (length-base, strips blanks)
    
    :param sample: sample ISO timestamp
    :type sample: str
    """
    s = sample.strip()
    # year only
    if len(s) == 4:
        tformat = "%Y"

    # year, month
    elif len(s) == 6:
        tformat = "%Y%m"

    # year, day of year
    elif len(s) == 7:
        tformat = "%Y%j"

    # year, month, day
    elif len(s) == 8:
        tformat = "%Y%m%d"

    # year, month, day, hour
    elif len(s) == 10:
        tformat = "%Y%m%d%H"

    # year, month, day, hour, minute
    elif len(s) == 12:
        tformat = "%Y%m%d%H%M"

    # year, month, day, hour, minute, second
    elif len(s) == 14:
        tformat = "%Y%m%d%H%M%S"

    # unknown
    else:
        raise PyntsError("Unknown time format '{f}'".format(f=sample))

    # raises error if doesn't match sample
    _ = datetime.strptime(s, tformat)

    return tformat


MISSING_VALUES_STANDARD = 'nan,NAN,NaN,-9999,-9999.0,-6999,-6999.0, '
def load_csv(filename, delimiter=',', headerline=1, first_dataline=2, timestamp_labels=STRTEST_STANDARD[0:1], missing=MISSING_VALUES_STANDARD):
    """
    Loads timeseries data from column oriented CSV file
    with at least one timestamp column
    
    :param filename: name of file to be written (fails if doesn't exists)
    :type filename: str
    :param delimiter: cell delimiter character (e.g., ',' or '\t')
    :type delimiter: str
    :param headerline: line number for column headers (starting from 1)
    :type headerline: int
    :param first_dataline: line number for first data record  (starting from 1)
    :type first_dataline: int
    :param timestamp_labels: list of timestamp column labels in file (will only use first)
    :type timestamp_labels: list
    :param missing: comma-separated string with all entries that should be treated as missing
    :param type: str
    """

    _log.debug("Started loading: {f}".format(f=filename))
    headers = get_headers(filename=filename)
    dtype = [(h, get_dtype(h, strtest=timestamp_labels)) for h in headers]
    fill_values = [get_fill_value(dtype=d[1]) for d in dtype]
    data = numpy.genfromtxt(fname=filename, dtype=dtype, names=True, delimiter=",", skip_header=first_dataline - 2, missing_values=missing, usemask=True)
    data = numpy.atleast_1d(data)
    data = numpy.ma.filled(data, fill_values)

    timestamp_label = timestamp_labels[0]
    tformat = get_timestamp_format_from_resolution(data[timestamp_label][0])
    timestamp = [datetime.strptime(i, tformat) for i in data[timestamp_label]]

    _log.debug("Finished loading: {f}".format(f=filename))
    return data, timestamp


def save_csv(filename, data, delimiter=',', newline='\n', header=None):
    """
    Saves data array into csv file.
    Saves missing values as -9999
    
    :param filename: name of file to be written (overwrites if exists)
    :type filename: str
    :param data: data array
    :type data: numpy.ndarray
    :param delimiter: cell delimiter character (e.g., ',' or '\t')
    :type delimiter: str
    :param newline: new line character
    :type newline: str
    :param header: header to be written before data (array labels used if none)
    :type header: str
    """
    _log.debug("Started saving: {f}".format(f=filename))
    if header is None:
        header = delimiter.join(data.dtype.names)

    with open(filename, 'w') as f:
        f.write(header + newline)
        for i, row in enumerate(data):
            if i % 1000 == 0:
                _log.debug("Writing {f}: line {l}".format(f=filename, l=i))
            line = delimiter.join("-9999" if (value == -9999.0 or value == -9999.9)  else str(value) for value in row)
            f.write(line + newline)
    _log.debug("Finished saving: {f}".format(f=filename))


if __name__ == '__main__':
    raise PyntsError('Not executable')
