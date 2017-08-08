#
# hdg-from -- Generate HDG files for GEMSS
#
# Copyright (C) 2017 Di WU
# All rights reserved.
#
# This software may be modified and distributed under the terms
# of the MIT license.  See the LICENSE file for details.
#

# Compatibility with Pyhton 2.7
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import str, open, super, int, range
__metaclass__ = type

from datetime import datetime, timedelta

from hdgfrom.flow import Flow, Observation, Rate


class FileFormats:
    SWMM = "SWMM"
    HDG = "HDG"

    _ALL_FORMATS = [ SWMM,
                     HDG ]

    ERROR_UNKNOWN_FORMAT = "Unknown file format '{name}'."

    @staticmethod
    def match(name):
        for any_format in FileFormats._ALL_FORMATS:
            if name.upper() == any_format:
                return any_format

        error = FileFormats.ERROR_UNKNOWN_FORMAT.format(name=name)
        raise ValueError(error)


class Processor:

    def __init__(self, file_format):
        self._file_format = file_format

    def accepts(self, file_format):
        return self._file_format == file_format


class Reader(Processor):
    """
    Read a flow from a specific file format
    """

    def __init__(self, format):
        super().__init__(format)

    def read_from(self, input_stream):
        pass


class SWMMReader(Reader):
    """
    Reader from a SWMM text file
    """

    def __init__(self):
        super().__init__(FileFormats.SWMM)

    def read_from(self, input_stream):
        water_body = self._read_water_body_from(input_stream)
        observations = self._read_observations_from(input_stream)
        return Flow(water_body.strip(), observations)

    @staticmethod
    def _read_water_body_from(input_stream):
        line = ""
        while not line.strip():
            line = input_stream.readline()
        _, water_body = line.split("-")
        return water_body

    @staticmethod
    def _read_observations_from(input_stream):
        observations = []
        SWMMReader._skip_lines(input_stream, 2)
        line = input_stream.readline()
        while line.strip() != "":
            (day, time, rate) = line.strip().split("\t")
            (hour, minute, second) = time.strip().split(":")
            timestamp = timedelta(
                days=int(day),
                hours=int(hour),
                minutes=int(minute),
                seconds=int(second))
            observations.append(Observation(Rate(float(rate.strip())), timestamp))
            line = input_stream.readline()
        return observations

    @staticmethod
    def _skip_lines(input_stream, count=1):
        for i in range(count):
            input_stream.readline()


class Writer(Processor):

    def __init__(self, format):
        super().__init__(format)

    def write_to(self, flow, output_stream):
        pass

    @staticmethod
    def now():
        return datetime.now()


class HDGWriter(Writer):

    DATE_FORMAT = "%d/%m/%Y %H:%M"

    HDG_HEADER = ("$GLLVHTTVDFile, V5.0\n"
                  "$Creation Date: {creation_date}\n"
                  "$Waterbody Name: {water_body}\n"
                  "$Created by: {user_name}\n"
                  "$Start Date: {start_date}\n"
                  "$End Date: {end_date}\n"
                  "$Number of Data Lines: {observation_count}\n"
                  "$X, Y, Station Height, Missing value,Profile Format, ExceFormat, Longitude, Latitude, Anemometer Height\n"
                  "$Number of bins, Depth data type, TVD file type\n"
                  "62000,6957300,0,999999999,0,0,0,0,0\n"
                  "1,0,0\n"
                  "1\n"
                  "2,0,0,1.0,0,0.0,0.0,Flow Rate,Flow Rate\n"
                  "$Year,Month,Day,Hour,Minute,Bin1,Flow Rate\n")

    def __init__(self):
        super().__init__(FileFormats.HDG)

    def write_to(self, flow, output_stream):
        header = self.HDG_HEADER.format(
            creation_date=self.now().strftime(self.DATE_FORMAT),
            water_body=flow.water_body,
            user_name=flow.user_name,
            start_date=flow.start_date.strftime(self.DATE_FORMAT),
            end_date=flow.end_date.strftime(self.DATE_FORMAT),
            observation_count=len(flow.observations)
        )
        output_stream.write(header)
        for each_observation in flow.observations:
            date = flow.start_date + each_observation.time
            line = "%d,%d,%d,%d,%d,%d,%.2f\n" % (date.year,
                                                 date.month,
                                                 date.day,
                                                 date.hour,
                                                 date.minute,
                                                 date.second,
                                                 each_observation.rate.value)
            output_stream.write(line)

class AdapterLibrary:
    """
    Select the proper reader (resp. writer), depending on the given format
    and delegates the reading (resp. pretty-prining).
    """

    ERROR_NO_READER = "Reading {format} files are not yet supported"
    ERROR_NO_WRITING = "Writing {format} files are not yet supported"

    DEFAULT_READERS = [ SWMMReader() ]
    DEFAULT_WRITERS = [ HDGWriter() ]

    def __init__(self, readers=None, writers=None):
        self._readers = readers or self.DEFAULT_READERS
        self._writers = writers or self.DEFAULT_WRITERS

    def read_from(self, file_format, input_stream):
        reader = self._find_reader_for(file_format)
        return reader.read_from(input_stream)

    def _find_reader_for(self, file_format):
        for any_reader in self._readers:
            if any_reader.accepts(file_format):
                return any_reader

        error = self.ERROR_NO_READER.format(format=file_format)
        raise RuntimeError(error)

    def write_to(self, flow, file_format, output_stream):
        writer = self._find_writer_for(file_format)
        writer.write_to(flow, output_stream)

    def _find_writer_for(self, file_format):
        for any_writer in self._writers:
            if any_writer.accepts(file_format):
                return any_writer

        error = self.ERROR_NO_WRITER.format(format=file_format)
        raise RuntimeError(error)
