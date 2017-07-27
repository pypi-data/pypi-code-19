from behave import *
from lib import graph
use_step_matcher("parse")


@when("we run {} from graph")
def step_impl(context, function):
    """
    :type context: behave.runner.Context
    """
    result = getattr(graph, function)(context.parser)

