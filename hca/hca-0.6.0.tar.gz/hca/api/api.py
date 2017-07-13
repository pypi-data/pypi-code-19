from __future__ import absolute_import, division, print_function, unicode_literals

import json, sys, os
from io import open
import requests
from .parser import get_parser


class GetBundles:
    """Class containing information to reach this endpoint."""

    command = "get_bundles"
    param_data = {"some": "param_data"}

    @classmethod
    def run(cls, uuid, version=None, replica=None):
        """Function that will be exposed to the api users."""
        pass

    @classmethod
    def run_cli():
        """Run this command using args from the cli."""
        pass

    @classmethod
    def add_parser():
        """Add a parser."""
        pass
