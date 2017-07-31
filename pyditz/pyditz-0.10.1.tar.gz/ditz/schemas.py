"""
Data validation schemas.
"""

from __future__ import print_function

from .flags import TYPE, STATUS, RELSTATUS, DISPOSITION


def option(iterable, **kw):
    kw.update(type='string', allowed=list(iterable))
    return kw


def listof(schema, **kw):
    kw.update(type='list', schema=schema)
    return kw


def datetime(**kw):
    kw.update(type='datetime')
    return kw


def string(**kw):
    kw.update(type='string')
    return kw


event = {'type': 'list',
         'items': [datetime(), string(), string(), string()]}

issue = {'title': string(required=True, empty=False),
         'desc': string(required=True),
         'type': option(TYPE.keys(), required=True),
         'component': string(required=True),
         'release': string(required=True, default=None, nullable=True),
         'reporter': string(required=True),
         'claimer': string(default=None, nullable=True),
         'status': option(STATUS.keys()),
         'disposition': option(DISPOSITION.keys(), nullable=True),
         'creation_time': datetime(required=True),
         'references': listof(string(), required=True),
         'id': string(required=True, regex=r'[0-9a-f]{40}'),
         'log_events': listof(event, required=True)}

component = {'name': string(required=True, empty=False)}

release = {'name': string(required=True, empty=False),
           'status': option(RELSTATUS.keys(), nullable=True),
           'release_time': datetime(nullable=True),
           'log_events': listof(event)}

project = {'name': string(required=True, empty=False),
           'version': string(required=True),
           'components': listof(component, required=False),
           'releases': listof(release)}


if __name__ == "__main__":
    from pprint import pprint

    for name, schema in (('Issue', issue),
                         ('Release', release),
                         ('Component', component),
                         ('Project', project)):

        print()
        print('***', name, '***')
        pprint(schema)
