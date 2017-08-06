import unittest
from flask  import Flask, abort, request, make_response, current_app , Response
from pseuserver import *
from pseuserver.methods import *
import pseuserver
import requests
import json
from pprint import pprint as pp
import os
from pseudb import *
# from pseudb.storages import JSONStorage, MemoryStorage


class TestMethods(unittest.TestCase):
    # def setUp(self):
        # pseuserver.DEFAULT_CONFIG = 'test.config.json'
        # _db = 'test.db.json'
        # this_dir = os.path.dirname(os.path.realpath(__file__))
        
        # self.db_file = os.path.join(this_dir, _db)
        # self.db = PseuDB(self.db_file)



    # def tearDown(self):
    #     self.db.close()

    #     if os.path.exists(self.db_file):
    #         os.remove(self.db_file)

    

    def test_output_json(self):
        pass
        # self.db.purge_tables()
        # kwargs = {}
        # kwargs[CONFIG_DB] = self.db_file
        # kwargs[RESOURCE_DOCUMENT] = 'posts'
        # kwargs[RESOURCE_DATA] = b'{\"text\": \"post 1\", \"author\": \"harry\" }'

        # result = create(**kwargs)

        # self.assertEqual( result ,
        #     {'id':1, 'text': 'post 1', 'author': 'harry'})

    def test_get(self):
        pass

if __name__ == "__main__":
    unittest.main()            