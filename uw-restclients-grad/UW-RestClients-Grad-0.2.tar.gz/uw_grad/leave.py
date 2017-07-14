"""
Interfacing with the GradScho Degree Request API
"""
import logging
import json
from uw_grad.models import GradLeave, GradTerm
from uw_pws import PWS
from uw_grad import get_resource, parse_datetime


PREFIX = "/services/students/v1/api/leave?id="


logger = logging.getLogger(__name__)


def get_leave_by_regid(regid):
    """
    raise: InvalidRegID, DataFailureException
    """
    person = PWS().get_person_by_regid(regid)
    return get_leave_by_syskey(person.student_system_key)


def get_leave_by_syskey(system_key):
    url = "%s%s" % (PREFIX, system_key)
    return _process_json(json.loads(get_resource(url)))


def _process_json(data):
    """
    return a list of GradLeave objects.
    """
    requests = []
    for item in data:
        leave = GradLeave()
        leave.reason = item.get('leaveReason')
        leave.submit_date = parse_datetime(item.get('submitDate'))
        if item.get('status') and len(item.get('status')):
            leave.status = item.get('status').lower()

        for quarter in item.get('quarters'):
            term = GradTerm()
            term.quarter = quarter.get('quarter').lower()
            term.year = quarter.get('year')
            leave.terms.append(term)
        requests.append(leave)
    return requests
