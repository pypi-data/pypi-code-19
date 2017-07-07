import unittest
import modconf

class TestClass:
    def test(self):
        args = ('hello', 1)
        cls = modconf.import_class('modconf.tests.conf.conf_class', 'Conf', args)
        assert cls.args == args

