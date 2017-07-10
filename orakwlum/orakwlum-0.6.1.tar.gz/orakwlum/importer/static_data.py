# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

from ..input import Message
from .importer import Importer

from enerdata.datetime.timezone import TIMEZONE
from pymongo import MongoClient

class ImporterStaticData (Importer):
    """
    StaticData Importer model
    """

    __slots__ = ('messages', 'time_config')

    def __init__(self, messages, config):
        super().__init__(message=messages, config=config)
        self.messages = messages
        self.time_config = {
            "mask": "%Y-%m-%d",
            "append": ""
            }


    def delete_static_data(self, processed_IDS):
        """
        Delete existing registries based on giscedata_polissa_modcontractual ID
        """
        assert type(processed_IDS) == list, "Processed IDs must be a list of IDs"

        filter_by_ID = {'static_data_id': { "$in":  processed_IDS } }

        self.collection.delete_many(filter_by_ID)


    def process_contracts (self):
        """
        Save static data to DB in block
        """
        # dict of processed IDs //useful to make a preventive deletion before the insertion
        static_data_IDs_list=[]

        # list of static data to insert
        static_data_list = []

        # Prepare the list that will be saved
        for message in self.messages:
            ID = message['static_data_id']
            static_data_IDs_list.append(ID)

            # Convert to datetimes the start and end dates
            message['date_start'] = TIMEZONE.localize(self.convert_string_to_datetime(message['date_start']))
            message['date_end'] = TIMEZONE.localize(self.convert_string_to_datetime(message['date_end']))

            # Append the entire message definition (the dict of static data fields)
            static_data_list.append(message.values)

        ## Delete existing Static Data entries in block
        self.delete_static_data(static_data_IDs_list)

        ## Save the new ones in block
        self.save_measures(static_data_list)
