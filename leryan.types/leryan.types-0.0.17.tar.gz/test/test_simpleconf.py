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

        cls.iniconf_interp = u"""[vars]
v1 = val
v2 = 2
v3 = 3
v4 = v

[sec1]
k1 = ${vars:v1}
k2 = ${vars:v2}

[sec2]
k1 = ${vars:v4}
k2 = ${vars:v3}"""

        cls.jsonconf = u'{"sec1": {"k1": "val", "k2": "2"}, "sec2": {"k1": "v", "k2": "3"}}'

    def _check_conf(self, sc):
        self.assertEqual(sc.sec1.k1, 'val')
        self.assertEqual(sc.sec1.k2, '2')
        self.assertEqual(sc.sec2.k1, 'v')
        self.assertEqual(sc.sec2.k2, '3')
        self.assertEqual(sc['sec1']['k1'], 'val')
        self.assertEqual(sc['sec1']['k2'], '2')
        self.assertEqual(sc['sec2']['k1'], 'v')
        self.assertEqual(sc['sec2']['k2'], '3')

    def _open_fd_check_conf(self, sconf, driver_cls, func_check_conf, *args, **kwargs):
        fd, name = tempfile.mkstemp()
        os.write(fd, sconf.encode('utf-8'))
        os.close(fd)

        exception = None

        try:
            with open(name, 'r') as fh:
                sc = SimpleConf.export(driver_cls(fh=fh, *args, **kwargs))
                func_check_conf(sc)

        except Exception as ex:
            exception = ex

        finally:
            os.unlink(name)

        if exception is not None:
            raise exception

    def test_ini_fh(self):
        self._open_fd_check_conf(self.iniconf, Ini, self._check_conf)

    def test_ini_interpolate_fh(self):
        self._open_fd_check_conf(
            self.iniconf_interp, Ini, self._check_conf, with_interpolation=True)

    def test_ini_str(self):
        sc = SimpleConf.export(Ini(sconf=self.iniconf))
        self._check_conf(sc)

    def test_json_fh(self):
        self._open_fd_check_conf(self.jsonconf, Json, self._check_conf)
