from behave import *
from lib import normalization
use_step_matcher("parse")


@when("we run {} from normalization")
def step_impl(context, function):
    """
    :type context: behave.runner.Context
    """
    result = getattr(normalization, function)(context.parser)

