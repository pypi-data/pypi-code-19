"""
Takes input json and massages it to make sconbld json (test edit)
"""
from __future__ import print_function

import sys
import os
import time
import json
import re
import datetime
import requests
from pyTableFormat import TableFormat, Table_Formattable_Object

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
# apparently python datetime is stupid and doesn't support zulu
# http://stackoverflow.com/questions/19654578/python-utc-datetime-objects-iso-format-dont-include-z-zulu-or-zero-offset

class Property(object):
    '''
    Slightly more advanced property value that can do special handling of
    representation for dict or datetime types. 
    Valid values for prop_type = 
    'S' ( for string )
    'D' ( for dict )
    'T' ( for datetime )
    '''
    def __init__(self, prop_name, prop_value, prop_type=None):
        self.prop_name = prop_name
        self.prop_value = prop_value
        self.key_type = ''
        if prop_type is None:
            prop_type = 'S' # string
        elif prop_type == 'T':
            self.dto = self.process_datetime(prop_value)
            self.prop_value = prop_value
        else:
            self.prop_type = prop_type

    def get(self, search):
        try:
            if self.prop_type == 'D':
                return self.prop_value.get(search)
        except:
            return self.__repr__()
    def __repr__(self):
        if 'dict' in str(type(self.prop_value)):
            str_dict = str(self.prop_value)
            return u''.join((str_dict)).encode('utf-8').strip()
        try:
            if self.prop_value is None:
                self.prop_value = ''
            return u''.join((self.prop_value)).encode('utf-8').strip()
        except Exception as e:
            msg = ("Exception: %s, trying to unicode encode: %s" % (str(e), str(self.prop_value)))
            print(msg, file=sys.stderr)
            return str(self.prop_value)
    def process_datetime(self, dstring):
        try:
            dto = datetime.datetime.strptime(dstring, DATETIME_FORMAT)
        except:
            dto = 'ERROR'
        return dto


