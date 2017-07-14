"""
Interfacing with the Grad Scho Petition Request API
"""
import logging
import json
from uw_grad.models import GradPetition
from uw_pws import PWS
from uw_grad import get_resource, parse_datetime


PREFIX = "/services/students/v1/api/petition?id="


logger = logging.getLogger(__name__)


def get_petition_by_regid(regid):
    """
    raise: InvalidRegID, DataFailureException
    """
    person = PWS().get_person_by_regid(regid)
    return get_petition_by_syskey(person.student_system_key)


def get_petition_by_syskey(system_key):
    url = "%s%s" % (PREFIX, system_key)
    return _process_json(json.loads(get_resource(url)))


def _process_json(data):
    """
    return a list of GradPetition objects.
    """
    requests = []
    for item in data:
        petition = GradPetition()
        petition.description = item.get('description')
        petition.submit_date = parse_datetime(item.get('submitDate'))
        petition.decision_date = parse_datetime(item.get('decisionDate'))

        if item.get('deptRecommend') and len(item.get('deptRecommend')):
            petition.dept_recommend = item.get('deptRecommend').lower()

        if item.get('gradSchoolDecision') and\
           len(item.get('gradSchoolDecision')):
            petition.gradschool_decision =\
                item.get('gradSchoolDecision').lower()
        requests.append(petition)
    return requests
