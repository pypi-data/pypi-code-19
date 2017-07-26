import pkg_resources

from bitfusion.bfapi import BFApi

VERSION = pkg_resources.require('bitfusion')[0].version
