# pylint: disable=unused-argument,unused-variable,protected-access
"""
This module adds a new marker @xmlprops which addes additional properties
to a test class in junit xml. Also modifies testcase name with the
@Title specified test case docstrings
"""
import re
import pytest

__all__ = [
    "xmlprop",
]


xmlprop = pytest.mark.xmlprop


def pytest_configure(config):
    """ Call ModifyJunit Plugin if junitxml is passed with py.test """
    if config.pluginmanager.hasplugin('junitxml'):
        config.pluginmanager.register(ModifyJunit(config), 'ModifyJunit')


class ModifyJunit(object):
    """ Modify junit xml by adding properties specified using
        marker @xmlprops
    """
    def __init__(self, config):
        """ modify junit xml file  """
        super(ModifyJunit, self).__init__()
        self._conf = config

    @property
    def junit(self):
        """ Get attributes of the junit xml """
        return getattr(self._conf, '_xml', None)

    def _add_property(self, report, name, value):
        """ Add property to testcase """
        if hasattr(self.junit, 'node_reporter'):
            reporter = self.junit.node_reporter(report.nodeid)
            reporter.add_property(name, value)
        else:
            pass #plugin is installed but not run with --junitxml

    def _add_marks(self, item, report):
        """ add markers to the junit xml """
        mark_info = item.get_marker('xmlprop')
        if mark_info:
            if len(mark_info.args) % 2 != 0:
                raise ValueError('xmlprop marks must be set in name value pairs')

            for nv_pair in [mark_info.args[i:i+2] for i in range(0, len(mark_info.args), 2)]:
                (name, value) = nv_pair
                self._add_property(report, name, value)

    @pytest.hookimpl(tryfirst=True, hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """ Fetch the title from docstrings during call phase """
        outcome = yield
        rep = outcome.get_result()
        title_regex = re.compile("^.[T|t]itle\s*:\s*.*")
        if item._obj.__doc__:
            tc_name = item._obj.__doc__.strip().split('\n')[0]
            for line in item._obj.__doc__.strip().split('\n'):
                if title_regex.match(line):
                    tc_name = re.sub("^.[T|t]itle\s*:\s*", "", line)
                    break
            rep.nodeid = '::'.join(rep.nodeid.split('::')[0:-1]) + \
                         '::' + tc_name
        if 'call' in rep.when:
            self._add_marks(item, rep)
