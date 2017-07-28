import collections
import os

import jprops
from allure.constants import COMMON_NAMESPACE
from allure.rules import xmlfied, Attribute, Element, WrappedMany, Nested, Many, \
    Ignored
from allure.structure import IterAttachmentsMixin


# overwriting the base class in allure.structure with an additional URL param.
class Environment(xmlfied('environment',
                          namespace=COMMON_NAMESPACE,
                          id=Element(),
                          name=Element(),
                          url=Element(),  # Added
                          parameters=Many(Nested()))):
    pass


# Overwriting the base class in allure.structure with an additional SEVERITY attribute.
class TestCase(IterAttachmentsMixin,
               xmlfied('test-case',
                       id=Ignored(),  # internal field, see AllureTestListener
                       name=Element(),
                       title=Element().if_(lambda x: x),
                       description=Element().if_(lambda x: x),
                       #                        description=Element(),
                       failure=Nested().if_(lambda x: x),
                       steps=WrappedMany(Nested()),
                       attachments=WrappedMany(Nested()),
                       labels=WrappedMany(Nested()),
                       status=Attribute(),
                       severity=Attribute(),  # Added
                       start=Attribute(),
                       stop=Attribute(),
                       statusDetails=Attribute())):
    pass


class ContextType(object):
    HIGH_LEVEL_SUITE = 'HIGH_LEVEL_SUITE'
    SUITE_WITH_TESTS = 'SUITE_WITH_TESTS'
    TEST = 'TEST'
    STEP = 'STEP'


class ContextTypeState(object):
    STARTED = 'STARTED'
    ENDED = 'ENDED'


class HighLevelSuite(object):
    def __init__(self):
        self.setup_steps = []
        self.teardown_steps = []
        self.setup = False
        self.teardown = False
        self.suites = []
        self.tests = []
        self.parent_suite = None
        self.state = ContextTypeState.STARTED
        self.name = None
        self.title = None
        self.description = None
        self.start = None
        self.stop = None
        self.status = None


class Test(object):
    def __init__(self):
        self.setup_steps = []
        self.teardown_steps = []
        self.steps = []
        self.parent_suite = None
        self.setup = False
        self.teardown = False
        self.state = ContextTypeState.STARTED
        self.name = None
        self.description = None
        self.start = None
        self.end = None
        self.tags = None
        self.critical = None
        self.status = None
        self.message = None


class Step(object):
    def __init__(self):
        self.messages = []
        self.attachments = []
        self.steps = []
        self.parent = None
        self.state = ContextTypeState.STARTED
        self.name = None
        self.title = None
        self.doc = None
        self.tags = None
        self.start = None
        self.stop = None
        self.status = None


class AllureProperties(object):
    def __init__(self, propertiesPath):
        self.path = propertiesPath
        if os.path.exists(self.path) is True:
            with open(self.path) as fp:
                self.properties = jprops.load_properties(fp, collections.OrderedDict)
            fp.close()
        else:
            return false

        #         return properties

    def save_properties(self, path=None):
        # store the Allure properties
        #
        if (path is None):
            output_path = self.get_property('allure.cli.logs.xml') + '\\allure.properties'
        else:
            output_path = path

        with open(output_path, 'w+') as fp:
            jprops.store_properties(fp, self.properties, timestamp=False)
        fp.close()

        return True

    def get_property(self, name):

        if name in list(self.properties.keys()):
            return self.properties[name]
        else:
            return None

    def get_properties(self):

        return self.properties

    def set_property(self, name, value):

        self.properties[name] = value

        return True
