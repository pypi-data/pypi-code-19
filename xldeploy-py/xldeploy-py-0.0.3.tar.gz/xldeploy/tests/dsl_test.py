from unittest import TestCase
import os
import xldeploy
from xldeploy.domain.ConfigurationItem import ConfigurationItem


class DslTest(TestCase):

    def setUp(self):
        config = xldeploy.Config()
        client = xldeploy.Client(config)
        self.dsl = client.dsl
        self.repo = client.repository

    def clean_up_cis(self):
        # Cleanup
        self.repo.delete("Environments/DEV")
        self.repo.delete("Infrastructure/localHost")

    def generate_dsl_test(self):
        localhost = ConfigurationItem("Infrastructure/localHost", "overthere.LocalHost", { "os": "UNIX" })
        self.repo.create_ci(localhost)
        directory_ci = ConfigurationItem("Environments/DEV", "core.Directory")
        self.repo.create_ci(directory_ci)
        environment_ci = ConfigurationItem("Environments/DEV/SampleEnv", "udm.Environment", {'members': [localhost.id]})
        self.repo.create_ci(environment_ci)

        generated_dsl = self.dsl.generate(['Environments/DEV'])
        expected_dsl = open(os.path.join(os.path.dirname(__file__), 'test_dsl.txt'), 'r').read()
        self.assertEquals(generated_dsl, expected_dsl)
        self.clean_up_cis()

    def apply_dsl_test(self):
        localhost = ConfigurationItem("Infrastructure/localHost", "overthere.LocalHost", { "os": "UNIX" })
        self.repo.create_ci(localhost)
        dsl_to_apply = open(os.path.join(os.path.dirname(__file__), 'test_dsl.txt'), 'r').read()
        self.dsl.apply(dsl_to_apply)
        self.assertTrue(self.repo.exists("Environments/DEV/SampleEnv"))
        self.clean_up_cis()
