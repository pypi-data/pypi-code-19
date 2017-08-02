# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import numpy as np
import os.path
import json
from tests.unit_tests.schema_tests_common import SchemaUnitTests
from azure.ml.api.schema.numpyUtil import NumpyUtil
from azure.ml.api.schema.dataTypes import DataTypes
from azure.ml.api.schema.sampleDefinition import SampleDefinition
from azure.ml.api.schema.schemaUtil import save_service_schema, load_service_schema


class NumpyUtilTests(SchemaUnitTests):
    int_array = np.array(range(10), dtype=np.int32)
    _structured_dt = np.dtype([('name', np.str_, 16), ('grades', np.float64, (2,))])
    struct_array = np.array([('Sarah', (8.0, 7.0)), ('John', (6.0, 7.0))], dtype=_structured_dt)
    _nested_array_dt = np.dtype("i4, (2,2,3)f8, f4")
    multi_level_array = np.array([(1, (((4.6, 3.2, 1.5), (1.1, 1.2, 1.3)), ((1.6, 1.2, 1.5), (3.1, -1.2, 8.3))), 3.6)],
                                 dtype=_nested_array_dt)

    _batch_expected_dt = np.dtype([('name', np.str_, 16), ('age', np.int64)])
    batch_expected_data = np.array([('John', 24), ('Tim', 24), ('Sally', 21), ('Jill', 26)], dtype=_batch_expected_dt)

    def test_single_array_schema_extract(self):
        # Simple types array
        self._run_schema_extract_test(self.int_array, 'int_array')
        # Structured data type array
        self._run_schema_extract_test(self.struct_array, 'struct_data_array')
        # Multi level array
        self._run_schema_extract_test(self.multi_level_array, 'multi_level_array')

    def test_schema_save_load(self):
        schema_filepath = 'saveload.schema'
        try:
            self.assertFalse(os.path.exists(schema_filepath), "Generated schema file was found prior to test run")

            # Extract & persist service schema to disk
            input_spec = {"data": SampleDefinition(DataTypes.NUMPY, self.struct_array)}
            output_spec = {"out": SampleDefinition(DataTypes.NUMPY, self.int_array)}
            save_service_schema(schema_filepath, input_spec, output_spec)
            self.assertTrue(os.path.exists(schema_filepath), "Expected generated schema file was not found")

            # Load & validate service schema from disk
            service_schema = load_service_schema(schema_filepath)
            self.assertIsNotNone(service_schema.input, "Service schema must have an input defined")
            self.assertTrue("data" in service_schema.input, "Expected input schema missing")
            self._validate_numpy_extracted_schema(self.struct_array, service_schema.input["data"],
                                                  self.expected_swagger_set['struct_data_array'])
            self.assertIsNotNone(service_schema.output, "Service schema must have an output defined")
            self.assertTrue("out" in service_schema.output, "Expected output schema missing")
            self._validate_numpy_extracted_schema(self.int_array, service_schema.output["out"],
                                                  self.expected_swagger_set['int_array'])
        finally:
            SchemaUnitTests._delete_test_schema_file(schema_filepath)

    def test_input_parsing(self):
        # First generate the input schema
        input_schema = NumpyUtil.extract_schema(self.struct_array)

        # Now parse the input json into a numpy array with the same schema
        input_json = '[{"name": "Steven", "grades": [3.3, 5.5]}, {"name": "Jenny", "grades": [8.8, 7.5]}, {"name": "Dan", "grades": [9.3, 6.7]}]'
        parsed_input = NumpyUtil.get_input_object(json.loads(input_json), input_schema)

        # Validate the result
        self.assertIsNotNone(parsed_input, "Parsed input must have a value here")
        self.assertTrue(type(parsed_input) == np.ndarray, "Parsed input must be a numpy array.")
        self.assertEqual(3, len(parsed_input),
                         "Parsed array holds {0} elements instead of expected {1}".format(len(parsed_input), 3))
        self.assertEqual(parsed_input.dtype, self.struct_array.dtype,
                         "Parsed array dtype={0} is different than expected {1}".format(parsed_input.dtype,
                                                                                        self.struct_array.dtype))

    def test_input_from_json_file_parsing(self):
        self._run_input_from_file_test(self.sample_json)

    def test_input_from_csv_file_parsing(self):
        self._run_input_from_file_test(self.sample_csv)

    def test_input_from_tsv_file_parsing(self):
        self._run_input_from_file_test(self.sample_tsv)

    def test_input_from_arff_file_parsing(self):
        self._run_input_from_file_test(self.sample_arff)

    def test_input_from_parquet_file_parsing(self):
        # Generate the input schema
        input_schema = NumpyUtil.extract_schema(self.batch_expected_data)

        with self.assertRaises(ValueError):
            NumpyUtil.get_input_object_from_file(self.sample_parquet, input_schema, True)

    def _run_input_from_file_test(self, input_file):
        # Generate the input schema
        input_schema = NumpyUtil.extract_schema(self.batch_expected_data)

        # Parse the input file
        parsed_input = NumpyUtil.get_input_object_from_file(input_file, input_schema, True)

        # Validate the result
        self.assertIsNotNone(parsed_input, "Parsed input must have a value here")
        self.assertTrue(type(parsed_input) == np.ndarray, "Parsed input must be a numpy array.")
        self.assertEqual(4, len(parsed_input), "Parsed array holds {0} elements instead of expected {1}".format(len(parsed_input), 4))
        self.assertEqual(parsed_input.dtype, self.batch_expected_data.dtype, "Parsed array dtype={0} is different than expected {1}".format(parsed_input.dtype, self.batch_expected_data.dtype))
        self.assertTrue(np.array_equiv(parsed_input, self.batch_expected_data), "Parsed array {0} is different than expected array {1}".format(parsed_input, self.batch_expected_data))

    def _run_schema_extract_test(self, array, swagger_key):
        expected_swagger = self.expected_swagger_set[swagger_key]
        schema = NumpyUtil.extract_schema(array)
        self._validate_numpy_extracted_schema(array, schema, expected_swagger)
