import tempfile
import os

from unittest import TestCase

from leryan.types.simpleconf import *

class SimpleConfTest(TestCase):

    @classmethod
    def setUp(cls):
        cls.iniconf = u"""[sec1]
k1 = val
k2 = 2

[sec2]
k1 = v
k2 = 3"""

        cls.jsonconf = u'{"sec1": {"k1": "val", "k2": "2"}, "sec2": {"k1": "v", "k2": "3"}}'

    def _check_conf(self, sc):
        self.assertEqual(sc.sec1.k1, 'val')
        self.assertEqual(sc.sec1.k2, '2')
        self.assertEqual(sc.sec2.k1, 'v')
        self.assertEqual(sc.sec2.k2, '3')

    def test_ini_fh(self):
        fd, name = tempfile.mkstemp()
        os.write(fd, self.iniconf.encode('utf-8'))
        os.close(fd)

        exception = None

        try:
            with open(name, 'r') as fh:
                sc = SimpleConf.export(Ini(fh=fh))
                self._check_conf(sc)

        except Exception as ex:
            exception = ex

        finally:
            os.unlink(name)

        if exception is not None:
            raise exception

    def test_ini_str(self):
        sc = SimpleConf.export(Ini(sconf=self.iniconf))
        self._check_conf(sc)

    def test_json_fh(self):
        fd, name = tempfile.mkstemp()
        os.write(fd, self.jsonconf.encode('utf-8'))
        os.close(fd)

        exception = None

        try:
            with open(name, 'r') as fh:
                sc = SimpleConf.export(Json(fh=fh))
                self._check_conf(sc)

        except Exception as ex:
            exception = ex

        finally:
            os.unlink(name)

        if exception is not None:
            raise exception