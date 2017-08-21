#!/usr/bin/env python
import gevent.monkey as monkey
monkey.patch_all()

import argparse
import os
import re
import subprocess

from gevent.pool import Pool


REQUIREMENT_FILE_NAME_PATTERN = r'requirements.*\.txt'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-p',
                        action='append',
                        help='Path to search for requirement files, repeat '
                             'flag to add more paths')
    parser.add_argument('--resolve-versions',
                        action='store_true',
                        default=False,
                        help='If more than one version of a package is used, '
                             'show the license info for each version '
                             'individually')
    return parser.parse_args()


def find_requirement_files(repo_path):
    for root, dirs, files in os.walk(repo_path):
        path = root.split(os.sep)
        for file in files:
            if re.search(REQUIREMENT_FILE_NAME_PATTERN, file):
                path_to_file = os.path.sep.join(path) + os.path.sep + file
                yield path_to_file


def get_packages(file_path, resolve_versions):
    for line in open(file_path):
        if resolve_versions:
            package_name = line.strip()
        else:
            package_name = line.strip().split('==')[0]
        if package_name:
            yield package_name


def get_license(package_name):
    print('Fetching license for {}'.format(package_name))
    args = ['yolk', '-M', package_name, '-f', 'license']
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        print('Error getting license for {}: {}'.format(package_name, err))
        return 'UNKNOWN'
    return out.decode('utf8').strip() or 'UNKNOWN'


def get_all_licenses(packages):
    print('Fetching license info from PyPi...')

    pool = Pool(10)

    licenses = pool.map(get_license, packages)

    output = zip(packages, licenses)
    for package, license in output:
        print('{:<40s} {}'.format(package, license))


def run():
    args = parse_args()

    packages = set()

    for base_path in args.p:
        for requirement_file in find_requirement_files(base_path):
            print('Processing file: {}'.format(requirement_file))
            packages.update(get_packages(requirement_file,
                                         args.resolve_versions))

    packages = sorted(list(packages), key=lambda x: x.lower())

    print('Found {} packages:'.format(len(packages)))
    for package in packages:
        print('    {}'.format(package))

    get_all_licenses(packages)
