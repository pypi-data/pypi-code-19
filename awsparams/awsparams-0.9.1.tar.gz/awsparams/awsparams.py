#!/usr/bin/env python3.6
# Copyright 2016 Brigham Young University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import fire
import boto3
import sys
from getpass import getpass
__VERSION__='0.9.1'


def connect_ssm(profile=''):
    """
    >>> ssm = connect_ssm()
    """
    if profile:
        session = boto3.Session(profile_name=profile)
        ssm = session.client('ssm')
    else:
        ssm = boto3.client('ssm')
    return ssm


def put_parameter(profile, overwrite, parameter):
    ssm = connect_ssm(profile)
    if overwrite:
        parameter['Overwrite'] = True
    ssm.put_parameter(**parameter)
    

def remove_parameter(profile, param):
    ssm = connect_ssm(profile)
    ssm.delete_parameter(Name=param)


# TODO refactor to regular get_parameter + clarity ie line 52 is hard to read
def get_parameter(name, profile=None, cache=None, decryption=False):
    ssm = connect_ssm(profile)
    param = next(parm for parm in ssm.get_parameters(Names=[name], WithDecryption=decryption)['Parameters'])
    if param.get('Description'):
        param['Description'] = next((parm['Description'] for parm in cache if parm['Name'] == name)) if cache else next((parm['Description'] for parm in get_all_parameters(profile) if parm['Name'] == name))
    return param


def get_all_parameters(profile, pattern=None, simplify=False):
    ssm = connect_ssm(profile)
    parameter_page = ssm.describe_parameters()
    parameters = parameter_page['Parameters']
    while parameter_page.get('NextToken'):
        parameter_page = ssm.describe_parameters(NextToken=parameter_page['NextToken'])
        parameters.extend(parameter_page['Parameters'])
    if pattern and simplify:
        return [param for param in translate_results(parameters) if pattern in param]
    elif pattern:
        return [param for param in parameters if pattern in param['Name']]
    elif simplify:
        return translate_results(parameters)
    else:
        return parameters


def translate_results(parameters):
    """
    >>> parms = [{'Name': 'test', 'Description': 'testing'}]
    >>> translate_results(parms)
    ['test']
    """
    return [parm['Name'] for parm in parameters]
    

def ls(*, profile=None, values=False, with_decryption=False, prefix=None):
    """
    >>> new('testing.testing.testing', '1234', description='This is a test parameter')
    >>> ls(prefix='testing.testing')
    testing.testing.testing
    >>> ls(prefix='testing.testing', values=True)
    testing.testing.testing: 1234
    >>> rm('testing.testing.testing', force=True)
    The testing.testing.testing parameter has been removed
    """
    for parm in get_all_parameters(profile, prefix, simplify=True):
        if values:
            try:
                ls_values = get_parameter(parm, profile=profile, decryption=with_decryption)
                print("{}: {}".format(ls_values['Name'], ls_values['Value']))
            except Exception as err:
                print("Unknown error occured: {}".format(err))
        else:
            print(parm)


def cp(src, dst=None, src_profile=None, dst_profile=None, prefix=False, overwrite=False):
    """
    >>> new('testing.testing.testing', '1234', description='This is a test parameter')
    >>> cp('testing.testing.testing', 'testing.testing.newthing')
    Copied testing.testing.testing to testing.testing.newthing
    >>> cp('testing.testing.testing')
    dst (Destination) is required when not copying to another profile
    >>> rm('testing.testing.testing', force=True)
    The testing.testing.testing parameter has been removed
    >>> rm('testing.testing.newthing', force=True)
    The testing.testing.newthing parameter has been removed
    """
    # cross account copy without needing dst
    if src_profile != dst_profile and not dst:
        dst = src
    elif not dst:
        print("dst (Destination) is required when not copying to another profile")
        return
    if prefix:
        params = get_all_parameters(src_profile, src)
        for i in params:
            put = get_parameter(name=i['Name'], profile=src_profile, cache=params, decryption=True)
            put['Name'] = put['Name'].replace(src, dst)
            put_parameter(dst_profile, overwrite, put)
            print(f"Copied {i['Name']} to {put['Name']}")
    else:
        if isinstance(src, str):
            src_param = [src]
        for i in src_param:
            put = get_parameter(name=i, profile=src_profile, decryption=True)
            put['Name'] = dst
            put_parameter(dst_profile, overwrite, put)
            print(f"Copied {src} to {dst}")


def mv(src, dst, prefix=False, profile=None):
    """
    >>> new('testing.testing.testing', '1234', description='This is a test parameter')
    >>> mv('testing.testing.testing', 'testing.testing.newthing')
    Copied testing.testing.testing to testing.testing.newthing
    The testing.testing.testing parameter has been removed
    >>> rm('testing.testing.newthing', force=True)
    The testing.testing.newthing parameter has been removed
    """
    if prefix:
        cp(src, dst, src_profile=profile, dst_profile=profile, prefix=prefix)
        rm(src, force=True, prefix=True, profile=profile)
    else:
        cp(src, dst, src_profile=profile, dst_profile=profile)
        rm(src, force=True, profile=profile)


def sanity_check(param, force):
    if force:
        return True
    sanity_check = input(f"Remove {param} y/n ")
    return sanity_check == 'y'


def rm(src, force=False, prefix=False, profile=None):
    """
    >>> new('testing.testing.testing', '1234', description='This is a test parameter')
    >>> new('testing.testing.testing2', '1234', description='This is a test parameter')
    >>> rm('testing.testing.testing', force=True)
    The testing.testing.testing parameter has been removed
    >>> rm('testing.testing', force=True, prefix=True)
    The testing.testing.testing2 parameter has been removed
    """
    if prefix:
        params = get_all_parameters(profile, src, True)
        if len(params) == 0:
            print(f"No parameters with the {src} prefix found")
        else:
            for param in params:
                if sanity_check(param, force):
                    remove_parameter(profile, param)
                    print(f"The {param} parameter has been removed")
    else:
        param = get_parameter(name=src, profile=profile)
        if 'Name' in param:
            if sanity_check(src, force):
                remove_parameter(profile, src)
                print(f"The {src} parameter has been removed")
        else:
            print(f"Parameter {src} not found")


def new(name=None, value=None, param_type='String', description=None, profile=None, overwrite=False):
    """
    >>> new('testing.testing.testing', '1234', param_type='SecureString', description='This is a test parameter')
    >>> ls(prefix='testing.testing', values=True, with_decryption=True)
    testing.testing.testing: 1234
    >>> rm('testing.testing.testing', force=True)
    The testing.testing.testing parameter has been removed
    """
    if not name:
        name = input("Parameter Name: ")
    if not param_type:
        control = True
        valid_types = ['String', 'StringList', 'SecureString']
        while control:
            param_type = input("Parameter Type: ")
            if param_type in valid_types:
                control = False
            else:
                print("Type must be one of {}".format(', '.join(valid_types)))
    if not value:
        if param_type == 'SecureString':
            value = getpass(prompt="SecureString: ")
        elif param_type == 'StringList':
            value = input("Input Values seperated by ','")
        elif param_type == 'String':
            value = input('Parameter Value: ')
    if not description:
        description = input("Parameter Description: ")
    
    param = {
        'Name': name,
        'Description': description,
        'Value': value,
        'Type': param_type,
        'Overwrite': overwrite
    }
    put_parameter(profile, overwrite, param)


def test(verbose=False):
    import doctest
    sys.exit(doctest.testmod(verbose=verbose)[0])

def main():
    fire.Fire()

if __name__ == '__main__':
    main()