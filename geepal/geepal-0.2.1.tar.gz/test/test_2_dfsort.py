#!/usr/bin/env python

# __author__ = "Eric Allen Youngson"
# __email__ = "eric@successionecological.com"
# __copyright__ = "Copyright 2015, Succession Ecological Services"
# __license__ = "GNU Affero (GPLv3)"

""" This module provides functions for requesting results from the Google
    calendar API """


from datetime import datetime, date, timedelta
from pyinvoice.models import InvoiceInfo, ServiceProviderInfo, ClientInfo, Item, Transaction
from pyinvoice.templates import SimpleInvoice

import time
import iso8601
import pandas as pd
import pprint as pp

import sys
sys.path.append('../geepal')
import get_events as ge
import dfsort as dfs

import pytest


def test_add_durations():
    """ """

    pass


def test_hrs_min_sec():
    """ """

    pass


def test_get_cals_durs():
    """ """

    pass


def test_summarize_cals_durs():
    """ """

    pass


def test_get_unique_events():
    """ """

    pass


def test_get_projects():
    """ """

    pass


def test_invoice_dict():
    """  """

    evStartEvEnd_calEvDfsDct = dfs.add_durations(ge.main())
    eventTypesDct = dfs.get_unique_events(evStartEvEnd_calEvDfsDct, 'Billing')
    invoiceItemsDct = dfs.invoice_dict(eventTypesDct, 'Bullitt')

    #invoiceItemsDct = {'Project1' : {'0': {'duration': 2, 'description': 'Work'},
    #                                 '1': {'duration': 1.5, 'description': 'Some other work'}},
    #                   'Project2' : {'2': {'duration': 2, 'description': 'Work'},
    #                                 '3': {'duration': 1.5, 'description': 'Some other work'}}
    #                  }

    assert type(invoiceItemsDct) is dict
    for key1, value1 in invoiceItemsDct.items():
        assert type(value1) is dict
        for key in value1.keys():
            assert type(key) is str
        for key2, value2 in value1.items():
            assert type(value2) is dict
            assert len(value2) is 2
            assert key2 is 'description' or 'duration'
