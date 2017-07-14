"""
This is the interface for interacting with the UW Libraries Web Service.
"""

from uw_libraries.dao import MyLib_DAO
from uw_libraries.models import MyLibAccount
from restclients_core.exceptions import DataFailureException
from datetime import datetime
from logging import getLogger
import json


mylib_url_prefix = '/mylibinfo/v1/'
logger = getLogger(__name__)


def _get_mylib_resource(url):
    response = MyLib_DAO().getURL(url, {})
    logger.info("%s ==status==> %s" % (url, response.status))

    if response.status != 200:
        raise DataFailureException(url, response.status, response.data)

    # 'Bug' with lib API causing requests with no/invalid user to return a 200
    if "User not found" in response.data:
        raise DataFailureException(url, 404, response.data)

    logger.debug("%s ==data==> %s" % (url, response.data))
    return response.data


def _get_account(netid, timestamp=None, is_html=False):
    url = "%s?id=%s" % (mylib_url_prefix, netid)

    if timestamp is not None:
        url += "&timestamp=%s" % timestamp

    if is_html:
        url += "&style=html"

    return _get_mylib_resource(url)


def get_account(netid, timestamp=None):
    """
    The Libraries object has a method for getting information
    about a user's library account
    """
    response = _get_account(netid, timestamp=timestamp)
    return _account_from_json(response)


def get_account_html(netid, timestamp=None):
    """
    The Libraries object has a method for getting information
    about a user's library account
    """
    return _get_account(netid, timestamp=timestamp, is_html=True)


def _account_from_json(body):
    try:
        account_data = json.loads(body)
    except Exception as ex:
        raise Exception("Unable to parse library data: %s.  Exception: %s" % (
            body, ex))
    account = MyLibAccount()
    account.fines = account_data["fines"]
    account.holds_ready = account_data["holds_ready"]
    account.items_loaned = account_data["items_loaned"]
    if account_data.get("next_due") is None:
        account.next_due = None
    else:
        account.next_due = datetime.strptime(account_data["next_due"],
                                             "%Y-%m-%d").date()
    return account
