"""Integrate a CSV/TSV file into a distant AskOmics"""

import os
from os.path import basename
import argparse

from libaskocli import askomics_auth
from libaskocli import askomics_url
from libaskocli import RequestApi

class Integrate(object):
    """Integrate a CSV/TSV file into a distant AskOmics"""

    def run(self, args):
        """Integrate a file into a distant askomics

        :param args: script's arguments
        :type args: Namespace
        """

        parser = argparse.ArgumentParser(prog='askocli integrate', description='Integrate data to a distant AskOmics')
        askomics_auth(parser)
        askomics_url(parser)
        parser.add_argument('file', nargs='?', type=str, action="store", help="file to integrate")
        parser.add_argument('--file-type', help='The file type')
        parser.add_argument('--public', action='store_true')
        parser.add_argument('--uri', help='Custom URI')

        # CSV args
        parser.add_argument('--headers', nargs='*', help='List of custom headers  (csv)')
        parser.add_argument('--key-columns', nargs='*', help='List of the key columns index  (csv)')
        parser.add_argument('--disabled-columns', nargs='*', help='List of columns index to disable  (csv)')
        parser.add_argument('-c', '--columns', nargs='*', help='List of forced columns types  (csv)')

        # GFF args
        parser.add_argument('-e', '--entities', nargs='*', help='List of entities to integrate  (gff)')

        # GFF and BED args
        parser.add_argument('-t', '--taxon', help='Taxon  (gff and bed)')

        # BED args
        parser.add_argument('-n', '--entity-name', help='Entity name  (bed)')

        args = parser.parse_args(args)

        url = args.askomics

        api = RequestApi(url, args.apikey, args.file_type)

        api.set_cookie()

        api.set_filepath(args.file)

        api.upload_file()

        api.set_visibility(args.public)

        ext = os.path.splitext(basename(args.file))[1].lower()

        if ext in ('.gff', '.gff2', '.gff3') or args.file_type == 'gff':
            api.integrate_gff(args.taxon, args.entities, args.uri)
        elif ext == '.ttl' or args.file_type == 'ttl':
            api.integrate_ttl()
        elif ext in ('.bed',) or args.file_type == 'bed':
            api.integrate_bed(args.entity_name, args.taxon, args.uri)
        else:
            if args.key_columns:
                api.set_key_columns(args.key_columns)
            if args.columns:
                api.force_col_types(args.columns)
            else:
                api.guess_col_types()
            if args.disabled_columns:
                api.set_disabled_columns(args.disabled_columns)
            api.set_headers(args.headers)
            api.integrate_data(args.uri)
