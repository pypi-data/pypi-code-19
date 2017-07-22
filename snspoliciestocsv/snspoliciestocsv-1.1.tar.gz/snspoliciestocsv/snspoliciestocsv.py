#!/usr/bin/env python3
# -*- coding: utf-8-sig -*-

# This file is part of snspoliciestocsv.
#
# Copyright (C) 2017, Thomas Debize <tdebize at mail.com>
# All rights reserved.
#
# snspoliciestocsv is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# snspoliciestocsv is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with snspoliciestocsv.  If not, see <http://www.gnu.org/licenses/>.

from codecs import open
from os import path 
import sys
import re
import csv
import os

# Script version
VERSION = '1.1'

# OptionParser imports
from optparse import OptionParser
from optparse import OptionGroup

# Options definition
parser = OptionParser(usage="%prog [options]\nVersion: " + VERSION)

# Options definition
main_grp = OptionGroup(parser, 'Main parameters')

main_grp.add_option('-i', '--input-file', help='Partial or full Stormshield Network security appliance configuration file. Ex: filter.cfg', nargs=1)
main_grp.add_option('-o', '--output-file', help='Output csv file (default ./policies-out.csv)', default=path.abspath(path.join(os.getcwd(), './policies-out.csv')), nargs=1)
main_grp.add_option('-s', '--skip-header', help='Do not print the csv header', action='store_true', default=False)
main_grp.add_option('-d', '--delimiter', help='CSV delimiter (default ";")', default=';', nargs=1)

parser.option_groups.extend([main_grp])

# Functions
def extract_all_matched_named_groups_from_regex_list(regex_list, line):
    """
        Return a set of all extractable matched parameters.
        >>> regex_list = [p_pass_log, p_pass_ipproto, p_pass_proto, p_from, p_to, p_port, p_comment_creation_date_and_ip_french]
        >>> regex_list[0].groupindex.items()
        [(u'from', 1)]
        >>>extract_all_matched_named_groups_from_regex_list() => {'creation_date': '1970-01-01 00:00:01', 'to': 'GRP_B', 'ip_user': '1.2.3.34', 'ipproto': 'vpn-esp', 'comment': ' ', 'proto': 'none', 'from': 'GRP_A', 'user': 'Foobar'}
            
    """
    result = {}
    
    for regex in regex_list:
        validator = regex.search(line)
        if validator:
            for name, id in regex.groupindex.items():
                matched_value = validator.group(name)
                if matched_value != None: result[name] = matched_value
    
    return result
            
# Functions
def parse(options):
    """
        Parse the data according to several regexes
        
        @param options:  options
        @rtype: return a list of policies ( [ {'type' : 'pass', 'from' : 'A', 'to' : 'B' ...}, {repeat}, ... ] )
    """
    # Handful patterns
    # -- separator
    p_separator_line = re.compile('^separator')
    p_separator_comment = re.compile('comment="(?P<comment>.*?)"', re.IGNORECASE)
    p_separator_color = re.compile('color="(?P<color>[0-9A-Fa-f]+)"', re.IGNORECASE)
    p_separator = [p_separator_comment, p_separator_color]

    # -- from and to
    p_from = re.compile('\sfrom (?P<from>.*) to', re.IGNORECASE)
    p_to = re.compile('\sto (?P<to>.*?)(\sport|\t#)', re.IGNORECASE)

    # -- port
    p_port = re.compile('\sport (?P<port>.*)\s#', re.IGNORECASE)

    # -- comment, so far only in french
    p_comment_creation_date_and_ip_french = re.compile('#(?P<comment>.*)Créée le (?P<creation_date>.*)\, par (?P<user>.*) \((?P<ip_user>.*)\)', re.IGNORECASE)

    # -- pass policy
    p_pass_line = re.compile('^pass')
    p_pass_log = re.compile('(?P<log>log)', re.IGNORECASE)
    p_pass_ipproto = re.compile('ipproto (?P<ipproto>.*) proto', re.IGNORECASE)
    p_pass_proto = re.compile('\sproto (?P<proto>.*) from', re.IGNORECASE)
    
    # -- block policy
    p_block_line = re.compile('^block', re.IGNORECASE)
    
    # -- list of elements in a policy 
    p_policy = [p_pass_log, p_pass_ipproto, p_pass_proto, p_from, p_to, p_port, p_comment_creation_date_and_ip_french]
    
    # End of pattern declaration #
    
    # Init stuff
    policy_list = []
    policy_elem = {}
    policy_count = 0
    
    with open(options.input_file,'r') as fd_input:
        for line in fd_input:
            line = line.lstrip().rstrip().strip()
            
            # We match a separator
            if p_separator_line.search(line):
                policy_elem = extract_all_matched_named_groups_from_regex_list(p_separator, line)
                policy_elem['type'] = 'separator'
                
            # We match a pass line
            if p_pass_line.search(line):
                policy_elem = extract_all_matched_named_groups_from_regex_list(p_policy, line)
                policy_elem['type'] = 'pass'
                policy_count = policy_count + 1
                
            # We match a block line
            if p_block_line.search(line):
                policy_elem = extract_all_matched_named_groups_from_regex_list(p_policy, line)
                policy_elem['type'] = 'block'
                policy_count = policy_count + 1
                
            # If our policy_elem is not empty
            if policy_elem:
                policy_list.append(policy_elem)
                policy_elem = {}
                
    print('[+] %s filtering policies found' % policy_count)
    return policy_list


def generate_csv(results, options):
    """
        Generate a plain CSV file

        @param results : parsed policies
        @param options : options
    """
    keys = ['type', 'log', 'from', 'to', 'ipproto', 'proto', 'port', 'comment', 'creation_date', 'user', 'ip_user']
    
    if results:
        with open(options.output_file, mode='w', encoding='utf-8-sig') as fd_output:
            spamwriter = csv.writer(fd_output, delimiter=options.delimiter)
            
            if not(options.skip_header):
                spamwriter.writerow(keys)
            
            for policy in results:
                output_line = []
                
                for key in keys:
                    if key in policy.keys():
                        # Nifty trick for separator lines, by replacing type column by the comment
                        if key == 'type' and policy[key] == 'separator' and 'comment' in policy.keys():
                            policy['type'] = policy['comment']
                            policy['comment'] = ''
                        
                        output_line.append(policy[key])
                    else:
                        output_line.append('')
            
                spamwriter.writerow(output_line)   
        
        fd_output.close()
    
    print("[+] policies written to '%s'" % options.output_file)
    
    return

def main():
    """
        Dat main
    """
    global parser, VERSION
    
    options, arguments = parser.parse_args()
    
    # Python 2 is a pain with utf-8, sorry but use Python 3
    if sys.version_info[0] < 3:
        parser.error('Sorry but this program is not compatible with Python 2, please use Python 3')
    
    print('snspoliciestocsv.py version %s\n' % VERSION)
    
    if (options.input_file == None):
        parser.error('Please specify a valid input file')
          
    results = parse(options)
    generate_csv(results, options)
    
    return

if __name__ == "__main__" :
    main()