class Entry(Table_Formattable_Object):
    """
    Holds entries coming back from the API json and
    supporting methods to generate print
    """
    def __init__(self, **kwargs):
        self.AccountId = Property('AccountId', kwargs.get('AccountId'))
        self.Alias = Property('Alias', kwargs.get('Alias'))
        self.AmiLaunchIndex = Property('AmiLaunchIndex', kwargs.get("AmiLaunchIndex"))
        self.Architecture = Property('AmiLaunchIndex', kwargs.get("Architecture"))
        self.ClientToken = Property('ClientToken', kwargs.get("ClientToken"))
        self.DnsName = Property('DnsName', kwargs.get('DnsName'))
        self.EbsOptimized = Property('EbsOptimized', kwargs.get('EbsOptimized')) 
        self.Hypervisor = Property('Hypervisor', kwargs.get('Hypervisor'))
        self.ImageId = Property('ImageId', kwargs.get('ImageId'))
        self.InstanceId = Property('InstanceId', kwargs.get('InstanceId'))
        self.InstanceType = Property('InstanceType', kwargs.get('InstanceType'))
        self.IpAddress = Property('IpAddress', kwargs.get('IpAddress'))
        self.KernelId = Property('KernelId', kwargs.get('KernelId'))
        self.KeyName = Property('KeyName', kwargs.get('KeyName'))
        self.LaunchTime = Property('LaunchTime', kwargs.get('LaunchTime'), prop_type='T')
        self.Name = Property('name', kwargs.get('Name'))
        self.PrivateDnsName = Property('PrivateDnsName', kwargs.get('PrivateDnsName'))
        self.PrivateIpAddress = Property('PrivateIpAddress', kwargs.get('PrivateIpAddress'))
        self.Reason = Property('Reason', kwargs.get('Reason'))
        self.Region = Property("Region", kwargs.get("Region"))
        self.RootDeviceType = Property("RootDeviceType", kwargs.get("RootDeviceType"))
        self.rootDeviceName = Property("rootDeviceName", kwargs.get("rootDeviceName"))
        self.SourceDestCheck = Property("SourceDestCheck", kwargs.get("SourceDestCheck"))
        self.State = Property('State', kwargs.get('State'))
        self.SubnetId = Property('SubnetId', kwargs.get('SubnetId'))
        self.Tags = Property('Tags', kwargs.get('Tags'), prop_type='D')
        # self.instance_profile = Property('instance_profile', kwargs.get('instance_profile'))
        self.VirtualizationType = Property('VirtualizationType', kwargs.get('VirtualizationType'))
        self.VpcId = Property('VpcId', kwargs.get('VpcId'))
        try:
            self.UAI = Property('UAI', self.Tags.get('UAI'))
        except:
            pass
        self.dict_extend_values = {'AccountId': 20,
                                   'Alias': 30,
                                   'DnsName': 30,
                                   'ImageId': 15,
                                   'InstanceId': 15,
                                   'InstanceType': 12,
                                   'IpAddress': 16,
                                   'KeyName': 20,
                                   'LaunchTime': 22,
                                   'Name': 30,
                                   'PrivateDnsName': 20,
                                   'PrivateIpAddress': 16,
                                   'Reason': 15,
                                   'Region': 20,
                                   'State': 15,
                                   'SubnetId': 25,
                                   'Tags': 20,
                                   'VirtualizationType': 25,
                                   'VpcId': 15,
                                   'UAI': 15}
        self.dump_ignore_attrs = ['AmiLaunchIndex', 'Architecture', 'ClientToken', 'EbsOptimized', 'Hypervisor', 'KernelId', 'PrivateDnsName',
                                    'Reason', 'RootDeviceType', 'SourceDestCheck', 'VirtualizationType', 'rootDeviceName']
    def dumpself(self):
        return "Name: '%s'" % self.Name
    def dumpdict(self):
        return_dict = {}
        for attr in dir(self):
            if (
                    '__' not in attr and
                    'instancemethod' not in str(type(getattr(self, attr))) and
                    'dict' not in str(type(getattr(self, attr))) and
                    'dump_ignore_attrs' not in attr):
                return_dict[attr] = str(getattr(self, attr))
        return return_dict
    def return_props(self):
        """
        returns just the list of properties of type Property()
        """
        attrs = [x for x in dir(self) if 'Property' in str(type(getattr(self, x)))]
        return attrs
    def dictify(self):
        dict_attrs = {}
        for attr in self.return_props():
            dict_attrs[attr] = getattr(self, attr).prop_value
        return dict_attrs
    def in_me(self, prop_name, prop_value_regex_obj):

        if prop_name == 'tag_key':
            tag_dict = getattr(self, 'Tags').prop_value
            for key, value in tag_dict.iteritems():
                try:
                    match = re.search(prop_value_regex_obj,
                                      str(key).encode('utf-8'))
                except UnicodeEncodeError:
                    pass
                if match:
                    return True
            return False

        elif prop_name == 'tag_value':
            tag_dict = getattr(self, 'Tags').prop_value
            for key, value in tag_dict.iteritems():
                try:
                    match = re.search(prop_value_regex_obj,
                                      str(value).encode('utf-8'))
                except UnicodeEncodeError:
                    pass
                if match:
                    return True
            return False
        # if prop_name in self.Tags.prop_value:
        #     match = re.search(prop_value_regex_obj, self.Tags.get(prop_name))
        #     if match:
        #         return True
        elif prop_name in self.return_props():
            match = False
            try:
                match = re.search(prop_value_regex_obj,
                                  str(getattr(self, prop_name).prop_value).encode('utf-8'))
            except Exception as e:
                log_msg = ("Exception '%s'. Failure with regex search match on entry: '%s'" %
                           (str(e), str(self.dumpdict())))
                print(log_msg, file=sys.stderr)
            if match:
                return True
    def is_within_datetime_range(self, dto_low, dto_high):
        ''' Takes datetime objects and returns true if entry.LaunchTime
        is within range
        '''
        # print("LAUNCH TIME IS: %s" % str(self.LaunchTime.dto))
        if self.LaunchTime.dto > dto_low and self.LaunchTime.dto < dto_high:
            return True
        else:
            return False
    def __eq__(self, other):
        return self.InstanceId.prop_value == other.InstanceId.prop_value
    def __hash__(self):
        return hash(('InstanceId', self.InstanceId.prop_value))

