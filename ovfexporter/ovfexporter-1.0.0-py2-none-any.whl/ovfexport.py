#!/usr/bin/python
import argparse
from OvfExporter import OvfExporter
import tempfile
import os
import sys


def parse_args():
    """
    Argument parser and validator
    :return: args
    """
    parser = argparse.ArgumentParser(description="Converts, and downloads a vm by name from vCenter to OVF in specified"
                                                 " directory, then uploads the image as an AMI. AMI will be uploaded "
                                                 "using specified AWS profile, to specified regions. ")
    parser.add_argument('-i', '--vcenter_host', type=str, required=True, help='Hostname or Ip of vCenter API of VM')
    parser.add_argument('-u', '--vcenter_user', type=str, required=True, help='Username for vCenter authentication')
    parser.add_argument('-p', '--vcenter_pass', type=str, required=True, help='Password for authentication to vCenter API')
    parser.add_argument('-n', '--vm_name', type=str, required=True, help='Name of the VM in vCenter')
    parser.add_argument('-d', '--directory', type=str, default=tempfile.mkdtemp(),
                        help='Directory to save the vmdk temp file (defaults to temp location')
    parser.add_argument('-w', '--vcenter_port', type=str, default='443',
                        help='Port to use for communication to vcenter api. Default is 443')
    args = parser.parse_args()
    validate_args(args)
    return args


def validate_args(args):
    """
    Call all required validation functions
    :param args:
    :return:
    """
    if not os.path.isdir(args.directory):
        print "Directory {} does not exist".format(args.directory)
        sys.exit(5)
    return args


def convert(args):
    """
    Download VM disks, and OVF from vCenter
    :param args:
    :return: created vmdk
    """
    exporter = OvfExporter(user=args.vcenter_user,password=args.vcenter_pass, host=args.vcenter_host, port=args.vcenter_port,
                           vm_name=args.vm_name, dir=args.directory)
    return exporter.export_ovf()


def main():
    args = parse_args()
    convert(args)
