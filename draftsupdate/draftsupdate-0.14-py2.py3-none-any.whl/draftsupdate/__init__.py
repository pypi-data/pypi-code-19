#! /usr/bin/env python

# coding: utf-8

# In[1]:

import boto3
import sys
from datetime import datetime 
from datetime import timedelta
import requests
import json
import urllib2
import argparse
import getpass
from botocore.exceptions import ClientError

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

def main():

    parser = argparse.ArgumentParser()
    
    parser.add_argument('--aws_access_key_id', required=True, dest='aws_access_key_id')
    parser.add_argument('--aws_secret_access_key', required=True, dest='aws_secret_access_key') 
    
    aws_args = parser.parse_args()

    email = raw_input('Email:')
    password = getpass.getpass("Password for " + email + ":")

    month_ago = datetime.now() - timedelta(days = 30)
    month_ago_2 = month_ago - timedelta(days = 30)
    month_minus_hour = month_ago - timedelta(hours = 1)

    month_ago_string = month_ago.strftime("%Y-%m-%dT%H:%M:%S")
    month_ago_2_string = month_ago_2.strftime("%Y-%m-%dT%H:%M:%S")
    month_minus_hour_string = month_minus_hour.strftime("%Y-%m-%dT%H:%M:%S")


    regions = ['us-west-1', 'us-west-2', 'us-east-1', 'us-east-2']
    instance_types = ['m4.large']

    metadata = {'end-time': month_ago_string, 'start-time': month_minus_hour_string}
    results = {'metadata': metadata}
    spot_instance_data = {}

    try:
        for region in regions:
            spot_instance_data[region] = {}
            for instance_type in instance_types:
                client = boto3.client('ec2', region_name=region,
                             aws_access_key_id = aws_args.aws_access_key_id,
                             aws_secret_access_key = aws_args.aws_secret_access_key)
                pag = client.get_paginator('describe_spot_price_history')
                params = {'EndTime': month_ago_string, 'StartTime': month_minus_hour_string, 
                        'InstanceTypes': [instance_type], 'ProductDescriptions': ['Linux/UNIX']}
                iterator = pag.paginate(**params)
                result = get_by_az(get_by_instance_type(get_spot_prices(iterator))[instance_type])
                spot_instance_data[region][instance_type] = result
                sys.stdout.flush()
                sys.stdout.write("\r" + region + ": " + instance_type)

        results['spot-instance-data'] = spot_instance_data

        jwt_response = requests.post('http://localhost:8080/login', json = { 'auth': { 'email': email, 'password': password } } )

        try:
            jwt = jwt_response.json()['jwt']

            headers = {'Authorization' : 'Bearer ' + jwt}

            response = requests.post('https://predictspotprice.cs.ucsb.edu/upload', json = results, headers = headers);

            success = response.json()['success']

            if success:
                print("\nSuccessfully updated!")
            else:
                print("\nSomething went wrong. As this feature is experimental we have made a note and will notify you when we have determined the cause.")

        except ValueError:
            print("\nIncorrect DrAFTS credentials")

    except (ClientError):
        print("Invalid AWS credentials")

if __name__ == "__main__":
    main()
