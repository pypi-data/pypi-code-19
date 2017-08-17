from __future__ import print_function
from argparse import ArgumentParser
import requests
import sys

url = 'https://coveralls.io/builds/{}.json'


def message(args, data, template):
    print(template.format(
        args.commit, data["covered_percent"], args.fail_under
    ))


def main():
    parser = ArgumentParser()
    parser.add_argument('commit', help='the commit hash to check')
    parser.add_argument('--fail-under', type=float, default=100,
                        help='Exit with a status of 2 if the total coverage is '
                             'less than MIN.')
    args = parser.parse_args()

    response = requests.get(url.format(args.commit))
    data = response.json()

    if data["covered_percent"] < args.fail_under:
        message(args, data, 'Failed coverage check for {} as {} < {}')
        sys.exit(2)
    else:
        message(args, data, 'Coverage OK for {} as {} >= {}')

