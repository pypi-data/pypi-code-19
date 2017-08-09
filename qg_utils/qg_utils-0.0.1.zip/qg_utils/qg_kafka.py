'''
module for qg_kafka
Class: QGKafkaConsumer
    It inherits from KafkaConsumer and used to stop repeated consumtion
    of messages from kafka queue.
    It stores offset of last 1000 messages from kafka and
    if current message is present in list of previsous 1000
    we skip the message and writes message in stderr file
'''
from __future__ import print_function
import sys
import time
from kafka import KafkaConsumer

class QGKafkaConsumer(KafkaConsumer):
    ''' Class for QGKafkaConsumer '''
    def __init__(self, *args, **kwargs):
        '''
        constructor for QGKafkaConsumer
        It is same as that of KafkaConsumer
        only one difference is that it stores offset of last 1000 messages
        in a dict which maps offset to time when offset was consumed first time
        Param: self.consumed_offsets_to_time
                mapping from offset to time when it was consumed first
        '''
        super(QGKafkaConsumer, self).__init__(*args, **kwargs)
        if 'offset_store_limit' in kwargs:
            self.offset_store_limit = kwargs['offset_store_limit']
        else:
            self.offset_store_limit = 1000 # default is 1000
        self.consumed_offsets_to_time = {}

    def __next__(self):
        '''
        implementing __next__ such that if a message is repeats
        we will catch it and write it to stderr
        '''
        while True:
            message = super(QGKafkaConsumer, self).__next__()
            curr_offset = message.offset
            if curr_offset in self.consumed_offsets_to_time:
                previous_time = self.consumed_offsets_to_time[curr_offset]
                err_message = 'Repeat offset [ {} ] at time [ {} ]'.format(curr_offset, time.time())
                err_message += ' first consumption was at [ {} ]'.format(previous_time)
                print(err_message, file=sys.stderr)
            else:
                if len(self.consumed_offsets_to_time) > self.offset_store_limit:
                    self.consumed_offsets_to_time = {}
                self.consumed_offsets_to_time[curr_offset] = time.time()
                return message
