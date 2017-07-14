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

import numpy as np

import time
import iso8601
import pandas as pd
import pprint as pp


def add_durations(evStartEvEnd_eventsDct):
    """ """

    (evStart_evEnd, eventsDct) = evStartEvEnd_eventsDct
    calEvDfsDct = {}
    calPerTots = []
    for key, value in eventsDct.items():
        evDurations = []
        events = value
        for event in events:
            dtEvEnd = iso8601.parse_date(event['end'])
            dtEvStart = iso8601.parse_date(event['start'])
            evDur = dtEvEnd - dtEvStart
            evDurations.append(evDur)
        eventDF = pd.DataFrame(events)
        eventDF['duration'] = evDurations
        calEvDfsDct[key] = eventDF
    evStartEvEnd_calEvDfsDct = (evStart_evEnd, calEvDfsDct)
    ## TODO(eayoungs): Revise name of return variable for consistency
    return  evStartEvEnd_calEvDfsDct


def hrs_min_sec(td): #Add a lambda function?
    """ """
    
    hrs = td.seconds//3600
    mins = (td.seconds//60)%60
    days = td.days*24+hrs
    # TalkPython Training - Pythonic Code: Foundational Concepts: String Formatting
    hrs_min_sec_str = "{}:{}".format(days, mins)

    return hrs_min_sec_str


def get_cals_durs(calEvDfsDct):
    """ """

    calPerTotHrsDct = {}
    for key, value in calEvDfsDct.items():
        calPerDurs = pd.Series(value['duration'])
        calPerTotHrs = sum(value['duration'], timedelta())
        calPerTotHrsDct[key] = calPerTotHrs

    return calPerTotHrsDct


def summarize_cals_durs(calPerTotHrsDct):
    """ """

    cumCalTotHrsLst = []
    for key, value in calPerTotHrsDct.items():
        cumCalTotHrsLst.append(value)
    
    sumCumCalTotHrs = sum(cumCalTotHrsLst, timedelta())
    allCalDurTotSec = sumCumCalTotHrs.total_seconds()

    colNames = ['calendar', 'hours', 'percent']
    calDursDF = pd.DataFrame()
    for key, value in calPerTotHrsDct.items():
        thisCalDurTotSec = value.total_seconds()
        thisCalDurPerc = (thisCalDurTotSec / allCalDurTotSec) * 100
        currRow = [key, hrs_min_sec(value), round(thisCalDurPerc, 1)]
        currFrame = pd.DataFrame([currRow],columns=colNames)
        calDursDF = calDursDF.append(currFrame)

    fmatSumCumCalTotHrs = hrs_min_sec(sumCumCalTotHrs)
    calDursDF_fmatSumCumCalTotHrs = (calDursDF, fmatSumCumCalTotHrs)

    return  calDursDF_fmatSumCumCalTotHrs


def get_unique_events(evStartEvEnd_calEvDfsDct, calendar):
    """ """

    (evStart_evEnd, calEvDfDct) = evStartEvEnd_calEvDfsDct
    thisCal = calEvDfDct[calendar]
    try:
        eventTypes = thisCal.summary.unique()
        eventTypesDct = {}

        for eventType in eventTypes:
            eventTypeDf = thisCal.ix[thisCal['summary']==eventType]
            eventTypesDct[eventType] = eventTypeDf

    except EventNotFoundError:
        print("No unique events found for {}".format(thisCal))

    return eventTypesDct


def get_project_events(eventTypeDf, projectNm):
    """ """

    projectDf = eventTypeDf.loc[eventTypeDf['description'].str.contains(
                                                                    projectNm)]
    #taskDf = projectDf.loc[projectDf['description'].str.contains(
    #                                                          r'- \[[^ ]\].+')]
    #taskDf.loc['item_list'] = taskDf['description'].str.findall(r'(- \[[^ ]\].+)')
    #taskDf.loc['joined'] = taskDf.item_list.apply('/n'.join)
    #invoiceDf = pd.DataFrame(taskDf[['joined', 'start', 'duration']])
    #invoiceDf['duration'] = invoiceDf['duration'].apply(hrs_min_sec)

    return projectDf


def get_marked_tasks(projectDf, regex=r'- \[[^ ]\].+'):
    """  """

    taskDf = projectDf.loc[projectDf['description'].str.contains(regex)]
    #taskDf.loc['item_list'] = taskDf['description'].str.findall(r'(- \[[^ ]\].+)')
    #taskDf.loc['joined'] = taskDf.item_list.apply('/n'.join)
    #invoiceDf = pd.DataFrame(taskDf[['joined', 'start', 'duration']])
    #invoiceDf['duration'] = invoiceDf['duration'].apply(hrs_min_sec)

    return taskDf

def invoice_dict(eventTypesDct, project):
    """ Transformss a dictionary of events, with unique names as keys, for a
        specific calendar and a 'project' name for invoicing over the period
        used tocreate the events into a dictionary for consumption by the
        ../bin/invoice.py script."""

    invoiceItemsDct = {}
    for key, value in eventTypesDct.items():
        try:
            projectDf = get_project_events(value, project)
            taskDct = {}
        except Exception as e:
            print(e)
        
        for index, row in projectDf.iterrows():
            try:
                taskDct[str(index)] = {'duration': row.loc['duration'] / np.timedelta64(1, 'h'),
                # https://stackoverflow.com/questions/31283001/get-total-number-of-hours-from-a-pandas-timedelta
                                       'description': row.loc['description'][:33]}
                invoiceItemsDct[key] = taskDct
            except Exception as e:
                print(e)

    return invoiceItemsDct


def main():
    """ """
    
    import sys
    sys.path.append('../bin')

    #import invdef
    import invoice
    import get_events as ge


    evStartEvEnd_calEvDfsDct = add_durations(ge.main())
    eventTypesDct = get_unique_events(evStartEvEnd_calEvDfsDct, 'Billing')

    invoiceItemsDct = invoice_dict(eventTypesDct, 'Bullitt')
    for key1, value1 in invoiceItemsDct.items():
        for key2, value2 in value1.items():
            print(key1, value2['description'], value2['duration'])
    #invoice.main(invoiceItemsDct)


if __name__ == '__main__':
    main()
