from unittest import TestCase
import xldeploy
from xldeploy.domain.ConfigurationItem import ConfigurationItem
from xldeploy.domain.QueryBuilder import QueryBuilder


class RepositoryTest(TestCase):
    def setUp(self):
        config = xldeploy.Config()
        client = xldeploy.Client(config)
        self.repo = client.repository

    # repository.copy(String id, String newId) : ConfigurationItem
    def test_copy(self):
        ci = ConfigurationItem("Applications/Sample", "udm.Application")
        created_CI = self.repo.create_ci(ci);
        self.assertEquals(ci.id, created_CI.id)
        self.assertEquals(ci.type, created_CI.type)

        ci = self.repo.copy("Applications/Sample", "Applications/CopySample");
        self.assertEquals("Applications/CopySample", ci.id)

        # Cleanup
        self.repo.delete("Applications/Sample");
        self.repo.delete("Applications/CopySample");

    # repository.create(ConfigurationItem ci) : ConfigurationItem
    def test_create_CI(self):
        ci = ConfigurationItem("Applications/Sample", "udm.Application")
        created_CI = self.repo.create_ci(ci);
        self.assertEquals(ci.id, created_CI.id)
        self.assertEquals(ci.type, created_CI.type)

        # Cleanup
        self.repo.delete("Applications/Sample");

    # repository.delete(String id) : void
    def test_delete(self):
        ci = ConfigurationItem("Applications/Sample", "udm.Application")
        created_CI = self.repo.create_ci(ci);
        self.assertEquals(ci.id, created_CI.id)
        self.assertEquals(ci.type, created_CI.type)

        self.repo.delete("Applications/Sample");

        result = self.repo.exists("Applications/Sample");
        self.assertEquals(False, result)

    # repository.exists(String id) : boolean
    def test_exists(self):
        ci = ConfigurationItem("Applications/Sample", "udm.Application")
        created_CI = self.repo.create_ci(ci);
        self.assertEquals(ci.id, created_CI.id)
        self.assertEquals(ci.type, created_CI.type)

        result = self.repo.exists("Applications/Sample");
        self.assertEquals(True, result)

        #Cleanup
        self.repo.delete("Applications/Sample");

    # repository.read(String id) : ConfigurationItem
    def test_read(self):
        ci = ConfigurationItem("Applications/Sample", "udm.Application")
        created_CI = self.repo.create_ci(ci);
        created_CI = self.repo.read(ci.id)
        self.assertEquals(ci.id, created_CI.id)
        self.assertEquals(ci.type, created_CI.type)

        #Cleanup
        self.repo.delete("Applications/Sample");

    # repository.rename(String id, String newName) : ConfigurationItem
    def test_rename_by_ID(self):
        ci = ConfigurationItem("Applications/Sample", "udm.Application")
        created_CI = self.repo.create_ci(ci);
        created_CI = self.repo.rename(ci.id, "RenamedSample")
        self.assertEquals("Applications/Sample", created_CI.id)
        self.assertEquals(ci.type, created_CI.type)

        #Cleanup
        self.repo.delete("Applications/RenamedSample");

    def test_query_by_type(self):
        params = QueryBuilder().type("udm.Environment").build()
        env_list = self.repo.query(params)
        self.assertTrue(isinstance(env_list, list))