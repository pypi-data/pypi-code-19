# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

from ..input import Message
from .importer import Importer

from enerdata.profiles.profile import Profile
from enerdata.contracts.tariff import *
from enerdata.datetime.timezone import TIMEZONE

from datetime import datetime
#import time

class ImporterF1 (Importer):
    """
    ImporterF1 model for F1 processing
    """

    __slots__ =  ('message', 'time_config')

    def __init__(self, message, config):
        super().__init__(message=message,config=config)
        self.time_config = {
            "mask": "%Y-%m-%d %H",
            "append": " 0"
            }

    def generate_consumptions (self):
        """
        Estimate hourly measures using a CUPS, a Tariff and a range of dates
        """
        #start_time = time.time()

        all_estimations=[]

        # Fetch and instance the related Tariff class
        tariff = (get_tariff_by_code(self.message['tariff']))()

        # Prepare the localized hours
        start_hour = TIMEZONE.localize(self.convert_string_to_datetime(self.message['date_start']))
        end_hour = TIMEZONE.localize(self.convert_string_to_datetime(self.message['date_end']))

        estimation = None
        # If type is "Anuladora" or "Anuladora+Rectificadora" don't profile anything
        if (self.message['invoice_type'] != 2):

            # Fetch the energy periods to compute
            periods = tariff.energy_periods

            # Fetch measures for each period
            total_by_period = eval(self.message['measures'])


            # Create the base profile and estimate it
            measures = []
            profile = Profile(start_hour, end_hour, measures)
            estimation = profile.estimate(tariff, total_by_period)
            #print("Generate consumptions: %s seconds" % (time.time() - start_time))

        return {
            "start_hour": start_hour,
            "end_hour": end_hour,
            "estimation": estimation
        }

    def process_measures (self):
        """
        Save measures to DB in block (this F1 related hours for this CUPS)
        """
        generated_consumptions = self.generate_consumptions()

        consumptions = generated_consumptions['estimation']
        start_hour = generated_consumptions['start_hour']
        end_hour = generated_consumptions['end_hour']

        # Prepare measure data
        measure_data = {
            'CUPS': self.message['cups'],
            'invoice_id': self.message['invoice_id'],
            'invoice_type': self.message['invoice_type'],
            'origin': 'F1',
            'origin_priority': 20,
            'provider_invoice_id': self.message['provider_invoice_id'],
            'original_invoice_id': self.message['original_invoice_id'],
            'date_invoice': self.message['date_invoice'],
        }

        print ()
        print ()
        print (self.message['invoice_id'])
        print ()

        # a dict of CUPS with the related start&end hours
        cups_list={}

        # insert current F1 CUPS with its min and max hours
        cups_list[self.message['cups']] = {
            "hour_start": start_hour,
            "hour_end": end_hour,
        }


        # Delete previous measures
        self.delete_measures(cups_list)


        # If type is "Anuladora" or "Anuladora+Rectificadora" don't create anything
        if (self.message['invoice_type'] != 2):
            # Prepare the list that will be saved
            measures_list = list()
            for (hour, measure, valid) in consumptions.measures:
                measure_to_append = dict(measure_data)
                measure_to_append['hour'] = hour
                measure_to_append['measure'] = float(measure)
                measures_list.append(measure_to_append)
        
            print ("Saving new measures")

            ## Save the new ones
            self.save_measures(measures_list)
