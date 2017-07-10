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
from __future__ import absolute_import, division
from MaKaC.webinterface import wcomponents
import os
import pkg_resources
import MaKaC.common.Configuration as Configuration

import indico_sixpay as pay_plugin


# Editor's Note  - MF@20170309
# This file exists only as an auxiliary to .pages.ePayments
# I have no idea why it is separate


class WTemplated(wcomponents.WTemplated):
    # Editor's Note  - MF@20170309
    # If you are wondering how tplId is set:
    #   WTemplated sets it at an arbitrary time after __init__ in getHTML (!!!) to
    # self.tplId = self.__class__.__name__[1:]
    def _setTPLFile(self):
        """
        Guesses the TPL (template) file for the object. It will try to get
        from the configuration if there's a special TPL file for it and
        if not it will look for a file called as the class name+".tpl"
        in the configured TPL directory.
        """
        cfg = Configuration.Config.getInstance()
        tpl_dir = pkg_resources.resource_filename(pay_plugin.__name__, "tpls")
        tpl_file = cfg.getTPLFile(self.tplId)
        if tpl_file == "":
            tpl_file = "%s.tpl" % self.tplId
        self.tplFile = os.path.join(tpl_dir, tpl_file)
        hfile = self._getSpecificTPL(
            os.path.join(tpl_dir, 'chelp'),
            self.tplId,
            extension='wohl',
        )
        self.helpFile = os.path.join(tpl_dir, 'chelp', hfile)
