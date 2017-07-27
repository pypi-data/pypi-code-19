from behave import *
from lib.inputoutput import ParseVectors, outputvector
use_step_matcher("parse")


@when("we read in the {} file")
def step_impl(context, file):
    """
    :type context: behave.runner.Context
    """
    context.vecparse = ParseVectors(file_name=getattr(context, file))
    context.matrix = context.vecparse.parse()


@step("print it")
def step_impl(context):
    """
    :type context: behave.runner.Context
    """
    outputvector(context.matrix)
