# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json


class SwaggerUtil:
    @staticmethod
    def get_swagger_object_schema():
        return {'type': 'object', 'properties': {}}

    @staticmethod
    def get_swagger_sample(iterable_records, max_count, item_schema):
        sample_swagger = []
        for i in range(max_count):
            item_sample = SwaggerUtil._get_data_record_swagger_sample(item_schema, iterable_records[i])
            sample_swagger.append(item_sample)
        return sample_swagger

    @staticmethod
    def _get_data_record_swagger_sample(item_swagger_schema, data_item):
        item_type = item_swagger_schema['type']
        if item_type == 'object':
            if 'properties' in item_swagger_schema:
                sample_swag = dict()
                for field in item_swagger_schema['properties']:
                    sample_swag[field] = SwaggerUtil._get_data_record_swagger_sample(
                        item_swagger_schema['properties'][field], data_item[field])
            elif 'additionalProperties' in item_swagger_schema:
                sample_swag = dict()
                for field in data_item:
                    sample_swag[field] = SwaggerUtil._get_data_record_swagger_sample(
                        item_swagger_schema['additionalProperties'], data_item[field])
            else:
                sample_swag = str(data_item)
        elif item_swagger_schema['type'] == 'array':
            sample_swag = []
            subarray_item_swagger = item_swagger_schema['items']
            for i in range(len(data_item)):
                array_item_sample = SwaggerUtil._get_data_record_swagger_sample(
                    subarray_item_swagger, data_item[i])
                sample_swag.append(array_item_sample)
        elif item_type == 'number':
            sample_swag = float(data_item)
        elif item_type == 'integer':
            sample_swag = int(data_item)
        elif item_type == 'bool':
            sample_swag = bool(data_item)
        else:
            sample_swag = str(data_item)
        return sample_swag
