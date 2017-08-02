# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import abc


class BaseUtil(object):
    __metaclass__ = abc.ABCMeta

    MAX_RECORDS_FOR_SAMPLE_SCHEMA = 3

    @classmethod
    @abc.abstractmethod
    def extract_schema(cls, data):
        pass

    @classmethod
    @abc.abstractmethod
    def get_input_object(cls, input, schema):
        pass

    @classmethod
    @abc.abstractmethod
    def _load_internal_schema_object(cls, serialized_internal_schema):
        pass

    @staticmethod
    def _validate_schema_object_property(schema, property_name, schema_file):
        if property_name not in schema \
                or schema[property_name] is None\
                or len(schema[property_name]) == 0:
            err = "Invalid schema file - {0}:  the {1} property must be specified.".format(schema_file, property_name)
            raise ValueError(err)
