"""
Contains IASystem DAO implementations.
"""

import logging
import os
from os.path import abspath, dirname
from restclients_core.dao import DAO


def IASystem_DAO(campus):
    return {
        "seattle": IASystem_UW_DAO,
        "bothell": IASystem_UWB_DAO,
        "tacoma": IASystem_UWT_DAO
    }[campus]()


class IASystem_UW_DAO(DAO):
    def service_name(self):
        return 'iasystem_uw'

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]


class IASystem_UWB_DAO(IASystem_UW_DAO):
    def service_name(self):
        return 'iasystem_uwb'


class IASystem_UWT_DAO(IASystem_UW_DAO):
    def service_name(self):
        return 'iasystem_uwt'
