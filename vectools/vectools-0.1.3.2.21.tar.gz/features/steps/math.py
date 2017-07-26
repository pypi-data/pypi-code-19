from behave import *
from lib import mathematics

use_step_matcher("parse")


@when("we run {} from mathematics")
def step_impl(context, function):
    """
    :type context: behave.runner.Context
    """
    result = getattr(mathematics, function)(context.parser)