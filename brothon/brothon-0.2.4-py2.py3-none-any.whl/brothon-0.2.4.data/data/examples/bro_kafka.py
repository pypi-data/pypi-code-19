"""FileTailer Python Class"""
from __future__ import print_function
import os
import sys
import argparse
from pprint import pprint

# Third Party imports
from kafka import KafkaConsumer

if __name__ == '__main__':
    # Example to consume Bro Kafka plugin messages

    # Collect args from the command line
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--topic', type=str, default='http', help='Specify the Kafka Topic to consume')
    args, commands = parser.parse_known_args()

    # Check for unknown args
    if commands:
        print('Unrecognized args: %s' % commands)
        sys.exit(1)

    # Create the Kafka consumer
    # consumer = KafkaConsumer(args.topic, bootstrap_servers=['localhost:9092'],
    #                          auto_offset_reset='earliest')
    consumer = KafkaConsumer(args.topic, bootstrap_servers=['localhost:9092'])
    for message in consumer:
        print(message)
