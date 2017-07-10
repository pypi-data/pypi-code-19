# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

from ..input import Message
from .importer import Importer

from enerdata.datetime.timezone import TIMEZONE
from pymongo import MongoClient

from datetime import datetime

from decimal import Decimal, ROUND_UP

#import time

class ImporterF5D (Importer):
    """
    Importer model
    """

    __slots__ = ('messages', 'time_config', 'unit_factor')

    def __init__(self, messages, config):
        super().__init__(message=messages,config=config)

        # From W to kW. F5D are ever in W
        self.unit_factor = Decimal(1.0/1000)

        assert type(messages) == list, "Incoming Messages must be a list"

        count = 0
        for message in messages:
            assert isinstance(message, Message), "All F5D Messages must be an instance of Message"

            # Convert W to kW using Decimal
            messages[count]['measure_converted'] = Decimal(Decimal(message['measure']) * self.unit_factor).quantize(Decimal('.01'))
            count += 1

        self.messages = messages
        self.time_config = {
            "mask": "%Y/%m/%d %H:%M",
            "append": ""
            }


    def process_measures (self):
        """
        Save measures to DB in block (all F5D entries in the messages list)
        """

        hour_start = None
        hour_end = None

        measures_list=[]

        # a dict of CUPS with the related start&end hours
        cups_list={}

        CUPS = None

        # Prepare the list that will be saved
        for message in self.messages:
            CUPS = message['cups']

            hour = TIMEZONE.localize(self.convert_string_to_datetime(message['hour']))

            # if first appearance of this CUPS
            if CUPS not in cups_list:
                # initialize values for this CUPS
                cups_list[CUPS] = {
                    "hour_start": hour,
                    "hour_end": hour,
                }

            hour_start = cups_list[CUPS]['hour_start']
            hour_end = cups_list[CUPS]['hour_end']

            # If current hour is smaller than min processed for this CUPS
            if hour < hour_start:
                cups_list[CUPS]['hour_start'] = hour

            # If current hour is bigger than max processed for this CUPS
            if hour > hour_end:
                cups_list[CUPS]['hour_end'] = hour

            measure_to_append = {
                'CUPS': message['cups'],
                'city': message['city'],
                'region': message['region'],
                'province': message['province'],
                'subsystem': message['subsystem'],
                'tariff': message['tariff'],
                'tension': message['tension'],
                'invoice_id': message['invoice_id'],
                'invoice_type': message['invoice_type'],
                'origin': 'F5D',
                'origin_priority': 10,
                'hour': hour,
                'measure': float(message['measure_converted']),
            }
            measures_list.append(measure_to_append)

        #print ("%s entries" % len(measures_list))

        ## Delete previous measures
        self.delete_measures(cups_list)

        ## Save the new ones
        self.save_measures(measures_list)
