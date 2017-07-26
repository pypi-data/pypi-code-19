from behave import *
from lib import descriptor_CLI_interfaces

use_step_matcher("parse")


@when("we run {} from descriptor_CLI_interfaces")
def step_impl(context, function):
    """
    :type context: behave.runner.Context
    """
    result = getattr(descriptor_CLI_interfaces, function)(context.parser)