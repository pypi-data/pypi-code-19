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
# from copy import deepcopy
import requests

from filter_datetime import filter_datetime
from path_dict_conv import paths_to_dict, dict_to_paths



def __single_filter(entry, path_list, first):
    '''
    filter single entry with path_list
    '''
    global metrics_dict
    path_groups = []
    for path in path_list:
        #check if path has ended.  If so, remove from checks if passed, return False if failed
        if len(path['path']) <= 1:
            value = str(path['value'])
            ##convert null to None
            if value == 'null':
                value = 'None'
            entry_index = path['path'][0]
            ##check for key errors
            try:
                entry[entry_index]
            except KeyError:
                metrics_dict['missing_keys'] += 1
                return False
            ##check regex and for compile errors
            try:
                regex_value = re.compile(value, re.IGNORECASE)
                if not re.search(regex_value, str(entry[entry_index]).encode('utf-8')) and not filter_datetime(value, entry[entry_index]):
                    return False
            except:
                metrics_dict['regex_errors'] += 1
                return False

        #sort paths into groups based on first value
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
                    if __single_filter(item, group, False):
                        match = True
                if not match:
                    return False
            else:
                if current_index in list(entry):
                    if not __single_filter(entry[current_index], group, False):
                        return False
                else:
                    return False
        return True
    else:
        for group in path_groups:
            for i, path in enumerate(group):
                group[i] = {'value': path['value'], 'path': path['path'][1:]}
            if __single_filter(entry, group, False):
                return True

def write_data(data, file_name='data.json'):
    with open(file_name, 'wb') as output_file:
        output_file.write(json.dumps(data))
        output_file.close()
        print("File written successfully...")


def filter_data(data, search_input, max_results=5000, metrics=False):
    '''
    filter data based on path list or search dict arrays
    '''
    ##check if single path or single path group was used
    try:
        search_input['path']
        search_input['value']
        print("single path")
        search_input = [search_input]
    except:
        pass

    try:
        search_input[0]['path']
        search_input[0]['value']
        print("single path group")
        search_input = [search_input]
    except:
        pass

    ##check if single dict was used
    if isinstance(search_input, dict):
        print("Input is dict")
        search_input = [search_input]

    print("Data length: ", len(data))
    print("Running Search...")
    filtered_results = []
    global metrics_dict
    metrics_dict = {'missing_keys': 0, 'regex_errors': 0}

    for i, search_list in enumerate(search_input):
        if isinstance(search_list, dict):
            search_list = dict_to_paths(search_list, [], [])
        elif isinstance(search_list, list):
            search_list = search_list
        else:
            print("Invalid input type.  Must be 'dicts' or 'lists'")
            sys.exit(1)
        print("search_list: ", search_list)
        for search in search_list:
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
            elif __single_filter(entry, search_list, True) and entry not in filtered_results:
                filtered_results.append(entry)
    print("Results found: ", len(filtered_results))
    if metrics:
        return {'results': filtered_results, 'metrics': metrics_dict}
    return filtered_results

def get_data(url=None, file_name='output.json', source="file"):
    '''
    Load data from either a source file or the api
    '''

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
            print("You must use a url string when calling the api_to_file function.  Ex: parski.get_data(url='api_address.google.com')")
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
                    return {'status_code': 404, 'error_msg': "Not found.  Your url is probably wrong or you're not on VPN"}
        else:
            pass
    else:
        return {'status_code': 500, 'error_msg': "Invalid source parameter."}

    try:
        api_key = os.environ['PCT_API_READ_KEY']
        headers = {'x-api-key': api_key, 'Cache-Control': 'no-cache'}
    except:
        print('api key could not be loaded')
        return {'status_code': 401, 'error_msg': "Unauthorized.  Your API key isn't working..."}

    #LOAD FROM API

    tries = 1
    while tries <= 5:

        try:
            print("Sending api request...")
            req = requests.get(url, headers=headers)
            if req.status_code != 200:
                print ("WARNING:  API call status code was %s" % req.status_code)

            json_string = json.dumps(req.json())
            clean_json_string = '[' + json_string.lstrip('[').rstrip(']') + ']'
            print("Request Returned!  Writing file....")
            with open(file_name, 'wb') as output_file:
                output_file.write(clean_json_string)
                output_file.close()
            print("File written successfully...")
            return json.loads(clean_json_string)

        except Exception as error:
            #Check Errors
            try:
                req
            except:
                print("API Server could not be reached")
                return {'status_code': 404, 'error_msg': 'API Server could not be reached'}
            print(error)
            print ("API request failed with a %s status code" % req.status_code)
            if req.status_code == 401:
                print ("Unauthorized.  Your API key isn't working...")
                return {'status_code': 401, 'error_msg': "Unauthorized.  Your API key isn't working..."}
            elif req.status_code == 404:
                print ("Not found.  Your url is probably wrong or you're not on VPN")
                return {'status_code': 404, 'error_msg': "Not found.  Your url is probably wrong or you're not on VPN"}
            elif req.status_code == 502:
                print ("The response failed.  This happens from time to time...")
            elif req.status_code == 503:
                print ("Internal Server Error.  The API might be down...")
            else:
                print(error)

            #Retry
            if tries >= 4:
                return {'status_code': 502, 'error_msg': "The API just doesn't want to talk to you today."}
            else:
                print("Trying again in %s seconds\n" % ((tries+1)**2))
                time.sleep((tries+1)**2)
                print("LET'S DO THIS!!!!")
            tries = tries + 1

