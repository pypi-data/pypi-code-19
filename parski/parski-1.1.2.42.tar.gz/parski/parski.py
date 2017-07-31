"""
Takes input json and massages it to make sconbld json (test edit)
"""
from __future__ import print_function

import sys
import os
import time
import json
import re
# import datetime
from copy import deepcopy
import requests

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"

def dict_to_paths(search_list, current_path, paths):
    '''
    Convert search_dict to list of paths.
    First call should be dict_to_paths(search_dict, [], [])
    '''
    if isinstance(search_list, dict):
        for key, value in search_list.iteritems():
            temp_path = deepcopy(current_path)
            temp_path.append(key)
            paths = dict_to_paths(search_list[key], temp_path, paths)
    elif isinstance(search_list, list):
        for i, item in enumerate(search_list):
            temp_path = deepcopy(current_path)
            temp_path.append(i)
            paths = dict_to_paths(search_list[i], temp_path, paths)
    else:
        paths.append({'path': current_path, 'value': str(search_list)})
    return paths

def paths_to_dict(input_list):
    #rewrite me to look like dict_to_paths, papa
    #shut up, boy
    search_dict = {}
    for item in input_list:
        sub_dict = search_dict
        for i, step in enumerate(item['path']):
            #check if last step and set value

            if isinstance(step, int):
                #if array extend array until it is the length of step
                while len(sub_dict) <= step:
                    sub_dict.append(None)
            elif isinstance(step, basestring):
                if step not in sub_dict:
                    sub_dict[step] = None

            if i+1 >= len(item['path']):
                sub_dict[step] = item['value']
            #else
            else:
                next_step = item['path'][i+1]
                if isinstance(next_step, int) and sub_dict[step] is None:
                    sub_dict[step] = []
                elif isinstance(next_step, basestring) and sub_dict[step] is None:
                    sub_dict[step] = {}
                sub_dict = sub_dict[step]
    return search_dict

def single_filter(entry, path_list, first):
    '''
    filter single entry with path_list
    '''
    path_groups = []
    for path in path_list:
        #check if path has ended.  If so, remove from checks if passed, return False if failed
        if len(path['path']) <= 1:
            value = str(path['value'])
            if value == 'null':
                value = 'None'
            entry_index = path['path'][0]
            try:
                entry[entry_index]
            except KeyError:
                print('Entry does not contain key: ', entry_index)
                return False
            try:
                regex_value = re.compile(value, re.IGNORECASE)
                if not re.search(regex_value, str(entry[entry_index]).encode('utf-8')):
                    return False
            except:
                print('ERR - regex compile: ', value)
                return False

        #sort pathes into groups based on first value
        else:
            found = False
            # new_path = {'value': path['value'], 'path': path['path'][1:]}
            for group in path_groups:
                if path['path'][0] == group[0]['path'][0]:
                    # print "found path: ", path
                    group.append(path)
                    found = True
                    break
            if not found:
                # print "didn't find path: ", path
                path_groups.append([path])

    #run each group together
    if not first:
        for group in path_groups:
            current_index = group[0]['path'][0]
            for i, path in enumerate(group):
                group[i] = {'value': path['value'], 'path': path['path'][1:]}
            #check if list, if so run against all
            if isinstance(entry, list):
                match = False
                for item in entry:
                    if single_filter(item, group, False):
                        match = True
                if not match:
                    return False
            else:
                if current_index in list(entry):
                    if not single_filter(entry[current_index], group, False):
                        return False
                else:
                    return False
        return True
    else:
        for group in path_groups:
            for i, path in enumerate(group):
                group[i] = {'value': path['value'], 'path': path['path'][1:]}
            if single_filter(entry, group, False):
                return True

def filter_data(data, search_input, max_results=5000):
    '''
    filter data based on path list or search dict arrays
    '''
    if isinstance(search_input, dict):
        print("dict found")
        search_input = [search_input]
    print(len(data))
    print("Running Search...")
    filtered_results = []
    for i, search_list in enumerate(search_input):
        if isinstance(search_list, dict):
            search_list = dict_to_paths(search_list, [], [])
        elif isinstance(search_list, list):
            search_list = search_list
        else:
            print("Invalid input type.  Must be 'dicts' or 'lists'")
            sys.exit(1)

        for search in search_list:
            print(search_list)
            try:
                int(search['path'][0])
            except:
                search['path'] = [i] + search['path']

        #Remove paths where value is None
        temp_paths = []
        for path in search_list:
            if path['value'] != str(None):
                temp_paths.append(path)
        search_list = temp_paths
        for entry in data:
            if len(filtered_results) >= max_results:
                break
            elif single_filter(entry, search_list, True) and entry not in filtered_results:
                filtered_results.append(entry)
    print("Results found: ", len(filtered_results))

    return filtered_results

def get_data(url=None, file_name='output.json', source="file"):
    '''
    Load data from either a source file or the api
    '''
    api_key = os.environ['PCT_API_READ_KEY']
    headers = {'x-api-key': api_key, 'Cache-Control': 'no-cache'}

    if source == "file":
        try:
            print("Loading File...")
            with open(file_name, 'rb') as stored_file:
                data = stored_file.read()
                return json.loads(data)
        except:
            print("File could not be loaded.  Pulling from API")
    elif source == "api":
        if not isinstance(url, str):
            print("You must use a url string when calling the api_to_file function.  Ex: parski.api_to_file(url='api_address.google.com')")
            print("Attempting to load from file...")
            if not os.path.isfile(file_name):
                print("%s cannot be found.  Exiting..." % file_name)
                sys.exit(1)
            else:
                try:
                    with open(file_name, 'rb') as stored_file:
                        data = stored_file.read()
                        return json.loads(data)
                except:
                    print("File could not be loaded.  Exiting...")
                    sys.exit(1)
        else:
            pass
    elif len(api_key) < 2:
        print("PCT_API_READ_KEY environment variable not set or set improperly. Exiting...")
        sys.exit(1)
    else:
        print("Invalid source parameter.  Exiting...")
        sys.exit(1)

    #LOAD FROM API

    tries = 1
    while tries <= 5:

        try:
            print("Sending api request...")
            req = requests.get(url, headers=headers)
            if req.status_code != 200:
                print ("WARNING:  API call status code was %s" % req.status_code)
            print("Request Returned!  Writing file....")
            json_string = json.dumps(req.json())
            clean_json_string = '[' + json_string.lstrip('[').rstrip(']') + ']'
            with open(file_name, 'wb') as output_file:
                output_file.write(clean_json_string)
            print("File written successfully...")
            break
        except Exception as error:
            #Check Errors
            try:
                req
            except:
                print("API Server could not be reached")
                print(error)
                sys.exit(1)
            print(error)
            print ("API request failed with a %s status code" % req.status_code)
            if req.status_code == 401:
                print ("Unauthorized.  Your API key isn't working...")
                break
            elif req.status_code == 404:
                print ("Not found.  Your url is probably wrong or you're not on VPN")
                break
            elif req.status_code == 502:
                print ("The response failed.  This happens from time to time...")
            elif req.status_code == 503:
                print ("Internal Server Error.  The API might be down...")
            else:
                print(error)

            #Retry
            if tries >= 4:
                print('4 api requests tried.  4 failed.  Exiting...')
                sys.exit(1)
            else:
                print("Trying again in %s seconds\n" % ((tries)**2))
                time.sleep((tries)**2)
                print("LET'S DO THIS!!!!")
            tries = tries + 1

    return json.loads(clean_json_string)

