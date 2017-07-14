"""
Contains UW Library DAO implementations.
"""
from restclients_core.dao import DAO
from os.path import abspath, dirname
import os


class MyLib_DAO(DAO):
    def service_name(self):
        return "libraries"

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]


class SubjectGuide_DAO(DAO):
    def service_name(self):
        return "libcurrics"

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]
