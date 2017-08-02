# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import os.path
from azure.ml.api.realtime.swagger_spec_generator import generate_service_swagger
from tests.unit_tests.ut_common import UnitTestBase


class SwaggerGenerationTests(UnitTestBase):
    def test_swagger_generation(self):
        schema_path = os.path.join(UnitTestBase.tests_folder, "resources/service_schema.json")
        service_name = "test_svc"
        expected_swagger_path = os.path.join(UnitTestBase.tests_folder, "resources/expected_service_swagger.json")
        swagger_json = generate_service_swagger(service_name, schema_path, "1.1")
        with open(expected_swagger_path, 'r') as f:
            expected_swagger_json = json.load(f)
        self.assertEqual(swagger_json, expected_swagger_json)
