from datetime import datetime

from regulations.generator import api_reader
from regulations.generator.layers.utils import convert_to_python


def fetch_regulations_and_future_versions():
    """ Returns a dict for all the regulations in the API. The dict includes
    lists of future versions for each regulation. """
    client = api_reader.ApiReader()
    all_versions = client.all_regulations_versions()
    all_versions = convert_to_python(all_versions)

    regulations_future = {}

    # We're only interested in future endpoint versions
    for v in all_versions['versions']:
        if v['regulation'] not in regulations_future:
            regulations_future[v['regulation']] = []
        if 'by_date' in v:
            regulations_future[v['regulation']].append(v)
    return regulations_future


def fetch_grouped_history(part):
    client = api_reader.ApiReader()
    versions = [
        version for version in client.regversions(part)['versions']
        if 'by_date' in version
    ]
    for version in versions:
        version['notices'] = []
    versions = sorted(convert_to_python(versions), reverse=True,
                      key=lambda v: v['by_date'])

    today = datetime.today()
    seen_current = False

    for version in versions:
        if version['by_date'] > today:
            version['timeline'] = 'future'
        elif not seen_current:
            seen_current = True
            version['timeline'] = 'current'
        else:
            version['timeline'] = 'past'

    for notice in client.notices(part)['results']:
        notice = convert_to_python(notice)
        for version in versions:
            if version['by_date'] == notice.get('effective_on'):
                version['notices'].append(notice)

    for version in versions:
        version['notices'] = sorted(version['notices'], reverse=True,
                                    key=lambda n: n['publication_date'])

    return versions
