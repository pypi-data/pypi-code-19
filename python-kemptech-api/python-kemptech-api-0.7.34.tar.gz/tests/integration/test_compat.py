from unittest import TestCase
from os import listdir
from os.path import isfile, join

import xmltodict

from python_kemptech_api import lxml_to_dict
from bin.conf import XML_COMPAT_DIR


class LxmlCompatLayerTests(TestCase):
    def setUp(self):
        self.test_files = [
            join(XML_COMPAT_DIR, file_path)
            for file_path
            in listdir(XML_COMPAT_DIR)
            if file_path.endswith('.xml') and
            isfile(join(XML_COMPAT_DIR, file_path))
        ]

    def test_xmltodict_compatibility(self):
        for path in self.test_files:
            with open(path) as f:
                xml = f.read()
                xmltodict_res = xmltodict.parse(xml)
                lxml_to_dict_res = lxml_to_dict.parse(xml)
                assertion_msg = (
                    'Incompatibility found between '
                    'xmltodict and lxml_to_dict in {}'
                    .format(path))
                self.assertDictEqual(
                    xmltodict_res,
                    lxml_to_dict_res,
                    assertion_msg)
