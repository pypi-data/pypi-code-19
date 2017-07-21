# encoding: utf-8

u"""
============================================================
Changes the endpoint by replacing the value
in 'filter' with the value in 'parameters'.
------------------------------------------------------------
Filter: original endpoint e.g. www.google.co.uk
Parameters: new endpoint e.g. maps.google.co.uk
------------------------------------------------------------
"""

import logging_helper

logging = logging_helper.setup_logging()


def modify(uri,
           parameters):

    original_endpoint = parameters.filter
    new_endpoint = (parameters.override
                    if parameters.override
                    else parameters.params)

    uri = uri.replace(original_endpoint,
                      new_endpoint)

    return uri
