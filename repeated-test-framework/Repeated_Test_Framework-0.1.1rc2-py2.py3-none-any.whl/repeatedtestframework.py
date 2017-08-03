#!/usr/bin/env python
# coding=utf-8
"""
# repeatedtestframework : Functionality to support the creation of multiple
                          test cases with the Unittest framework

Summary :
    Helper functionality to reduce the amount of boiler plate or repeated
    code which is implemented when the same functionality is tested multiple
    times with the different data.

Use Case :
    As a user I want to reduce the amount of boiler plate and repeated code
    so as to reduce errors.

Testable Statements :
    ...
"""
import six as _six
import unittest

from .version import __version__ as __version__

__author__ = 'Tony Flury : anthony.flury@btinternet.com'
__created__ = '17 Jan 2017'

# Python 3 introduced the collections.abc module
if _six.PY2:
    from collections import Iterable, Mapping
else:
    from collections.abc import Iterable, Mapping


class GenerateTestMethods(object):
    """A decorator for unittest.TestCase class to auto-generate test methods
       based on data list"""

    def __init__(self, test_name='',
                 test_method=None,
                 test_cases=None,
                 method_name_template="test_{index:03d}_{test_name}",
                 method_doc_template="{test_name} {index:03d}: "
                                     "{test_data}"
                 ):
        """Automatically generates test cases based on the data sets

        ``test_name`` must be a string which can be included in a
        method name (i.e. alphabetic, numeric and underscore `_` only)

        ``test_method`` is the function which executes the actual test.
        By default the method should be function with the signature :

            *test_method* (index: int, input: object, expected_result: object)

        .. note::

            Since the actual test methods on the unittest.TestCase are instance methods,
            they expect to be passed only *self* as an arguemnt when called.

            This means that
            test_method **must** be a wrapping function which contains the actual
            test exacution method as a closure. This is illustrated in the example code below

        ``test_cases`` is a iterator for which each entry is a Mapping (for
        instance a dict). Each dict is unpacked as arguments into the callable
        specified by the test_method arguemnt. By default the dict should contain
        the keys ``input``, and ``expected_results``, with the appropriate values
        required to execute the tests.

        ``method_name_template`` is a python format string which defines the name
        of the test methods to be created.

        ``method_doc_template`` is a python format string which defines the
        documentation string of the test methods to be created.

        Both the ``method_name_template`` and ``method_doc_template`` can contain
        the following keys :

            - ``test_name`` : the value is the string passed into `test_name`` attrribute.
            - ``index`` : the value is the start from zero index of the appropriate entry in the `test_case` iterator for this test case
            - ``test_data`` : the value is the appropriate entry within the test_cases iterator for this test case.

        :param test_name: mandatory valid python identifier for these tests
        :param test_method: mandatory the actual test method to execute
        :param test_cases: mandatory a list of tuples defining the actual test cases
        :param method_name_template: optional A format string for the test method name
        :param method_doc_template: optional A format string for the test doc string

        :type test_name: str
        :type test_method: Callable
        :type test_cases: list[ Mapping ] | None
        :type method_name_template: str
        :type method_doc_template: str

        """
        if not self._isidentifier(test_name):
            raise ValueError(
                'test_name value not able to be used in a method name')
        else:
            self._test_name = test_name

        if not (callable(test_method)):
            raise TypeError('test_method is not callable')
        else:
            self._method = test_method

        if not (isinstance(test_cases, Iterable)):
            raise TypeError('test_cases is not a valid Iterator')
        else:
            self._test_cases = test_cases

        self._method_name_template = method_name_template
        self._method_doc_template = method_doc_template

    @staticmethod
    def _isidentifier(name):
        """returns True only if strng can be included into a method name"""
        if not name:
            return False
        else:
            return all(
                True if (c.isalnum() or c == "_") else False for c in name)

    def __call__(self, cls):

        if not issubclass(cls, unittest.TestCase):
            raise TypeError(
                'Invalid type: Decorator target is not '
                'unittest.TestCase subclass')

        cls._RTF_DECORATED = True
        cls._RTF_METHODS = {}

        for index, case in enumerate(self._test_cases):
            if not isinstance(case, Mapping):
                raise TypeError(
                    "test_cases item {} is not a Mapping".format(index))

            # Add in the test data as a single item
            test_data = {'index': index, 'test_data': case}

            # Pass test_data as individual arguments to the test method
            test_method = self._method(index, **case)

            test_method.__name__ = self._method_name_template.format(
                test_name=self._test_name, index=index, test_data=case)
            test_method.__doc__ = self._method_doc_template.format(
                test_name=self._test_name, index=index, test_data=case)
            setattr(cls, test_method.__name__, test_method)
            cls._RTF_METHODS[test_method.__name__] = test_data
        return cls


