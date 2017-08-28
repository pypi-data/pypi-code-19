# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Binding accessor filters
"""


def flat_keys(iterable, max_iterations=1000):
    """ Returns keys of iterable and nested iterables
    """
    iteration = 0

    keys = []
    remaining_iterables = [iterable]

    seen_iterables = set()

    while len(remaining_iterables) != 0:

        iteration += 1
        # If we have a very big or nested iterable, returns False
        if iteration >= max_iterations:
            break

        iterable_value = remaining_iterables.pop(0)

        # Protection against recursive objects
        if id(iterable_value) in seen_iterables:
            continue

        seen_iterables.add(id(iterable_value))

        # If we get an iterable, add it to the list of remaining
        if isinstance(iterable_value, dict):
            dict_values = iterable_value.values()

            # Be sure to not extend with an empty dict, faster check
            if len(dict_values) > 0:
                remaining_iterables.extend(list(dict_values))

            dict_keys = iterable_value.keys()

            if len(dict_keys) > 0:
                keys.extend(dict_keys)

        elif isinstance(iterable_value, list):
            # Be sure to not extend with an empty list, faster check
            if len(iterable_value) > 0:
                remaining_iterables.extend(iterable_value)

    return keys


def flat_values(iterable, max_iterations=1000):
    """ Returns values of iterable and nested iterables
    """
    iteration = 0

    values = []
    remaining_iterables = [iterable]

    seen_iterables = set()

    while len(remaining_iterables) != 0:

        iteration += 1
        # If we have a very big or nested iterable, returns False
        if iteration >= max_iterations:
            break

        iterable_value = remaining_iterables.pop(0)

        # Protection against recursive objects
        if id(iterable_value) in seen_iterables:
            continue

        seen_iterables.add(id(iterable_value))

        # If we get an iterable, add it to the list of remaining
        if isinstance(iterable_value, dict):
            dict_values = iterable_value.values()

            # Be sure to not extend with an empty dict, faster check
            if len(dict_values) > 0:
                remaining_iterables.extend(list(dict_values))

        elif isinstance(iterable_value, list):
            # Be sure to not extend with an empty list, faster check
            if len(iterable_value) > 0:
                remaining_iterables.extend(iterable_value)
        else:
            values.append(iterable_value)

    return values
