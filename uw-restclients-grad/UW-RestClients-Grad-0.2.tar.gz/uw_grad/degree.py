"""
Interfacing with the Grad Scho Degree Request API
"""
import logging
import json
from uw_grad.models import GradDegree
from uw_pws import PWS
from uw_grad import get_resource, parse_datetime


PREFIX = "/services/students/v1/api/request?id="
SUFFIX = "&exclude_past_quarter=true"


logger = logging.getLogger(__name__)


def get_degree_by_regid(regid):
    """
    raise: InvalidRegID, DataFailureException
    """
    person = PWS().get_person_by_regid(regid)
    return get_degree_by_syskey(person.student_system_key)


def get_degree_by_syskey(system_key):
    url = "%s%s%s" % (PREFIX, system_key, SUFFIX)
    return _process_json(json.loads(get_resource(url)))


def _process_json(json_data):
    """
    return a list of GradDegree objects.
    """
    requests = []
    for item in json_data:
        degree = GradDegree()
        degree.degree_title = item["degreeTitle"]
        degree.exam_place = item["examPlace"]
        degree.exam_date = parse_datetime(item.get("examDate"))
        degree.req_type = item["requestType"]
        degree.major_full_name = item["majorFullName"]
        degree.submit_date = parse_datetime(item.get("requestSubmitDate"))
        degree.decision_date = parse_datetime(item.get('decisionDate'))
        degree.status = item["status"]
        degree.target_award_year = item["targetAwardYear"]
        if item.get("targetAwardQuarter")and\
           len(item.get("targetAwardQuarter")):
            degree.target_award_quarter = item["targetAwardQuarter"].lower()

        requests.append(degree)
    return requests
