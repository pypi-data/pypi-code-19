import requests

from .base import (
    BaseHandler,
    Workaround,
)


class GithubHandler(BaseHandler):
    adjectives = {'closed', 'merged'}
    value_patterns = [
        r'.*github\.com\/(?P<user>[A-Za-z._-]*)\/(?P<repo>[A-Za-z._-]*)\/(?P<type>(pull(s)?|issue(s)?))\/(?P<id>\d+)'
    ]
    example_values = [
        'https://github.com/django/django/pull/8825/',
        'https://github.com/django/djangoproject.com/issues/775'
    ]

    GITHUB_URL = 'https://api.github.com/repos/{user}/{repo}/{type}/{id}'

    def extract_info_from_value(self, value):
        result = super().extract_info_from_value(value)
        if result and not result['type'].endswith('s'):
            result['type'] += 's'
        return result

    def is_result_equal(cls, result, adjective):
        if adjective == 'merged':
            return result['merged']

        return result['state'] == adjective

    def get_result(self, workaround: Workaround, parsed_value):
        res = requests.get(self.GITHUB_URL.format(**parsed_value)).json()
        return {'merged': res.get('merged'), 'state': res['state']}
