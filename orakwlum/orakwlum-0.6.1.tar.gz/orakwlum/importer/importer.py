# -*- coding: utf-8 -*-
__author__ = 'XaviTorello'

from ..input import Message
from datetime import datetime

#import time
from pymongo import MongoClient

class Importer (object):
    """
    Importer model
    """

    __slots__ = ('message', 'time_config', 'server_config', 'collection')

    def __init__(self, message, config):
        assert isinstance(message, Message) or type(message) == list, "Message must be an instance of Message or a list of Messages"
        assert type(config) == dict, "Config must be a dict"

        assert "host" in config, "Config must have a host"
        assert "db" in config, "Config must have a DB"
        assert "port" in config, "Config must have a port"
        assert "collection" in config, "Config must have a collection"

        self.message = message
        self.time_config = {
            "mask": "%Y-%m-%d %H",
            "append": " 0"
            }

        client = MongoClient('{}:{}'.format(config['host'], config['port']))
        db = client[config['db']]
        self.collection = db[config['collection']]
        self.server_config = config


    def convert_string_to_datetime(self, string):
        """
        Convert an string to a datetime
        """
        return datetime.strptime(string + self.time_config['append'], self.time_config['mask'])


    def delete_measures(self, processed_cups):
        """
        Delete existing registries based on a range hours and a CUPS
        """


        ## Iterate all processed cups and delete it hours range
        for cups, hours in processed_cups.items():
            start = hours['hour_start']
            end = hours['hour_end']
            filter_by_dates = {'hour': {'$gte': start, '$lte': end}, 'CUPS': cups}

            print ("Delete from {}:".format(self.server_config['db']))
            print (filter_by_dates)

            #x = self.collection.find(filter_by_dates).count()
            #print (x)

            self.collection.remove(filter_by_dates)

            #x = self.collection.find(filter_by_dates).count()
            #print (x)


    def save_measures(self, measures_list):
        #start_time = time.time()
        self.collection.insert_many(measures_list)
        #print("Insert to DB (pymongo): %s seconds" % (time.time() - start_time))
