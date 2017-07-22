from __future__ import unicode_literals, print_function

import argparse
import json
import os
import sys

from .api import BelugaAPI
from .exceptions import InvalidCredentials


def error(message):
    print(message, file=sys.stderr)
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='BelugaCDN API Tool')
    parser.add_argument('--token-id', dest='token_id', default=os.environ.get("BELUGA_TOKEN_ID", None),
                        help='API Token ID, may be specified with BELUGA_TOKEN_ID environment variable')
    parser.add_argument('--token-secret', dest='token_secret', default=os.environ.get("BELUGA_TOKEN_SECRET", None),
                        help='API Token Secret, may be specified with BELUGA_TOKEN_SECRET environment variable')
    parser.add_argument('--username', dest='username', default=os.environ.get("BELUGA_USERNAME", None),
                        help='Beluga account username, may be specified with BELUGA_USERNAME environment variable')
    parser.add_argument('--password', dest='password', default=os.environ.get("BELUGA_PASSWORD", None),
                        help='Beluga account password, may be specified with BELUGA_PASSWORD environment variable')
    parser.add_argument('--base-url', dest='base_url', default=os.environ.get("BELUGA_BASE_URL", 'https://api.belugacdn.com'),
                        help='API Base URL')
    parser.add_argument(
        '--body', dest='body', help='JSON body to post, prepend with @ to read from file', default=None)
    parser.add_argument(
        '--method', dest='method', default='GET', help='GET|POST|PUT|DELETE')
    parser.add_argument(
        '--service', dest='service', default='api/cdn/v2', help='API Service Name')
    parser.add_argument(
        '--path', dest='path', default='identity', help='API Request Path')
    parser.add_argument('--pretty', dest='pretty', default=False,
                        help='prettify JSON output', action='store_true')
    parser.add_argument('--print', dest='print', default=False,
                        help='print JSON result to stdout', action='store_true')
    parser.add_argument('--silent', dest='silent', default=False,
                        help='inhibit default json result printing', action='store_true')
    parser.add_argument('--accept', dest='accept',
                        default='application/json', help='accept content-type')
    parser.add_argument(
        '--write', dest='write', default=False, help='write JSON result to a file')

    args = parser.parse_args()
    ssl_verify = True

    try:
        api = BelugaAPI(args.token_id, args.token_secret, args.username,
                        args.password, args.base_url, args.accept)
    except InvalidCredentials:
        error("--token-id and --token-secret OR --username and --password "
              "are required")

    if args.silent is False and getattr(args, 'print') is False and args.write is False:
        setattr(args, 'print', True)
        args.pretty = True

    if args.body:
        if args.method not in ['POST', 'PUT']:
            error("method must be POST|PUT if body is specified")
        if args.body[0] == "@":
            body_fh = open(args.body[1:], "r")
            body_json = json.load(body_fh)
            body_fh.close()
        else:
            body_json = json.loads(args.body)
    else:
        if args.method not in ['GET', 'DELETE']:
            error("method must be GET|DELETE if body is not specified")
        body_json = None

    if len(args.service) > 0:
        url = "%s/%s" % (args.service, args.path)
    else:
        url = "%s" % (args.path,)

    response = api.request(args.method, url, json=body_json, verify=ssl_verify)

    if args.accept == 'application/json':
        try:
            json_response = response.json()
        except ValueError:
            print(response.text)
            return

        if getattr(args, 'print'):
            if args.pretty:
                print(json.dumps(json_response, indent=2))
            else:
                print(json.dumps(json_response))

        if args.write:
            write_fh = open(args.write, "w")
            if args.pretty:
                json.dump(write_fh, json_response, indent=2)
            else:
                json.dump(write_fh, json_response)
            write_fh.close()
    else:
        print(response.text)

if __name__ == "__main__":
    main()
