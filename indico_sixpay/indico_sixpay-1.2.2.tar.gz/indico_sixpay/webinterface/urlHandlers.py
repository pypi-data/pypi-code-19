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
from MaKaC.webinterface.urlHandlers import URLHandler as MainURLHandler

from .. import MODULE_ID


# Editor's Note  - MF@20170309
# These classes simply define URLs *on the indico server* which are open handles
# for external requests. The requestTag is used to search corresponding pages/actions
# in other submodules.


class EPURLHandler(MainURLHandler):
    _requestTag = ''

    @classmethod
    def getURL(cls, target=None, _ignore_static=False, **params):
        return super(EPURLHandler, cls).getURL(
            target, EPaymentName=MODULE_ID, requestTag=cls._requestTag, _ignore_static=False, **params
        )


# URLs for Indico to modify the plugin
class UHConfModifEPayment(EPURLHandler):
    _endpoint = 'event_mgmt.confModifEpayment-modifModule'


class UHConfModifEPaymentSixPay(UHConfModifEPayment):
    _requestTag = "modifSixPay"


class UHConfModifEPaymentSixPayDataModif(UHConfModifEPayment):
    _requestTag = "modifSixPayData"


class UHConfModifEPaymentSixPayPerformDataModif(UHConfModifEPayment):
    _requestTag = "modifSixPayPerformDataModif"


class UHPay(EPURLHandler):
    _endpoint = 'misc.payment'


# URLs given to the Six Pay service to call back after/during a transaction
class UHPayTransactionSuccess(UHPay):
    # redirect when the user completed the transaction
    _requestTag = "successlink"


class UHPayTransactionFaillink(UHPay):
    # redirect when the user could not be authorised
    _requestTag = "faillink"


class UHPayTransactionBacklink(UHPay):
    # redirect when the user aborts the transaction
    _requestTag = "backlink"


class UHPayTransactionNotifyUrl(UHPay):
    # endpoint for SixPay to confirm transaction WITHOUT user intervention
    _requestTag = "notifyurl"
