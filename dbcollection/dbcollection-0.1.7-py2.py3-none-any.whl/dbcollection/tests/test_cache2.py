#!/usr/bin/env python3

"""
dbcollection/cache.py unit testing.
"""


import os
import sys
import copy

import unittest
if sys.version_info[0] == 2:
    import mock
else:
    from unittest import mock


# dir_path = os.path.dirname(os.path.realpath(__file__))
# lib_path = os.path.abspath(os.path.join(dir_path, '..', '..', '..'))
# sys.path.append(lib_path)
from dbcollection.cache import CacheManager


class CacheManagerTest(unittest.TestCase):
    """
    Test class.
    """

    # @patch('__main__.CacheManager.create_cache_file_disk')
    # @patch('__main__.CacheManager.read_data_cache')
    # @patch('os.path.exists', return_value=True)
    def setUp(self):
        """
        Initialize class.
        """
        # create a sample cache data dictionary
        default_cache_dir =  "tmp/dir/"
        default_data_dir =  "tmp/dir/data/"
        self.sample_cache_data = {
            "info":{
                "default_cache_dir": default_cache_dir,
                "default_data_dir": default_data_dir,
            },
            "dataset":{
                "cifar10":{
                    "cache_dir" : "tmp/dir/",
                    "data_dir" : "tmp/dir/",
                    "tasks":{
                        "default" : "file1.h5",
                        "classific" : "file2.h5",
                        "extra" : "file3.h5"
                        },
                    "keywords" : ['image_processing', 'classification']
                },
                "cifar100": {}
            },
            "category":{
                'image_processing': ['cifar10'],
                'classification': ['cifar10']
            }
        }

        ## mock function return value
        #mock_read.return_value = self.sample_cache_data
        #
        ## create class
        #self.cache_manager = CacheManager()
        #self.cache_manager.default_cache_dir = default_cache_dir
        #self.cache_manager.default_data_dir = default_data_dir
        #
        ## check if the object is of the same type
        #self.assertIsInstance(self.cache_manager, CacheManager, 'Object: CacheManager')
        #
        ## check if the mocked functions were called correctly
        #self.assertTrue(mock_os.called, 'os.path.exists')
        #self.assertTrue(mock_read.called, 'CacheManager.read_data_cache')
        #self.assertFalse(mock_file.called, 'CacheManager.create_cache_file_disk')


    # @patch('builtins.open', mock_open(read_data='1'))
    # @patch('json.load')
    def test_read_data_cache_file__return_valid_data(self):
        """
        Test loading data from the json file.
        """
        pass
    
    def test_read_data_cache_file__return_invalid_data(self):
        """
        Test loading data from the json file.
        """
        pass


#----------------
# Run Test Suite
#----------------

def main(level=1):
    """Main function to start testing"""
    unittest.main(verbosity=level)

if __name__ == '__main__':
    main()
