from behave import *
from mock import patch
from lib import analysis
from lib.analysis import *

use_step_matcher("parse")


@given(u'a {:d}x{:d} matrix with zeros')
def step_impl(context, rows, cols):
    """
    :param cols:
    :param rows:
    :type context: behave.runner.Context
    """
    context.matrix = np.zeros((rows, cols))
    context.rows = None
    context.cols = None
    context.return_type = None


@when(u'we run {} from analysis')
def step_impl(context, function):
    """
    :param function:
    :type context: behave.runner.Context
    """
    with patch.object(ParseVectors, 'parse') as mock_method:
        mock_method.return_value = context.matrix
        result = getattr(analysis, function)(context.parser)
    assert mock_method.called


@then("there should be {:d} zeros on the console")
def step_impl(context, times):
    """
    :param times:
    :type context: behave.runner.Context
    """
    #print(context.stdout_capture.getvalue())
    assert context.stdout_capture.getvalue().count('0.0') == times


@given("a {:d}x{:d} diag matrix with {:d}")
def step_impl(context,rows, cols, value):
    """
    :type context: behave.runner.Context
    """
    matrix = np.ones((rows, cols))
    matrix * value
    context.matrix = np.diag(np.diag(matrix))
    context.rows = None
    context.cols = None
    context.return_type = None


@then("there should be {} {:d} times on the console")
def step_impl(context, value, times):
    """
    :type context: behave.runner.Context
    """
    assert context.stdout_capture.getvalue().count(value) == times


@given("a {} matrix")
def step_impl(context, array_type):
    """
    :type context: behave.runner.Context
    """
    matrix = []
    rows = context.text.split("\n")
    for i in rows:
        matrix.append(i.split(" "))
    matrix = np.array(matrix)
    context.matrix = matrix.astype(array_type)


@then("there should be {} on the console")
def step_impl(context, text):
    """
    :type context: behave.runner.Context
    """

    assert context.stdout_capture.getvalue().count(text) >= 1


@then("there should be a {} on column {:d}")
def step_impl(context, text, column):
    """
    :type context: behave.runner.Context
    """
    output = context.stdout_capture.getvalue()
    col_x = list()
    for line in output.split("\n"):
        if len(line.split()) > 0:
            col_x.append(line.split()[column - 1])
    result = False
    for i in col_x:
        if text in i:
            result = True
    assert result



@when("we run {} from analysis with tmpfile")
def step_impl(context, function):
    """
    :type context: behave.runner.Context
    """
    result = getattr(analysis, function)(context.parser)