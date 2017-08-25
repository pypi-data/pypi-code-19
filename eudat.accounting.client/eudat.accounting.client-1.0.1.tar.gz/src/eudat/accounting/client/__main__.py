# -*- coding: utf-8 -*-
"""
=======================
eudat.accounting.client
=======================

Command line handling
"""

import argparse
import logging
import sys

from eudat.accounting.client import __version__, LOG, utils


def main(argv=sys.argv):
    """Main function called from console command
    """
    logging.basicConfig(filename='.accounting.log', level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    exit_code = 1
    try:
        app = Application(argv)
        app.run()
        exit_code = 0
    except KeyboardInterrupt:
        exit_code = 0
    except Exception as exc:
        LOG.exception(exc)
    sys.exit(exit_code)


class Application(object):
    """
    The main Application class

    :param argv: The command line as a list as ``sys.argv``
    """
    def __init__(self, argv):
        ap = argparse.ArgumentParser()
        ap.add_argument('--version', action='version', version=__version__)
        ap.add_argument('account',
                        help='account to be used. Typically the (P)ID of the '\
                        'resource to be accounted')
        ap.add_argument('value', help='The value to be recorded')
        ap.add_argument('unit', nargs='?', default='byte', 
                        help='The unit of measurement for the value provided. '\
                        'Default: "byte"')
        ap.add_argument('-b', '--base_url', default='https://accounting.eudat.eu',
                        help='base URL of the accounting server to use. '\
                        'Default: https://accounting.eudat.eu')

        ap.add_argument('-u', '--user', default='',
                        help='user id used for logging into the server. '\
                        'If not provided it is looked up in the environment variable '\
                        '"ACCOUNTING_USER". ' \
                        'Default: "" - aka not set')

        ap.add_argument('-p', '--password', default='',
                        help='password used for logging into the server. '\
                        'If not provided it is looked up in the environment variable '\
                        '"ACCOUNTING_PW". ' \
                        'Default: "" - aka not set')

        ap.add_argument('-d', '--domain', default='eudat',
                        help='name of the domain holding the account. '\
                        'Default: eudat')

        ap.add_argument('-s', '--service', default='',
                        help='UID (or PID) of the registered service component reporting '\
                        'the record. '\
                        'Default: "" - not set')

        ap.add_argument('-n', '--number', default='',
                        help='number of objects associated with this accounting record. '\
                        'This is EUDAT specific. '\
                        'Default: "" - not set')
        
        ap.add_argument('-o', '--object_type', default='registered objects',
                        help='object type for the number of objects specified with "-n". '\
                        'This is EUDAT specific. '\
                        'Default: "registered objects"')

        utils.addCommonArguments(ap)

        self.args = ap.parse_args(args=argv[1:])
        """Arguments of your app"""

    def run(self):
        LOG.info("addRecord called with: " + str(self.args))
        credentials = utils.getCredentials(self.args)
        url = utils.getUrl(self.args)
        data = utils.getData(self.args)
        if not self.args.test:
            response = utils.call(credentials, url, data)
            if self.args.verbose:
                print(response.text)
            if not response.ok:
                LOG.error("status: %s" % response.status_code)
                sys.exit(str(response.status_code))
            LOG.info("status: %s -- record key: %s" % (response.status_code,
                                                       response.text))
        else:
            print("Dry run; would call %s with %s" % (url, data))

if __name__ == '__main__':
    main()
