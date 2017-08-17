# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Various constants
"""

# Constant for callback not changing the workflow
NOTHING = 'NOTHING'
RETRY = 'RETRY'


LIFECYCLE_METHODS = {
    "PRE": "pre",
    "POST": "post",
    "FAILING": "failing"
}

ACTIONS = {
    "RAISE": "raise",
    "OVERRIDE": "override",
    "RETRY": "retry",
    "MODIFY_ARGS": "modify_args"
}


VALID_ACTIONS_PER_LIFECYCLE = {
    LIFECYCLE_METHODS["PRE"]: [
        ACTIONS["RAISE"],
        ACTIONS["OVERRIDE"],
        ACTIONS["MODIFY_ARGS"]],
    LIFECYCLE_METHODS["FAILING"]: [
        ACTIONS["RAISE"],
        ACTIONS["RETRY"],
        ACTIONS["OVERRIDE"]],
    LIFECYCLE_METHODS["POST"]: [
        ACTIONS["RAISE"],
        ACTIONS["OVERRIDE"]
    ]
}
