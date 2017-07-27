from behave import *
from mock import *
from lib import manipulation
from lib.inputoutput import *
from io import StringIO

use_step_matcher("parse")

@when("we run {} from manipulation")
def step_impl(context, function):
    """
    :param function:
    :type context: behave.runner.Context
    """
    with patch.object(ParseVectors, 'parse') as mock_method:
        mock_method.return_value = context.matrix
        result = getattr(manipulation, function)(context.parser)

    assert mock_method.called


@when("we run {} from manipulation with STDIN")
def step_impl(context, function):
    """
    :param function:
    :type context: behave.runner.Context
    """
    with patch("sys.stdin", StringIO(context.text_matrix)):
        result = getattr(manipulation, function)(context.parser)


'''
@when("we run {} from manipulation with STDIN and tmpfile ")
def step_impl(context, function):
    """
    :param function:
    :type context: behave.runner.Context
    """
    with patch.object(ParseVectors, 'parse') as mock_method:
        mock_method.return_value = context.matrix
        result = getattr(manipulation, function)(context.parser)
    assert mock_method.called
'''


@when("we run {} from manipulation with tmpfile")
def step_impl(context, function):
    """
    :type context: behave.runner.Context
    """
    result = getattr(manipulation, function)(context.parser)