# noinspection PyPep8Naming
def DecorateTestMethod(criteria=lambda test_data: True, decorator_method=None,
                       decorator_args=None, decorator_kwargs=None):
    """A decorator to allow generated test methods to be deocorated (e.g.. skipped)

    :param criteria: A callable which will return boolean. The callable is passed a relevant item from test_input list (from the ``GenerateTestMethods``) call. The ``criteria`` should return a boolean value which determines if the test method which will be generated for this test_input item should be deoctorated or not.
    :param decorator_method: A decorator called which will be used to decorate the test_method.
    :param decorator_args:  A typle of the positional arguments passed to the ``decorator_method`` callable.
    :param decorator_kwargs: A dictionary of keyword arguments passed to the ``decorator_method`` callable.

    :type criteria: Callable -> Boolean
    :type decorator_method: Callable -> Callable
    :type decorator_args: tuple
    :type decorator_kwargs: dict

    """
    # Double check the attribute validity
    if not (callable(criteria)):
        raise TypeError('criteria is not callable')

    if not (callable(decorator_method)):
        raise TypeError('decorator_method is not callable')

    if decorator_args is None:
        decorator_args = ()

    if decorator_kwargs is None:
        decorator_kwargs = {}

    # noinspection PyProtectedMember
    def _iter_method_data(cls_):
        """Helper method to iterate around the data for each method """
        for method_name, test_data in cls_._RTF_METHODS.items():
            yield method_name, test_data['index'], test_data[
                'test_data'], getattr(cls_, method_name)

    def class_wrapper(cls):
        """ Function returned by the decorator to wrap the class
            :param cls: An instance of the GenerateTestMethods class
        """

        # Check the validity of the call arguments
        if not hasattr(cls, '_RTF_DECORATED'):
            raise TypeError(
                'Incorrect usage; DecorateTestMethod can only be used to '
                'decorate a TestCase class which is already decorated '
                'by GenerateTestMethods')

        for name, index, data, method in _iter_method_data(cls):

            # Create a temp dictionary to allow unpacking of test data dictionary
            # Unpacking within the dictionary initialiser is allowed in Py3 - but having
            # a separate code segment of Py3 is overkill.
            criteria_data = {'index': data}
            criteria_data.update(**data)

            if criteria(data):
                if decorator_args or decorator_kwargs:
                    new_method = decorator_method(
                        *decorator_args,
                        **decorator_kwargs)(method)
                else:
                    new_method = decorator_method(method)

                new_method.__name__ = name
                new_method.__doc__ = method.__doc__
                setattr(cls, name, new_method)
        return cls

    return class_wrapper


# --------------------------------------------------------------------------
# A set of shortcuts for common test method decorators
#
# skip - skip decorator of methods based on test data
# skipIf - skipIf decorator of methods based on test data
# skipUnless - skipUnless decorator of methods based on test data
# expectedFailure  - expectedFailure decorator of methods based on test data
#

def skip(reason, criteria=lambda test_data: True):
    """Shortcut Decorator to allow skip decorator of methods based on test data

    :param reason: the reason string to be passed to the decorator
    :param criteria: A callable which will return True if a given method should be decorated. This is the same as the criteria attribute to the DecorateTestMethod. By default all methods will be skipped.

    :type reason: str
    :type criteria: callable(dict) -> bool
    """
    return DecorateTestMethod(criteria=criteria,
                              decorator_method=unittest.skip,
                              decorator_kwargs={'reason': reason})


# noinspection PyPep8Naming
def skipIf(condition, reason, criteria=lambda test_data: True):
    """Shortcut Decorator to allow skipIf decorator of methods based on test data

    :param condition: Skip the decorated test if condition is true
    :param reason: the reason string to be passed to the decorator
    :param criteria: A callable which will return True if a given method should be decorated. This is the same as the criteria attribute to the DecorateTestMethod. By default all methods will be skipped.

    :type condition: bool
    :type reason: str
    :type criteria: callable(dict) -> bool
    """
    if condition:
        return DecorateTestMethod(criteria=criteria,
                                  decorator_method=unittest.skip,
                                  decorator_kwargs={'reason': reason})
    else:
        return lambda x: x


# noinspection PyPep8Naming
def skipUnless(condition, reason, criteria=lambda test_data: True):
    """Shortcut Decorator to allow skipunless decoration based on test data

    :param condition: Skip the decorated test unless the condition is true
    :param reason: the reason string to be passed to the decorator
    :param criteria: A callable which will return True if a given method should be decorated. This is the same as the criteria atrribute to the DecorateTestMethod. By default all methods will be decorated

    :type condition: bool
    :type reason: str
    :type criteria: callable(dict) -> bool
    """
    if not condition:
        return DecorateTestMethod(criteria=criteria,
                                  decorator_method=unittest.skip,
                                  decorator_kwargs={'reason': reason})
    else:
        return lambda x: x


# noinspection PyPep8Naming
def expectedFailure(criteria=lambda test_data: True):
    """Shortcut allow expectedFailure to decorate methods based on test data

    :param criteria: A callable which will return True if a given method should be decorated. This is the same as the criteria atrribute to the DecorateTestMethod. By default all methods will be skipped

    :type criteria: callable(dict) -> bool
    """
    return DecorateTestMethod(criteria=criteria,
                              decorator_method=unittest.expectedFailure)
