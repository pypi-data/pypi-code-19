# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import ctypes
import warnings
import platform
import datetime
import sys
import io
import os
import csv
import json
import atexit
import signal

try:
    import flask
    from flask import request
except ImportError:
    pass
try:
    import pyspark
    from pyspark.sql import DataFrame
except ImportError:
    pass
try:
    import pandas as pd
except ImportError:
    pass
try:
    import numpy as np
except ImportError:
    pass

class ModelDataCollector(object):
    if platform.system() == "Windows":
        dllpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools', 'modeldatacollector', 'lib', 'native', 'Windows')
        os.environ['PATH'] = dllpath + ';' + os.environ['PATH']
        _lib = ctypes.CDLL('modeldatacollector.dll', use_last_error=True)
    else:
        trackR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools', 'modeldatacollector', 'lib', 'native', 'Linux', 'libtrackR.so')
        libmodeldatacollector = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools', 'modeldatacollector', 'lib', 'native', 'Linux', 'libmodeldatacollector.so')
        ctypes.CDLL(trackR, use_last_error=True)
        _lib = ctypes.CDLL(libmodeldatacollector, use_last_error=True)

    def __init__(self, model_name, identifier='default', model_version='unknown', feature_names=None):
        """
        Instantiates a new ModelDataCollector.

        When storage collection is enabled, data will be sent to the following container path:
        /modeldata/{model_name}/{model_version}/{identifier}/{year}/{month}/{day}/data.csv

        Args:
            model_name(str). the name of the model
            identifier(str). a unique identifier for this data collection location, i.e. 'RawInput'
            model_version(str). the version of the model. Will get extracted from model config file if present.
            feature_names(list). a list of feature names that become the csv header when supplied
        """
        if 'flask' in sys.modules:
            self._aml_operationalization = True
        else:
            self._aml_operationalization = False

        self._cloud_enabled = ModelDataCollector._lib.IsDataCollectionEnabled()
        self._debug = False
        self._handle = -1
        if os.environ.get('AML_MODEL_DC_DEBUG') and os.environ.get('AML_MODEL_DC_DEBUG').lower() == 'true':
            self._debug = True
            self._feature_names = feature_names
            print("Data collection is in debug mode. Set environment variable AML_MODEL_DC_STORAGE_ENABLED to 'true' to send data to the cloud (http://aka.ms/amlmodeldatacollection).")
        elif not self._cloud_enabled:
            print("Data collection is not enabled. Set environment variable AML_MODEL_DC_STORAGE_ENABLED to 'true' to enable (http://aka.ms/amlmodeldatacollection).")
            return

        if os.path.isfile("/var/azureml-app/model_config_map.json"):
            with open("/var/azureml-app/model_config_map.json") as config_map_json:
                model_config_map = json.load(config_map_json)
            if model_name in model_config_map:
                model_version = model_config_map[model_name]['version']

        if self._cloud_enabled:
            # Initialize TrackR and save handle
            if sys.version_info[0] < 3:
                self._handle = ModelDataCollector._lib.Init(model_name, str(model_version), identifier)
            else:
                self._handle = ModelDataCollector._lib.InitW(model_name, str(model_version), identifier)

            if self._handle == -1:
                warnings.warn('initialize failed: environment variable AML_MODEL_DC_STORAGE must be set to an Azure storage connection string (http://aka.ms/amlmodeldatacollection).')
                return

            if feature_names:
                header_csv_data_buffer = self._convert_feature_names_to_csv_header(feature_names)
                ModelDataCollector._lib.WriteHeader(self._handle, header_csv_data_buffer, len(header_csv_data_buffer))

        signal.signal(signal.SIGTERM, self._sigterm_handler)


    @atexit.register
    def _shutdown():
        ModelDataCollector._lib.ShutdownAll()

    def _sigterm_handler(self, signum, frame):
        print("Model data collection shutting down: SIGTERM called")
        ModelDataCollector._lib.ShutdownAll()
        sys.exit(0)

    def collect(self, input_data, user_correlation_id=""):
        """
        Collect data for this ModelDataCollector instance.
        Args:
            input_data(list, numpy.array, pandas.DataFrame, pyspark.sql.DataFrame). the data to be collected
            user_correlation_id(str). an optional correlation id provided by the user
        """
        if (not self._cloud_enabled or self._handle == -1) and not self._debug:
            return

        if isinstance(input_data, list):
            csv_data_buffer = self._convert_list_to_csv(input_data, user_correlation_id)
            csv_header_buffer = None
        elif ('numpy' in sys.modules and 'pandas' in sys.modules) and isinstance(input_data, np.ndarray):
            csv_data_buffer = self._convert_numpy_to_csv(input_data, user_correlation_id)
            csv_header_buffer = None
        elif 'pandas' in sys.modules and isinstance(input_data, pd.DataFrame):
            csv_header_buffer, csv_data_buffer = self._convert_pandas_df_to_csv(input_data, user_correlation_id)
            if self._cloud_enabled:
                ModelDataCollector._lib.WriteHeader(self._handle, csv_header_buffer, len(csv_header_buffer))
        elif ('pyspark' in sys.modules and 'pandas' in sys.modules) and isinstance(input_data, DataFrame):
            csv_header_buffer, csv_data_buffer = self._convert_spark_df_to_csv(input_data, user_correlation_id)
            if self._cloud_enabled:
                ModelDataCollector._lib.WriteHeader(self._handle, csv_header_buffer, len(csv_header_buffer))
        else:
            warnings.warn('collect failed: input data must be list, numpy array, pandas dataframe, or spark dataframe. Corresponding modules must be installed first.')
            return None

        if self._cloud_enabled:
            self._handle = ModelDataCollector._lib.WriteBinary(self._handle, csv_data_buffer, len(csv_data_buffer))
        if self._debug:
            self._write_to_stdout(csv_header_buffer, csv_data_buffer)
            
    def _convert_feature_names_to_csv_header(self, feature_names):
        standard_headers = ['$Timestamp', '$CorrelationId', '$RequestId']
        header_csv_data = self._convert_list_to_csv_buffer(standard_headers + feature_names)
        return header_csv_data

    def _get_generated_data_fields(self):
        timestamp = datetime.datetime.utcnow().isoformat()
        if self._aml_operationalization and flask.has_request_context():
            if 'REQUEST_ID' in request.environ:
                return {'timestamp': timestamp, 'request_id': request.environ['REQUEST_ID']}
        
        # Not running in AML context with flask/request id
        return {'timestamp': timestamp, 'request_id': '00000000-0000-0000-0000-000000000000'}

    def _write_to_stdout(self, header_buffer, data_buffer):
        if not header_buffer:
            if self._feature_names:
                header_buffer = self._convert_feature_names_to_csv_header(self._feature_names)

        if header_buffer:
            print(header_buffer.decode() + data_buffer.decode())
        else:
            print(data_buffer.decode())

    def _convert_list_to_csv(self, input_list, user_correlation_id):
        generated_data_fields = self._get_generated_data_fields()
        additional_fields_list = [generated_data_fields['timestamp'], user_correlation_id, generated_data_fields['request_id']]
        buffer_object = self._convert_list_to_csv_buffer(additional_fields_list + input_list)
        return buffer_object

    def _convert_numpy_to_csv(self, numpy_data, user_correlation_id):
        if numpy_data.ndim == 1:
            # Transposing so that data is a single row not single column
            numpy_data = [numpy_data]

        # Numpy datastructures are strongly typed which makes adding additional columns
        # a pain. Instead, converting numpy to pandas allows us to do this easily and reuse code
        pandas_df = pd.DataFrame(data=numpy_data)

        # Header buffer is ignored here because users store headers in numpy arrays
        # inconsistantly (dtype, 1st row). Instead use the ModelDataCollector constructor
        # and feature_names list to explictly pass these in for numpy.
        _, data_buffer = self._convert_pandas_df_to_csv(pandas_df, user_correlation_id)
        return data_buffer

    def _convert_pandas_df_to_csv(self, pandas_df, user_correlation_id):
        generated_data_fields = self._get_generated_data_fields()
        pandas_df.insert(0, '$Timestamp', generated_data_fields['timestamp'])
        pandas_df.insert(1, '$CorrelationId', user_correlation_id)
        pandas_df.insert(2, '$RequestId', generated_data_fields['request_id'])
        header_buffer, data_buffer = self._convert_pandas_df_to_csv_buffers(pandas_df)
        return header_buffer, data_buffer

    def _convert_spark_df_to_csv(self, spark_df, user_correlation_id):
        # Use pandas conversion
        pandas_df = spark_df.toPandas()
        header_buffer, data_buffer = self._convert_pandas_df_to_csv(pandas_df, user_correlation_id)
        return header_buffer, data_buffer

    def _convert_list_to_csv_buffer(self, input_list):
        # csvwriter in python 2 and 3 requires a different type of buffer due to string encoding differences
        if sys.version_info[0] < 3:
            buf = io.BytesIO()
            csvwriter = csv.writer(buf)
            csvwriter.writerow(input_list)
        else:
            stringbuf = io.StringIO()
            csvwriter = csv.writer(stringbuf)
            csvwriter.writerow(input_list)
            buf = io.BytesIO(stringbuf.getvalue().encode())
        
        return buf.getvalue()

    def _convert_pandas_df_to_csv_buffers(self, pandas_df):
        # Puts the header names into a buffer
        header_buf = self._convert_list_to_csv_buffer(list(pandas_df))
        if sys.version_info[0] < 3:
            buf = io.BytesIO()
            pandas_df.to_csv(buf, index=False, header=False)
            return header_buf, buf.getvalue()
        else:
            stringbuf = io.StringIO()
            pandas_df.to_csv(stringbuf, index=False, header=False)
            buf = io.BytesIO(stringbuf.getvalue().encode())
            return header_buf, buf.getvalue()