class NodeSet(object):
    def __init__(self, fname=None, rawjson=None):
        if fname is not None:
            self.entries = self.load(fname) # list of Entry objects
        if rawjson is not None:
            self.entries = self.load_json(rawjson)
        self.date_range_low = datetime.datetime.now() # set to dto now for now
        self.date_range_high = datetime.datetime.now()
        self.date_range_string = self.build_dtos_default()

    def dictify_entries(self):
        attrs = []
        for entry in self.entries:
            attrs.append(entry.dictify())
        return attrs

    def load_json(self, rawjson):
        nodes = []
        if 'str' in str(type(rawjson)):
            rawjson = json.loads(rawjson)
        for item in rawjson:
            #Tags
            Tags = {}
            try:
                for tag in item['Tags']:
                    Tags[tag.get('Key')] = tag.get('Value')
                    if tag.get('Key') == 'Name':
                        item['Name'] = tag.get('Value')
            except:
                pass
            item['Tags'] = Tags

            #State
            item['State'] = ''
            try:
                for tag, val in item['InstanceState'].iteritems():
                    if tag == 'Name':
                        item['State'] = val
            except:
                pass

            #Bool and Integers
            try:
                item['AmiLaunchIndex'] = str(item['AmiLaunchIndex'])
                item['SourceDestCheck'] = str(item['SourceDestCheck'])
                item['EbsOptimized'] = str(item['EbsOptimized'])
            except:
                pass

            entry = Entry(**item)
            nodes.append(entry)
        return nodes

    def load(self, fname):
        with open(fname) as f:
            j = json.load(f)
            return self.load_json(j)

    def format_results(self, results, html=None):
        msg = "{0:40}{1:10}".format("Number of Results:", str(len(results)))
        msg += '<table border=1>'
        if html is None:
            html_bool = True
        else:
            html_bool = False
        if len(results) > 0:
            if html_bool:
                try:
                    msg += '<tr>'
                    msg += (results[0].dumpself_tableformat_header(html=html_bool))
                    msg += '</tr>'
                    for entry in results:
                        msg += '<tr>'
                        msg += entry.dumpself_tableformat(html=html_bool)
                        msg += '</tr>'
                    msg += '</table>'
                    return msg
                except Exception as e:
                    log_msg = "Error in results formatting: " + str(e)
                    print(log_msg, file=sys.stderr)
                    msg += str(e)
            else:
                msg += (results[0].dumpself_tableformat_header(html=html_bool))
                for entry in results:
                        msg += entry.dumpself_tableformat(html=html_bool)
                return msg
        else:
            msg += "EMPTY RESULTS"
            return msg
    def within_date_range(self, results):
        '''
        returns list that matches the datetime ranges
        '''
        return [x for x in results if x.is_within_datetime_range(self.date_range_low, self.date_range_high)]

    def build_dtos(self, date_range_string=None):
        '''
        Builds from self.date_range_string and builds the datetime objects
        for self.date_range_low and date_range_high
        date_range is a string in the format "YYYYMMDD-YYYYMMDD"
        '''
        if date_range_string is None:
            self.date_range_string = self.build_dtos_default()
        else:
            self.date_range_string = date_range_string
        lowstring = self.date_range_string.split('-')[0]
        highstring = self.date_range_string.split('-')[1]
        self.date_range_high = datetime.datetime.strptime(highstring, '%Y%m%d')
        self.date_range_low = datetime.datetime.strptime(lowstring, '%Y%m%d')
        print("DATE RANGE HIGH OBJ: '%s'" % str(self.date_range_high))
        print("DATE RANGE LOW OBJ: '%s'" % str(self.date_range_low))

    def build_dtos_default(self):
        now = datetime.datetime.now()
        nowstring = datetime.datetime.strftime(now, '%Y%m%d')
        date_range = '19700101-' + nowstring
        print("SETTING DATE RANGE DEFAULT: '%s' " % date_range)
        return date_range

    def single_search(self, entries, tag_name, tag_value_regex):
        results = []
        log_msg = "Tag name is '%s' and regex is '%s'" % (str(tag_name), str(tag_value_regex))
        print(log_msg, sys.stderr)
        try:
            rtv = re.compile(tag_value_regex, re.IGNORECASE)
        except Exception as e:
            log_msg = ("HRMMMMM: %s" % str(e))
            print(log_msg, file=sys.stderr)
            return [{'ERR - regex compile'}]
        for i, entry in enumerate(entries):
            if entry.in_me(tag_name, rtv):
                results.append(entry)
        return results
    def search_tag(self, search_Tags_dict, gimmestring=True, date_range=None, match_policy='AND'):
        '''
            Search for a given set of Tags in the inventory. Takes a dictionary of
            Tags as keys with values of regex to search.
            gimmestring is a boolean and will return string results instead of list
            when set to True.
            date_range is a string in the format "YYYYMMDD-YYYYMMDD"
            date_range defaults to "19700101-(now)" if none is specified
        '''
        try:
            self.build_dtos(date_range_string=date_range)
        except Exception as ex:
            print("using default date range due to Exception parsing date_range: %s" % str(ex))
            self.build_dtos()
        print("match policy = " + str(match_policy), sys.stderr)

        total_results = self.entries
        if match_policy.upper() == 'OR':
            filtered_results = []
            for key, val in search_Tags_dict.iteritems():
                subsearch = self.single_search(total_results, key, val)
                filtered_results = list(set(subsearch) | set(filtered_results))
            filtered_results = list(set(self.within_date_range(total_results)) | set(filtered_results))
            final_results = filtered_results
        else:
            filtered_results = total_results
            for key, val in search_Tags_dict.iteritems():
                filtered_results = self.single_search(filtered_results, key, val)
            filtered_results = self.within_date_range(filtered_results)
            final_results = filtered_results

        if gimmestring:
            return self.format_results(final_results)
        else:
            return final_results
    def gen_csv_string(self, results):
        msg = ''
        if len(results) > 0:
            msg += results[0].dumpself_csv_header()
            for result in results:
                msg += result.dumpself_csv()
        return msg

