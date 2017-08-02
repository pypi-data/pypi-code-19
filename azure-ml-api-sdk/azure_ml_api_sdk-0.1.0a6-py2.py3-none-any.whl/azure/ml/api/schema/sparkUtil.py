# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
"""
Utilities to save and load schema information for Spark DataFrames.
"""

import os
from pyspark.sql import SQLContext
from pyspark.sql.dataframe import DataFrame
from pyspark.sql.session import SparkSession
from pyspark.sql.types import *
from azure.ml.api.schema.baseUtil import BaseUtil
from azure.ml.api.schema.swaggerCommon import SwaggerUtil
from azure.ml.api.schema.schemaObjects import Schema, InternalSchema
from azure.ml.api.schema.dataTypes import DataTypes
from azure.ml.api.schema.swaggerFromSpark import Spark2Swagger
from azure.ml.api.schema.constants import ERR_FILE_NOT_SUPPORTED_FOR_SPARK


class SparkSchema(InternalSchema):

    def __init__(self, df_schema):
        if not isinstance(df_schema, StructType):
            raise TypeError("Invalid data fme schema parameter: must be a valid StructType object")
        self.schema = df_schema

    def serialize_to_string(self):
        return self.schema.jsonValue()

    @classmethod
    def deserialize_from_string(cls, serialized_schema_string):
        df_schema = StructType.fromJson(serialized_schema_string)
        return SparkSchema(df_schema)


class SparkUtil(BaseUtil):
    type = DataTypes.SPARK

    spark_session = SparkSession.builder.getOrCreate()
    sqlContext = SQLContext(spark_session.sparkContext)

    @classmethod
    def extract_schema(cls, data_frame):
        if not isinstance(data_frame, DataFrame):
            raise TypeError('Invalid data type: expected a Spark data frame.')

        internal_schema = SparkSchema(data_frame.schema)
        swagger_schema = Spark2Swagger.convert_spark_dataframe_schema_to_swagger(data_frame.schema)

        # Also extract some sample values for the schema from the first few items of the array
        items_to_sample = data_frame.take(BaseUtil.MAX_RECORDS_FOR_SAMPLE_SCHEMA)
        items_count = len(items_to_sample)
        df_record_swagger = swagger_schema['items']
        swagger_schema['example'] = SwaggerUtil.get_swagger_sample(items_to_sample, items_count, df_record_swagger)

        return Schema(SparkUtil.type, internal_schema, swagger_schema)

    @classmethod
    def get_input_object(cls, raw_input_value, schema):
        if not isinstance(raw_input_value, list):
            raise ValueError("Invalid input format: expected an array of items.")

        data_frame = SparkUtil.sqlContext.createDataFrame(data=raw_input_value, schema=schema.internal.schema,
                                                          verifySchema=True)
        return data_frame

    @classmethod
    def get_input_object_from_file(cls, input_file, schema, has_header):
        filename, file_extension = os.path.splitext(input_file)

        if file_extension == '.json':
            import json
            with open(input_file, 'r') as input:
                return SparkUtil.get_input_object(json.load(input), schema)
        elif file_extension == '.csv':
            return SparkUtil.spark_session.read.csv(input_file, schema=schema.internal.schema, header=has_header)
        elif file_extension == '.tsv':
            return SparkUtil.spark_session.read.csv(input_file, schema=schema.internal.schema, header=has_header, sep='\t')
        elif file_extension == '.arff':
            raise ValueError("Unable to parse .arff file {} into spark dataframe.".format(input_file))
        elif file_extension == '.parquet':
            return SparkUtil.spark_session.read.parquet(input_file)
        else:
            raise ValueError(ERR_FILE_NOT_SUPPORTED_FOR_SPARK.format(file_extension))

    @classmethod
    def _load_internal_schema_object(cls, serialized_internal_schema):
        internal_schema = SparkSchema.deserialize_from_string(serialized_internal_schema)
        return internal_schema
