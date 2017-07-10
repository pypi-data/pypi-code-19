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

from MaKaC.webinterface.pages import conferences
from MaKaC.webinterface.pages import registrationForm
from MaKaC.webinterface import wcomponents
from xml.sax.saxutils import quoteattr

from ..wcomponents import WTemplated
from .. import urlHandlers as localUrlHandlers
from ... import MODULE_ID


# Editor's Note  - MF@20170309
# * The W<.....> classes build templates pages
# Thanks to Magic [TM] indico pulls the templates from the `tpls` folder
# This is done using the class name MINUS THE FIRST CHARACTER. Example:
# class WConfModifEPaymentSixPay => ConfModifEPaymentSixPay.tpl
# * These classes are used by the RequestHandlers if they need to display stuff


class WPConfModifEPaymentSixPayBase(registrationForm.WPConfModifRegFormBase):
    def _createTabCtrl(self):
        self._tabCtrl = wcomponents.TabControl()
        self._tabMain = self._tabCtrl.newTab(
            "main",
            "Main",
            localUrlHandlers.UHConfModifEPaymentSixPay.getURL(self._conf)
        )
        wf = self._rh.getWebFactory()
        if wf:
            wf.customiseTabCtrl(self._tabCtrl)
        self._setActiveTab()

    def _setActiveTab(self):
        pass

    def _setActiveSideMenuItem(self):
        self._regFormMenuItem.setActive(True)

    def _getPageContent(self, params):
        self._createTabCtrl()
        banner = wcomponents.WEpaymentBannerModif(self._conf.getModPay().getPayModByTag(MODULE_ID),
                                                  self._conf).getHTML()
        html = wcomponents.WTabControl(self._tabCtrl, self._getAW()).getHTML(self._getTabContent(params))
        return banner + html

    def _getTabContent(self, params):
        return "nothing"


class WPConfModifEPaymentSixPay(WPConfModifEPaymentSixPayBase):
    def _getTabContent(self, params):
        wc = WConfModifEPaymentSixPay(self._conf)
        p = {
            'dataModificationURL': quoteattr(
                str(localUrlHandlers.UHConfModifEPaymentSixPayDataModif.getURL(self._conf)))
        }
        return wc.getHTML(p)

    def display(self, **params):
        result = WPConfModifEPaymentSixPayBase.display(self, **params)
        return result


class WConfModifEPaymentSixPay(WTemplated):
    def __init__(self, conference):
        WTemplated.__init__(self)
        self._conf = conference

    def getVars(self):
        """
        Current settings of this EPayment Module for display

        Displayed via `tpls/ConfModifEPaymentSixPay.tpl`.
        """
        _vars = WTemplated.getVars(self)
        modSixPay = self._conf.getModPay().getPayModByTag(MODULE_ID)
        _vars.update(modSixPay.getValues())
        return _vars


class WPConfModifEPaymentSixPayDataModif(WPConfModifEPaymentSixPayBase):
    def _getTabContent(self, params):
        wc = WConfModifEPaymentSixPayDataModif(self._conf)
        p = {'postURL': quoteattr(str(localUrlHandlers.UHConfModifEPaymentSixPayPerformDataModif.getURL(self._conf)))}
        return wc.getHTML(p)


class WConfModifEPaymentSixPayDataModif(WConfModifEPaymentSixPay):
    def __init__(self, conference):
        WTemplated.__init__(self)
        self._conf = conference

    def getVars(self):
        """
        Current settings of this EPayment Module for modification

        Displayed via `tpls/ConfModifEPaymentSixPayDataModif.tpl`.
        """
        return WConfModifEPaymentSixPay.getVars(self)


# Pages for the Six Pay service to call back after/during a transaction
class WPTransactionUserCallback(conferences.WPConferenceDefaultDisplayBase):
    """Request Handler for Callbacks the User is directed to"""
    #: display page after handling transaction
    display_template = None
    #: overwrite message on the displayed page
    message = None
    #: overwrite message detail on the displayed page
    message_detail = None

    def __init__(self, rh, conf, reg):
        conferences.WPConferenceDefaultDisplayBase.__init__(self, rh, conf)
        self._registrant = reg

    def _getBody(self, params):
        assert self.display_template is not None, "Callbacks must set display template for users"
        wc = self.display_template(self._conf, self._registrant)
        if self.message is not None:
            wc.message = self.message
        if self.message_detail is not None:
            wc.message_detail = self.message_detail
        return wc.getHTML()

    def _defineSectionMenu(self):
        conferences.WPConferenceDefaultDisplayBase._defineSectionMenu(self)
        self._sectionMenu.setCurrentItem(self._regFormOpt)


class WTransactionUserCallback(WTemplated):
    message = None
    message_detail = None

    def __init__(self, configuration, registrant):
        WTemplated.__init__(self)
        self._registrant = registrant
        self._conf = configuration

    def getVars(self):
        vars = WTemplated.getVars(self)
        assert self.message is not None, "Callbacks must set display message for users"
        vars["message"] = self.message
        vars["message_detail"] = self.message_detail or (
            "Registrant: %s %s" % (self._registrant.getFirstName(), self._registrant.getSurName())
        )
        return vars


class WTransactionSuccesslink(WTransactionUserCallback):
    """redirect when the user completed the transaction"""
    message = "Your payment has been successfully processed"


class WPTransactionSuccesslink(WPTransactionUserCallback):
    """redirect when the user completed the transaction"""
    display_template = WTransactionSuccesslink


class WTransactionFaillink(WTransactionUserCallback):
    """redirect when the user could not be authorised"""
    message = "You could not be authorised by the payment service"


class WPTransactionFaillink(WPTransactionUserCallback):
    """redirect when the user could not be authorised"""
    display_template = WTransactionFaillink


class WTransactionBacklink(WTransactionUserCallback):
    """redirect when the user aborts the transaction"""
    message = "You have aborted the transaction"


class WPTransactionBacklink(WPTransactionUserCallback):
    """redirect when the user aborts the transaction"""
    display_template = WTransactionBacklink
