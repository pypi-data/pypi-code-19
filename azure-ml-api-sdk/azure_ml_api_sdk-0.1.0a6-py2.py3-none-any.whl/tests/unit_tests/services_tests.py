# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import numpy as np
import pandas as pd

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from azure.ml.api.realtime import services
from azure.ml.api.schema.sampleDefinition import SampleDefinition
from azure.ml.api.schema.dataTypes import DataTypes
from azure.ml.api.schema.schemaUtil import *
from tests.unit_tests.ut_common import UnitTestBase
from azure.ml.api.schema.sparkUtil import SparkUtil
from pyspark.sql import SQLContext


class ServicesTests(UnitTestBase):
    int_array = np.array(range(10), dtype=np.int32)
    input_types = {'a': SampleDefinition(DataTypes.NUMPY, int_array),
                   'b': SampleDefinition(DataTypes.STANDARD, 10)}
    output_types = {'output1': SampleDefinition(DataTypes.STANDARD, "Adf")}
    output_type = {"sdf": "Sdf"}

    _int_array = np.array(range(10), dtype=np.int32)
    _birthsPerName = list(
        zip(['Bob', 'Jessica', 'Mary', 'John', 'Mel'], [968, 155, 77, 578, 973]))
    _births_df = pd.DataFrame(data=_birthsPerName, columns=['Names', 'Births'])
    _sqlContext = SQLContext(SparkUtil.spark_session.sparkContext)
    _contacts_df = _sqlContext.read.json(
        os.path.join(UnitTestBase.tests_folder, 'resources/contact_data.json'))

    user_input_schema = {
        "ints": SampleDefinition(DataTypes.NUMPY, _int_array),
        "contacts": SampleDefinition(DataTypes.SPARK, _contacts_df),
        "number": SampleDefinition(DataTypes.STANDARD, 10)}
    output_schema = {"births": SampleDefinition(DataTypes.PANDAS, _births_df)}

    def test_validate_run_func_no_schema(self):
        self.validate_run_func_base(sample_run, None,
                                    expected_msg="Provided run function has arguments")

    def test_validate_run_func_no_args_no_schema(self):
        self.validate_run_func_base(sample_run_no_args, None, num_args=0, num_defaults=0)

    def test_validate_run_func_happy(self):
        self.validate_run_func_base(sample_run_2, self.user_input_schema,
                                    num_args=3, num_defaults=1)

    def test_validate_run_func_kwargs_happy(self):
        self.validate_run_func_base(sample_run, {'a': None,
                                                 'b': None},
                                    num_args=2, num_defaults=0)

    def test_validate_run_func_bad_missing_arg_in_schema(self):
        self.validate_run_func_base(sample_run, {'a': None},
                                    expected_msg='Argument mismatch: Provided run')

    def test_validate_run_func_bad_extra_arg_in_schema(self):
        self.validate_run_func_base(sample_run, {'a': None,
                                                 'b': None,
                                                 'c': None},
                                    expected_msg='Argument mismatch: Provided run')

    def validate_run_func_base(self, fn, schema, num_args=0, num_defaults=0,
                               expected_msg=None):
        try:
            args, defaults = services._validate_run_func_args(fn, schema)
            # fail if expected message is not None and we don't throw
            self.assertEqual(expected_msg, None)
            self.assertEqual(len(args), num_args)
            self.assertEqual(len(defaults), num_defaults)
        except ValueError as exc:
            if not str(exc).startswith(expected_msg):
                self.fail('Threw ValueError with incorrect message. '
                          'Expected: "{}" and got "{}"'.format(expected_msg, str(exc)))

    @patch('azure.ml.api.realtime.services._validate_run_func_args')
    @patch('azure.ml.api.realtime.services._generate_service_schema')
    def test_generate_schema_no_write(self, generate_schema_mock, validate_run_func_mock):
        expected_schema = 'an awesome schema'
        generate_schema_mock.return_value = expected_schema
        schema = services.generate_schema(sample_run)
        self.assertEqual(schema, expected_schema)
        generate_schema_mock.assert_called_once()
        validate_run_func_mock.assert_called_once()

    @patch('azure.ml.api.realtime.services.json.dump')
    @patch('azure.ml.api.realtime.services.open')
    @patch('azure.ml.api.realtime.services._validate_run_func_args')
    @patch('azure.ml.api.realtime.services._generate_service_schema')
    def test_generate_schema_with_write(self, generate_schema_mock, validate_run_func_mock, open_mock, dump_mock):
        expected_schema = 'an awesome schema'
        generate_schema_mock.return_value = expected_schema
        schema = services.generate_schema(sample_run, filepath='/my/awesome/filepath')
        self.assertEqual(schema, expected_schema)
        generate_schema_mock.assert_called_once()
        validate_run_func_mock.assert_called_once()
        open_mock.assert_called_once()
        dump_mock.assert_called_once()


def sample_run_2(ints, contacts, number=10):
    return ServicesTests._births_df


def sample_run(a, **b):
    print(a)
    return b


def sample_run_no_args():
    return "asdf"


def sample_run_default(a, b=[2, 3, 4]):
    print(a)
    return b


def sample_run_no_args_no_output():
    print(10)
