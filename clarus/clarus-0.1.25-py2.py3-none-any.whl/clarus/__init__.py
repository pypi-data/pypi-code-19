#Name: clarus.py
#Runtimes: Python,Python_Lambda
#Leave blank line below to mark end of header

from __future__ import print_function
from six.moves import urllib
import requests
import json
import os
import sys
import logging

from clarus.services import compliance, credit, dates, etd, frtb, hedge, load, margin, market, portfolio, profitloss, risk, sdr, simm, trade, util, xva
from clarus.api_config import ApiConfig
from clarus.models import ApiResponse
from clarus.output_types import *
from clarus.api import request
from clarus.resource_util import read

__version__ = '0.1.25'