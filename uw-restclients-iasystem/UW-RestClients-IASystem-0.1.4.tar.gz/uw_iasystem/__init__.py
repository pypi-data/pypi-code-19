import json
import logging
from restclients_core.exceptions import DataFailureException
from uw_iasystem.dao import IASystem_DAO
from uw_iasystem.exceptions import TermEvalNotCreated


logger = logging.getLogger(__name__)


def get_resource_by_campus(url, campus):
    return get_resource(url, campus)


def get_resource(url, campus):
    """
    Issue a GET request to IASystem with the given url
    and return a response in Collection+json format.
    :returns: http response with content in json
    """
    headers = {"Accept": "application/vnd.collection+json"}
    response = IASystem_DAO(campus).getURL(url, headers)
    status = response.status
    logger.info("%s ==status==> %s", url, status)
    if status != 200:
        message = response.data
        logger.error("%s ==data==> %s", url, message)
        if status == 400:
            if "Term is out of range" in response.data:
                raise TermEvalNotCreated(url, status, message)
        raise DataFailureException(url, status, message)

    return json.loads(response.data)
