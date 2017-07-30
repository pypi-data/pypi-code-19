import requests
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name
from packaging.version import parse

from .base import (
    BaseHandler,
    Workaround,
)


class PyPiHandler(BaseHandler):
    adjectives = {'released'}
    value_patterns = [
        r'^pypi:(?P<value>.*)'
    ]
    example_values = [
        'pypi:Django>=2.0',
        'pypi:colorama~=3.4',
    ]

    PYPI_URL = 'https://pypi.python.org/pypi/{package}/json'

    def get_result(self, workaround: Workaround, parsed_value):
        parsed_value = Requirement(parsed_value['value'])
        package_name = canonicalize_name(parsed_value.name)

        pypi_response = requests.get(self.PYPI_URL.format(package=package_name)).json()
        releases = list(parse(v) for v in pypi_response['releases'].keys())

        return 'released' if any(parsed_value.specifier.filter(releases)) else 'unreleased'
