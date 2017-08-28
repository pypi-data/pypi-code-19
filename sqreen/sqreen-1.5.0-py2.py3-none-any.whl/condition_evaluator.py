# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Condition Evaluator
"""

import operator

from logging import getLogger

from .binding_accessor import BindingAccessor
from .exceptions import SqreenException
from .utils import is_string


LOGGER = getLogger(__name__)


class ConditionValueError(SqreenException):
    """ Exception raised when the condition is invalid
    """


class ConditionRecursionError(SqreenException):
    """ Exception raised when the condition is too deeply nested
    """


def hash_value_includes(value, iterable, min_value_size, max_iterations=1000):
    """ Tries to find if a string value includes one of the deeply nested
    iterable values. The iterable could be composed of dict / list or a
    combination of the two.
    The min_value_size is used to avoid comparison on small strings. For example
    there is no possible SQL injection below 8 characters.
    """
    iteration = 0

    # Early stop
    if iterable is None:
        return False

    if isinstance(iterable, dict):
        remaining_iterables = list(iterable.values())
    else:
        remaining_iterables = iterable

    while len(remaining_iterables) != 0:

        iteration += 1
        # If we have a very big or nested iterable, returns True and execute the
        # rule
        if iteration >= max_iterations:
            return True

        iterable_value = remaining_iterables.pop(0)

        # If we get an iterable, add it to the list of remaining
        if isinstance(iterable_value, dict):
            remaining_iterables.extend(list(iterable_value.values()))
        elif isinstance(iterable_value, list):
            remaining_iterables.extend(iterable_value)
        else:
            # Check the value
            if not is_string(iterable_value):
                iterable_value = str(iterable_value)

            if len(iterable_value) < min_value_size:
                continue

            if iterable_value in value:
                return True

    return False


def hash_key_includes(patterns, iterable, min_value_size, max_iterations=1000):
    """ Tries to find if, in a nested object composed of dict and lists, one
    dict key is in the list of patterns. The min_value_size is used to avoid
    comparison on small strings. For example there is no possible Mongo
    injection below 1 characters.
    """
    iteration = 0

    # Early stop
    if not isinstance(iterable, dict):
        return False

    remaining_iterables = [iterable]

    while len(remaining_iterables) != 0:

        iteration += 1
        # If we have a very big or nested iterable, returns True and execute the
        # rule
        if iteration >= max_iterations:
            return True

        iterable_value = remaining_iterables.pop(0)

        if not iterable_value:
            continue

        if isinstance(iterable_value, list):
            remaining_iterables.extend(list(iterable_value))
        elif isinstance(iterable_value, dict):
            # Process the keys
            for key, value in iterable_value.items():

                if isinstance(value, dict):
                    remaining_iterables.extend(list(iterable_value.values()))
                elif isinstance(value, list):
                    remaining_iterables.extend(value)
                else:
                    if len(key) > min_value_size:
                        if key in patterns:
                            return True
    return False


def and_(*args):
    """ Return the bool value of and between all values
    """
    return all(args)


def or_(*args):
    """ Return the bool value of or between all values
    """
    return any(args)


OPERATORS = {
    "%and": and_,
    "%or": or_,
    "%equals": operator.eq,
    "%not_equals": operator.ne,
    "%gt": operator.gt,
    "%gte": operator.ge,
    "%lt": operator.lt,
    "%lte": operator.le,
    "%include": operator.contains,
    "%hash_val_include": hash_value_includes,
    "%hash_key_include": hash_key_includes
}

OPERATORS_ARITY = {
    "%equals": 2,
    "%not_equals": 2,
    "%gt": 2,
    "%gte": 2,
    "%lt": 2,
    "%lte": 2,
    "%include": 2,
    "%hash_val_include": 3,
    "%hash_key_include": 3
}


def is_condition_empty(condition):
    """ Returns True if the condition is no-op

    >>> is_condition_empty(None)
    True
    >>> is_condition_empty(True)
    False
    >>> is_condition_empty(False)
    False
    >>> is_condition_empty({})
    True
    >>> is_condition_empty({"%and": ["true", "true"]})
    False
    """
    if condition is None:
        return True
    elif isinstance(condition, bool):
        return False
    elif isinstance(condition, dict):
        return len(condition) == 0
    else:
        LOGGER.warning("Invalid pre condition type %r", condition)
        return True


def compile_condition(condition, level):
    """ Compile a row condition, replace values by BindingAccessor
    and check operators validity and arity.
    """
    if level <= 0:
        raise ConditionRecursionError("Compile went too deep")

    if isinstance(condition, bool):
        return condition

    compiled = {}

    for _operator, values in condition.items():

        # Check operator validity
        if _operator not in OPERATORS:
            raise ConditionValueError('Unkown operator {}'.format(_operator))

        # Check operator arity
        if len(values) != OPERATORS_ARITY.get(_operator, len(values)):
            msg = 'Bad arity for operator {}: {}'
            raise ConditionValueError(msg.format(_operator, len(values)))

        # Check types
        if not isinstance(values, list):
            msg = "Values should be an array (was {})"
            raise ConditionValueError(msg.format(type(values)))

        compiled_values = []
        for value in values:
            if isinstance(value, bool):
                compiled_values.append(value)
            elif isinstance(value, dict):
                compiled_values.append(compile_condition(value, level - 1))
            elif is_string(value):
                compiled_values.append(BindingAccessor(value))
            else:
                compiled_values.append(BindingAccessor(str(value)))

        compiled[_operator] = compiled_values

    return compiled


def resolve_and_evaluate(condition, level, **kwargs):
    """ Take a compiled condition, resolve values and evaluate the result
    """
    resolved = resolve(condition, level, **kwargs)
    result = evaluate(resolved)
    return result


def resolve(condition, level, **kwargs):
    """ Takes a condition with BindingAccessor and resolve them
    """
    if level <= 0:
        raise ConditionRecursionError("Resolve went too deep")

    if isinstance(condition, bool):
        return condition

    resolved = {}

    for _operator, values in condition.items():

        resolved_values = []

        for value in values:

            if isinstance(value, bool):
                resolved_values.append(value)
            elif isinstance(value, dict):
                resolved_values.append(resolve_and_evaluate(value, level - 1,
                                                            **kwargs))
            else:
                resolved_values.append(value.resolve(**kwargs))

        resolved[_operator] = resolved_values

    return resolved


def evaluate(resolved_condition):
    """ Evaluate a resolved condition
    """
    if isinstance(resolved_condition, bool):
        return resolved_condition

    elif isinstance(resolved_condition, dict):

        result = True

        # Implicit and between operators
        for operator_name, values in resolved_condition.items():
            operator_callable = OPERATORS[operator_name]

            result = result and operator_callable(*values)

            # Break early
            if result is False:
                return result

        return result
    else:
        msg = "Invalid condition type: {!r}"
        raise ConditionValueError(msg.format(resolved_condition))


class ConditionEvaluator(object):
    """ Evaluate a condition, resolving literals using BindingAccessor.
     {"%and": ["true", "true"]} -> true
     {"%or": ["true", "false"]} -> true
     {"%and": ["false", "true"]} -> false
     {"%equal": ["coucou", "#.args[0]"]} -> "coucou" == args[0]
     {"%hash_val_include": ["toto is a small guy", "#.request_params", 0]} ->
          true if one value of request params in included
          in the sentence 'toto is a small guy'.
    Combine expressions:
     { "%or":
       [
         {"%hash_val_include": ["AAA", "#.request_params", 0]},
         {"%hash_val_include": ["BBB", "#.request_params", 0]},
       ]
     }
    will return true if one of the request_params include either AAA or BBB.
    """

    def __init__(self, condition):
        self.raw_condition = condition
        self.compiled = compile_condition(condition, 10)

    def evaluate(self, **kwargs):
        """ Evaluate the compiled condition and return the results
        """
        return resolve_and_evaluate(self.compiled, level=10, **kwargs)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.raw_condition)
