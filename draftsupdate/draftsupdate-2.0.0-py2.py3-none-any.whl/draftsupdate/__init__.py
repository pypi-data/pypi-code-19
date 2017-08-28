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
import os.path
from os.path import expanduser
import re

# assumes valid file
def process_aws_creds_file(creds_path, user):
    content = None
    with open(creds_path) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    users = {}
    user_is = []
    for line_i, val in enumerate(content):
        if not len(val.strip()) == 0:
            if val[0] == '[' and val[-1] == ']':
                users[val[1:-1]] = line_i
                user_is.append(line_i)
    user_is.sort()
    line_n = users[user]
    end_index = len(user_is) - 1
    end = end_index
    if user_is.index(line_n) + 1 < end_index:
        end = user_is[user_is.index(line_n) + 1]
    else:
        end = len(content)
    access_key_re = re.compile("aws_access_key_id\s*=\s*(.+)")
    secret_re = re.compile("aws_secret_access_key\s*=\s*(.+)")
    acces_key = None
    secret = None
    for line_i in xrange(line_n, end):
        ak_res = access_key_re.match(content[line_i])
        s_res = secret_re.match(content[line_i])
        if ak_res != None:
            access_key = ak_res.groups()[0]
        if s_res != None:
            secret = s_res.groups()[0]
    rv = {}
    rv[user] = {}
    rv[user]['access_key'] = access_key
    rv[user]['secret'] = secret
    return rv
            

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

    parser.add_argument('--user', required=False, dest='user')
    parser.add_argument('--sign_in', action='store_true', default=False)
    
    parser.add_argument('--aws_access_key_id', required=False, dest='aws_access_key_id')
    parser.add_argument('--aws_secret_access_key', required=False, dest='aws_secret_access_key') 
    
    aws_args = parser.parse_args()

    user = aws_args.user
    if aws_args.user == None:
        print "no user provided, using default user"
        user = 'default'
    aws_access_key_id = None
    aws_secret_access_key = None
    aws_creds_path = os.path.join(expanduser("~"), '.aws', 'credentials')
    if not os.path.exists(aws_creds_path):
        if aws_args.aws_access_key_id != None and aws_args.aws_access_key_id != None:
            aws_access_key_id = aws_args.aws_access_key_id
            aws_secret_access_key = aws_args.secret_access_key
        else:
            print "no credential file present, and no commandline arguments provided"
            return
    else:
        try:
            aws_creds_dict = process_aws_creds_file(aws_creds_path, user)
            aws_access_key_id = aws_creds_dict[user]['access_key']
            aws_secret_access_key = aws_creds_dict[user]['secret']
        except:
            print "either there is an error with your ~/.aws/credentials file or the specified user doesn't have aws_access_key_id and aws_secret_access_key specified"
            return

    email = None
    password = None
    drafts_creds_path = os.path.join(expanduser("~"), '.drafts', 'credentials')
    if aws_args.sign_in or not os.path.exists(drafts_creds_path):
        email = raw_input('Email:')
        password = getpass.getpass("Password for " + email + ":")
        if not os.path.exists(os.path.join(expanduser("~"), '.drafts')):
            os.mkdir(os.path.join(expanduser('~'), '.drafts'))
        with open(drafts_creds_path, 'wb') as f:
            f.write('email = ' + email + '\n')
            f.write('password = ' + password + '\n')
    else:
        email_reg = re.compile("email\s*=\s*(.+)")
        pass_reg = re.compile("password\s*=\s*(.+)")
        try:
            with open(drafts_creds_path, 'rb') as f:
                for line in f:
                    email_res = email_reg.match(line)
                    pass_res = pass_reg.match(line)
                    if email_res != None:
                        email = email_res.groups()[0]
                    if pass_res != None:
                        password = pass_res.groups()[0]
            if email == None or password == None:
                raise "email or passwor not present"
        except:
            print "Error with ~/.drafts/credentials please run draftsupdate with --sign_in"
            return


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
                             aws_access_key_id = aws_access_key_id,
                             aws_secret_access_key = aws_secret_access_key)
                pag = client.get_paginator('describe_spot_price_history')
                params = {'EndTime': month_ago_string, 'StartTime': month_minus_hour_string, 
                        'InstanceTypes': [instance_type], 'ProductDescriptions': ['Linux/UNIX']}
                iterator = pag.paginate(**params)
                result = get_by_az(get_by_instance_type(get_spot_prices(iterator))[instance_type])
                spot_instance_data[region][instance_type] = result
                sys.stdout.flush()
                sys.stdout.write("\r" + region + ": " + instance_type)

        results['spot-instance-data'] = spot_instance_data

        jwt_response = requests.post('http://predictspotprice.cs.ucsb.edu:3000/user_token', json = { 'auth': { 'email': email, 'password': password } } )

        try:
            jwt = jwt_response.json()['jwt']

            headers = {'Authorization' : 'Bearer ' + jwt}

            response = requests.post('http://predictspotprice.cs.ucsb.edu:3000/users/update_az_map', json = results, headers = headers);

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
