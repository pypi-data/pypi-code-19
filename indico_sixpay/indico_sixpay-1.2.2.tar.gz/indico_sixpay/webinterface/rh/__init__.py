# -*- coding: utf-8 -*-
##
## This file is part of the SixPay Indico EPayment Plugin.
## Copyright (C) 2017 Max Fischer
##
## This is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 3 of the
## License, or (at your option) any later version.
##
## This software is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Indico;if not, see <http://www.gnu.org/licenses/>.
from __future__ import print_function, absolute_import

modules = {}


def getRHByTag(self, tag):
    """Do the link between url handlers and request handlers"""
    for mod in self.modules.values():
        for RH in mod.__dict__.keys():
            try:
                if mod.__dict__[RH]._requestTag == tag:
                    return mod.__dict__[RH]
            except:
                pass


def preprocessParams(params):
    return True
