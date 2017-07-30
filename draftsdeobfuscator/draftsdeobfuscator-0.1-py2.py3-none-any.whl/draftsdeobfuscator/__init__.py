#! /usr/bin/env python

import boto3
import sys
from datetime import datetime 
from datetime import timedelta
import requests
import pickle
import json
import urllib2
import argparse
import os
import math

def get_spot_prices(iterator):
    spot_prices = []
    for page in iterator:
        for spotdata in page['SpotPriceHistory']:
            spot_prices.append(spotdata)
    return spot_prices

def get_by_instance_type(spot_prices):
    by_instance_types = {}
    for sp in spot_prices:
        instance_type_data = by_instance_types.get(sp['InstanceType'], [])
        instance_type_data.append(sp)
        by_instance_types[sp['InstanceType']] = instance_type_data
    return by_instance_types

def get_by_az(instance_type_data):
    by_az = {}
    for data_point in instance_type_data:
        data_point['Timestamp'] = data_point['Timestamp'].strftime("%Y-%m-%dT%H:%M:%S")
        az_point = by_az.get(data_point['AvailabilityZone'], [])
        az_point.append(data_point)
        by_az[data_point['AvailabilityZone']] = az_point
    return by_az

def compare(res1, res2):
    results = {}
    for az1 in res1.keys():
        data_points1 = res1[az1]
        result = {}
        for az2 in res2.keys():
            data_points2 = res2[az2]
            matches = 0
            for dp1 in data_points1: 
                for dp2 in data_points2:
                    if (dp1['SpotPrice'] == dp2['SpotPrice'] and
                        dp1['Timestamp'] == dp2['Timestamp']):
                        matches += 1
            result[az2] = matches / float(len(data_points1))
        results[az1] = result
    return results

def main():
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--start_time', required=True, dest='start_time')
    parser.add_argument('--end_time', required=True, dest='end_time')
    parser.add_argument('--spot_instance_data', required=True, dest='spot_instance_data')

    args = parser.parse_args()

    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']

    month_ago_string = args.end_time
    month_ago_minus_hour_string = args.start_time

    user_spot_instance_data = json.loads(args.spot_instance_data)

    regions = ['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2']
    instance_types = ['m4.large']

    my_spot_instance_data = {}

    for region in regions:
        my_spot_instance_data[region] = {}
        for instance_type in instance_types:
            client = boto3.client('ec2', region_name=region,
                         aws_access_key_id = aws_access_key_id,
                         aws_secret_access_key = aws_secret_access_key)
            pag = client.get_paginator('describe_spot_price_history')
            params = {'EndTime': month_ago_string, 'StartTime': month_ago_minus_hour_string, 
                    'InstanceTypes': [instance_type], 'ProductDescriptions': ['Linux/UNIX']}
            iterator = pag.paginate(**params)
            result = get_by_az(get_by_instance_type(get_spot_prices(iterator))[instance_type])
            my_spot_instance_data[region][instance_type] = result

    
    for region in my_spot_instance_data.keys():
        for instance_type in my_spot_instance_data[region].keys():

            r = compare(my_spot_instance_data[region][instance_type], user_spot_instance_data[region][instance_type])

            for my_az in r.keys():
                user_azs = r[my_az]
                cur_score = float('-inf')
                cur_az = None
                for user_az in user_azs.keys():
                    score = user_azs[user_az]
                    if score > cur_score:
                        cur_score = score
                        cur_az = user_az
                print(my_az + " " +  cur_az)
    
