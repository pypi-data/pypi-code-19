# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Callbacks rules classes and helpers
"""
import logging
from functools import wraps

from .runtime_infos import runtime

LOGGER = logging.getLogger(__name__)


def check_condition_wrapper(rule_data, function, condition, lifecycle):
    """ Wrapper that will check lifecycle method pre-condition before
    calling it.
    If pre-conditions are true, call the lifecycle method, otherwise
    return None.
    """

    @wraps(function)
    def wrapped(*args, **kwargs):
        """ Wrapper around lifecycle method
        """

        # Copy args to work on them
        binding_args = list(args)

        # Compute return value depending on the lifecycle method we wrap
        return_value = False
        if lifecycle in ('post', 'failing'):
            # Args[1] is either the return value of the hooked point
            # or the exception
            return_value = binding_args.pop(1)

        original = binding_args.pop(0)

        binding_eval_args = {
            "binding": locals(),
            "global_binding": globals(),
            "framework": runtime.get_current_request(),
            "instance": original,
            "arguments": binding_args,
            "cbdata": rule_data,
            "return_value": return_value
        }

        # Check the pre condition
        condition_result = condition.evaluate(**binding_eval_args)

        LOGGER.debug("ConditionWrapper (%s) result for %s: %s", condition, function, condition_result)

        if condition_result in (False, None):
            return None

        # Execute the hook otherwise with the original args
        return function(*args, **kwargs)

    wrapped.__wrapped__ = function

    return wrapped
