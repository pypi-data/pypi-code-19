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

pynts.util: data utility functions for timeseries data

@author: Gilberto Pastorello
@contact: gzpastorello@lbl.gov
@date: 2017-07-19
"""
import os
import logging
import numpy

from datetime import datetime, date, time, timedelta
from pynts import PyntsError
from pynts.dataio import STRTEST_STANDARD

_log = logging.getLogger(__name__)


def extract_columns(data, columns, timestamps=STRTEST_STANDARD):
    """
    Returns array with requested columns
    (always includes at least one timestamp column)
    
    :param data: data array to be extracted from
    :type data: numpy.ndarray
    :param columns: list of column labels to be extracted
    :type columns: list
    :param timestamps: list of timestamp column labels to be preserved if present
    :type timestamps: list
    """
    in_headers = list(data.dtype.names)
    temp_headers = [t for t in timestamps if t in in_headers]

    if len(temp_headers) == 0:
        for label in in_headers:
            dt = str(data.dtype.fields[label][0])
            if dt == '|S25':
                temp_headers.append(label)
                _log.warning("Couldn't find timestamps '{t}' in data, using '{h}' instead".format(t=timestamps, h=label))
                break

    if len(temp_headers) == 0:
        raise PyntsError("Could not find timestamp column in {h}".format(h=in_headers))

    out_headers = [t for t in temp_headers if t not in columns] + columns

    _log.debug("Extracting columns: {c}".format(c=out_headers))

    return data[out_headers]


def extract_interval(data, timestamp_list, first_datetime=None, last_datetime=None):
    """
    Returns array with records within first and last datetimes
    (inclusive interval for first, exclusive interval for last) 
    
    :param data: data array to be extracted from
    :type data: numpy.ndarray
    :param timestamp_list: list of datetime objects corresponding to data array
    :type timestamp_list: list
    :param first_datetime: earliest timestamp to be included
    :type first_datetime: datetime
    :param last_datetime: earliest timestamp to be excluded
    :type last_datetime: datetime
    """

    if first_datetime is None:
        first_datetime = timestamp_list[0]

    if first_datetime > timestamp_list[-1]:
        # return empty array
        _log.debug("First timestamp '{f}' is later than last available timestamp '{l}'".format(f=first_datetime, l=timestamp_list[-1]))
        return data[-1:0]

    if last_datetime is None:
        last_datetime = timestamp_list[-1]

    if last_datetime <= timestamp_list[0]:
        # return empty array
        _log.debug("Last timestamp '{l}' is earlier than (or equal to) first available timestamp '{f}'".format(l=last_datetime, f=timestamp_list[0]))
        return data[-1:0]

    # search forwards for timestamp
    # TODO: maybe binary search-like implementation can speed-up process
    current = 0
    while timestamp_list[current] < first_datetime:
        current += 1
    first_idx = current

    # search backwards for timestamp
    # TODO: maybe binary search-like implementation can speed-up process
    current = -1
    while timestamp_list[current] >= last_datetime:
        current -= 1
    last_idx = current

    _log.debug("Extracting interval: [{fi}] {ft} -- [{li}] {lt}".format(fi=first_idx, ft=timestamp_list[first_idx], li=last_idx, lt=timestamp_list[last_idx]))

    return data[first_idx:last_idx]



if __name__ == '__main__':
    raise PyntsError('Not executable')
