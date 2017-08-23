import os
import esig
import unittest


# Two global variables, providing information on where the test modules are to be found,
# and the naming convention for the modules.
TEST_MODULE_ROOT = os.path.join(esig.ESIG_PACKAGE_ROOT, 'tests')
TEST_MODULE_PATTERN = 'test*.py'


def get_suite():
    """
    Constructs and returns a Python unittest suite object.
    This can be used to run the unit tests for ESig.
    
    Args:
        None
    
    Returns:
        suite: A Python unittest suite, referring to all tests specified within the tests package.
    
    """
    loader = unittest.TestLoader()
    
    # The test suite is constructed from all modules matching the filename pattern specified by TEST_MODULE_PATTERN.
    # All modules are to be found in TEST_MODULE_ROOT.
    suite = loader.discover(TEST_MODULE_ROOT, pattern=TEST_MODULE_PATTERN)
    return suite


def run_tests(output_path=None):
    """
    Acquires the ESig test suite, and runs the tests.
    The test log can be optionally saved to a file; provide a string to the file you wish to save to as output_path.
    
    Args:
        output_path: Optional. A string representing the path to which the output log should be saved.
    
    Returns:
        None
    """
    f = None

    if output_path is not None:
        f = open(output_path, 'w')
    
    esig_test_suite = get_suite()

    runner = unittest.TextTestRunner(f)
    runner.run(esig_test_suite)
    
    if output_path is not None:
        f.close()