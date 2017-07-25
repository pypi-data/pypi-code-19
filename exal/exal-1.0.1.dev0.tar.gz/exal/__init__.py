__author__ = 'Kevin'

import logging
from drivers.basedriver import BaseDriver

logger = logging.getLogger(__name__)
DRIVERS = {}

PRIORITY = [
    "win32com",
    "xlwings",
    "comtype",
    "openpyxl",
]

def EXAL(drivername="win32com", use_alternative = True):
    """

    :param drivername: Name of the Driver
    :type drivername: str
    :return: Driver instance
    :rtype: BaseDriver
    """

    _loaddriver(drivername)

    if not drivername in DRIVERS.keys():
        if use_alternative:
            alt_drivername = None
            for dn in PRIORITY:
                _loaddriver(dn)
                if dn in DRIVERS.keys():
                    alt_drivername = dn
                    break
            if alt_drivername is None:
                raise EXALDriverNotFound(drivername)

            logger.warning("Driver '{0}' not found, used instead '{1}'".format(drivername, alt_drivername))
            return DRIVERS[alt_drivername]
        else:
            raise EXALDriverNotFound(drivername)

    return DRIVERS[drivername]

def EXAL_shutdown():
    for driver in DRIVERS.values():
        driver.shutdown()

def _loaddriver(name):
    if name in DRIVERS.keys():
        return

    logger.debug("Loading driver '{0}'".format(name))

    if name == "xlwings":
        try:
            from drivers import xlwingsdriver
            DRIVERS["xlwings"] = xlwingsdriver.XLWingsDriver()
        except Exception, ex:
            logger.warning("Exception while loading EXAL Driver 'exlwings' : " + repr(ex))
    elif name == "comtype":
        try:
            from drivers import comtypedriver
            DRIVERS["comtype"] = comtypedriver.ComTypeDriver()
        except Exception, ex:
            logger.warning("Exception while loading EXAL Driver 'comtype' : " + repr(ex))
    elif name == "openpyxl":
        try:
            from drivers import openpyxldriver
            DRIVERS["openpyxl"] = openpyxldriver.OpenpyxlDriver()
        except Exception, ex:
            logger.warning("Exception while loading EXAL Driver 'openpyxl' : " + repr(ex))
    elif name == "win32com":
        try:
            from drivers import win32comdriver
            DRIVERS["win32com"] = win32comdriver.Win32ComDriver()
        except Exception, ex:
            logger.warning("Exception while loading EXAL Driver 'win32com' : " + repr(ex))

class EXALDriverNotFound(Exception):
    """  """
    def __init__(self, driver):
        """

        :param driver: Name of Driver
        :type driver: str
        :return:
        """
        super(EXALDriverNotFound, self).__init__(self, "Driver '{0}' not found".format(driver))
