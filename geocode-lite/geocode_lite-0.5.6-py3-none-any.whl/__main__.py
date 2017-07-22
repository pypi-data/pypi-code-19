# -*- coding: utf-8 -*-
import sys
import os
import logging
from optparse import OptionParser
from geocode_lite import __about__
from geocode_lite.api_key_manager import Manager
from geocode_lite.geocoder import Geocoder, get_lat_lng

APP_NAME = __about__.__app_name__

# Exit codes
EXIT_OK = '0'
EXIT_API_KEY = '1'

key_manager = Manager(APP_NAME)
google_map = 'google-map'


def _config_options():
    usage = "Usage: python -m geocode_lite [options] address"
    description = "Get lat/long of the provided address."
    version = APP_NAME + " v" + __about__.__version__

    parser = OptionParser(usage=usage, description=description, version=version)
    parser.add_option("-k", "--api-key", metavar="API_KEY",
                      help="install Google Map API key", dest='api_key')
    parser.add_option("-r", "--full-response",
                      help='Output full JSON response', dest='full_response',
                      action='store_true', default=False)
    parser.add_option("-f", metavar='input-file', help='set input address file', dest='input_file')
    parser.add_option("-o", metavar='output-file', help='set output to CSV file', dest='output_file')
    parser.add_option("-v", "--verbose", action='store_true', default=False, dest='verbose',
                      help='Output results to stdout even with -o options set')

    return parser


def _install_api_key(key):
    flag = False
    if key_manager.is_key_installed(google_map):
        answer = input("Google Map API key is already installed.\nDo you want to overwrite it with a new key? [y/n] ")
        if answer != 'Y' and answer != 'y':
            print("Using previously installed Google Maps API key...")
        else:
            flag = True
    else:
        flag = True

    if flag is True:
        print("Installing Google Maps API key...")
        key_manager.install_key(google_map, key)


def _get_addresses(input_file):
    with open(input_file) as fd:
        addresses = fd.readlines()
        return [x.strip() for x in addresses]


def _print_out(line, output_file=None, verbose=False):
    if not output_file:
        print(line)
    else:
        if verbose:
            print(line)
        with open(output_file, 'a') as fd:
            fd.write(line + '\n')


def main(argv=None):
    if argv is None:
        argv = sys.argv

    opt_parser = _config_options()
    (options, args) = opt_parser.parse_args(argv[1:])

    # Install API key
    if options.api_key is not None:
        _install_api_key(options.api_key)

    # Set input
    if options.input_file is not None:
        addresses = _get_addresses(options.input_file)
    elif args:
        addresses = [' '.join(args)]
    else:
        if options.api_key is None:
            opt_parser.print_help()
        return EXIT_OK

    # Set output
    if options.output_file:
        output_path = os.path.abspath(options.output_file)
        if os.path.exists(output_path):
            os.remove(output_path)
    else:
        output_path = None

    # Get API key
    api_key = key_manager.get_key(google_map)
    if api_key is None:
        logging.error('no Google Maps API key found, try to (re)install API key using -k option')
        opt_parser.print_help()
        return EXIT_API_KEY

    # Print header
    if options.full_response:
        _print_out('ID,RESPONSE', output_path, options.verbose)
    else:
        _print_out('ID,LAT,LON', output_path, options.verbose)

    geocoder = Geocoder(api_key)
    for i, a in enumerate(addresses):
        try:
            response = geocoder.get_response(a)
        except Exception as e:
            logging.error('[address #%d]: Google Maps: %s', i+1, e)
            if options.full_response:
                _print_out('{},'.format(i+1), output_path, options.verbose)
            else:
                _print_out('{},,'.format(i+1), output_path, options.verbose)
        else:
            if options.full_response:
                _print_out('{},"{}"'.format(i+1, response), output_path, options.verbose)
            else:
                lat, lng = get_lat_lng(response)
                _print_out('{},{},{}'.format(i+1, lat, lng), output_path, options.verbose)


if __name__ == '__main__':
    try:
        res = main()
    except Exception as err:
        logging.error(err)
    else:
        sys.exit(res)