def api_to_file(url=None, file_name='output.json', check_file=False):
    if not isinstance(url, str):
        print("You must use a url string when calling the api_to_file function.  Ex: parski.api_to_file(url='api_address.google.com')")
        sys.exit(1)

    if check_file and os.path.isfile( file_name):
        return
    api_key = os.environ['PCT_API_READ_KEY']

    if len(api_key) < 2:
        print("PCT_API_READ_KEY environment variable not set or set improperly. Exiting.")
        sys.exit(1)

    headers = {'x-api-key': api_key, 'Cache-Control': 'no-cache'}

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
            print(error)
            print ("API request failed with a %s status code" % req.status_code)
            if req.status_code == 401:
                print ("Unauthorized.  Your API key isn't working...")
                break
            elif req.status_code == 502:
                print ("The response failed.  This happens from time to time...")
            elif req.status_code == 503:
                print ("Internal Server Error.  The API might be down...")
            else:
                print(error)

            if tries >= 4:
                print('4 api requests tried.  4 failed.  Exiting...')
                sys.exit(1)
            else:
                print("Trying again in %s seconds\n" % ((tries)**2))
                time.sleep((tries)**2)
                print("LET'S DO THIS!!!!")
            tries = tries + 1

def debug():
    d = {'name': 'proxy'}
    req = nodeset.search_tag(d, gimmestring=False, date_range='19701001-20161001')
    print(nodeset.format_results(req, html=False))

if __name__ == '__main__':
    nodeset = NodeSet('lib/output.json')
    debug()
