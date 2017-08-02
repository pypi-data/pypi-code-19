# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azure.ml.api.schema.dataTypes import DataTypes


class SampleDefinition:
    def __init__(self, input_type, sample_data):
        if input_type is DataTypes.NUMPY:
            from azure.ml.api.schema.numpyUtil import NumpyUtil
            self.schema = NumpyUtil.extract_schema(sample_data)
        elif input_type is DataTypes.SPARK:
            from azure.ml.api.schema.sparkUtil import SparkUtil
            self.schema = SparkUtil.extract_schema(sample_data)
        elif input_type is DataTypes.PANDAS:
            from azure.ml.api.schema.pandasUtil import PandasUtil
            self.schema = PandasUtil.extract_schema(sample_data)
        elif input_type is DataTypes.STANDARD:
            from azure.ml.api.schema.pythonUtil import PythonUtil
            self.schema = PythonUtil.extract_schema(sample_data)
        else:
            raise ValueError("Invalid sample definition type: {}. This type is not supported. Please use one of the "\
                             "values defined in dataTypes.DataTypes".format(self.type))
        self.type = input_type

    def serialize(self):
        return {"internal": self.get_schema_string(), "swagger": self.schema.swagger, "type": self.type}

    def get_schema_string(self):
        return self.schema.internal.serialize_to_string()
