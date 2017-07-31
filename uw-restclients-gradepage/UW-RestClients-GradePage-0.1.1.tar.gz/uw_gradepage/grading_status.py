
"""
This is the interface for interacting with the GradePage Web Service.
"""

from dateutil.parser import parse
import logging
import simplejson as json
from uw_gradepage.models import GradingStatus
from uw_gradepage import get_resource
from restclients_core.exceptions import DataFailureException
try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote


url_prefix = "/api/v1/grading_status/"
logger = logging.getLogger(__name__)


def get_grading_status(section_id, act_as=None):
    """
    Return a restclients.models.gradepage.GradePageStatus object
    on the given course
    """
    url = "%s%s" % (url_prefix, quote(section_id))
    headers = {}

    if act_as is not None:
        headers["X-UW-Act-as"] = act_as

    response = get_resource(url, headers)
    return _object_from_json(url, response)


def _object_from_json(url, response_body):
    json_data = json.loads(response_body, use_decimal=True)
    return_obj = GradingStatus()

    gs_data = json_data.get('grading_status')
    if gs_data is None:
        raise DataFailureException(
            url, 500, "error: bogus resopnse data")

    return_obj.section_id = gs_data['section_id']
    return_obj.grading_period_open = gs_data['grading_period_open']
    return_obj.display_name = gs_data['display_name']
    return_obj.section_url = gs_data['section_url']
    return_obj.status_url = gs_data['status_url']
    return_obj.grading_status = gs_data['grading_status']

    try:
        return_obj.submitted_count = gs_data['submitted_count']
        return_obj.unsubmitted_count = gs_data['unsubmitted_count']
        return_obj.submitted_by = gs_data['submitted_by']
        return_obj.submitted_date = parse(gs_data["submitted_date"])
        return_obj.accepted_date = parse(gs_data["accepted_date"])
        return_obj.no_grades_submitted = False
    except KeyError:
        return_obj.no_grades_submitted = True

    return return_obj
