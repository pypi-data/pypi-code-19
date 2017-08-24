"""
Influence Types and Use Case Examples

1. Sorts/Searches: Define choice set sortings under specific conditions
2. Defaults: Set order field value defaults under specific conditions
3. Recommendations: Suggest documentation, orders, analyses, and patient engagements
4. Rationales: Request or require rationales when behavior diverges from protocols
5. Tasks: Assign a task to a user

Below is a small sample of the 200+ events in charting and coordination available for subscription.

Charting Events

CHART_OPENED, CHART_QUERIED, PRESCRIPTION_ORIGINATED, PRESCRIPTION_COMMITTED, REFERRAL_ORIGINATED,
REFERRAL_COMMITTED, NOTE_LOCKED, ...

Care Coordination Events

APPOINTMENT_SCHEDULED, PATIENT_ARRIVED, PATIENT_ROOMED, REFILL_REQUEST_RECEIVED,
REFERRAL_LOOP_CLOSED, POPULATION_QUERIED, MULTIPATIENT_ACTION_ORIGINATED, ...
"""

import importlib
import pkgutil

from collections import defaultdict

import arrow

from .patient import Patient
from .timeframe import Timeframe


class Protocol(object):

    responds_to_event_types = []

    def __init__(self, patient, **kwargs):
        self.patient = patient


class ClinicalQualityMeasure(Protocol):
    """
    Example CQMs:

    - pneumonia
    - depression screening
    """

    def __init__(self, timeframe=None, **kwargs):
        super().__init__(**kwargs)

        if timeframe:
            self.timeframe = timeframe
        else:
            now = arrow.utcnow()

            self.timeframe = Timeframe(start=now, end=now)

    def get_narrative_recommendations(self):
        return {}

    def in_initial_population(self):
        raise NotImplementedError('in_initial_population must be overridden')

    def in_denominator(self):
        raise NotImplementedError('in_denominator must be overridden')

    def in_numerator(self):
        raise NotImplementedError('in_numerator must be overridden')

    # TODO move to ClinicalQualityMeasureReport class
    # def report(self):
    #     """
    #     Report aggregate statistical information on patients who are included or excluded from this
    #     protocol's criteria.
    #     """
    #     return {}


def get_subclasses(cls):
    subclasses = []

    for subclass in cls.__subclasses__():
        subclasses.append(subclass)
        subclasses.extend(get_subclasses(subclass))

    return subclasses


def get_protocols(module):
    for _, name, _ in pkgutil.iter_modules(module.__path__):
        importlib.import_module(f'{module.__name__}.{name}')

    subclasses = get_subclasses(Protocol)
    protocols_by_event_type = defaultdict(list)

    for subclass in subclasses:
        if subclass in (Protocol, ClinicalQualityMeasure):
            continue

        for event_type in subclass.responds_to_event_types:
            protocols_by_event_type[event_type].append(subclass)

    return protocols_by_event_type


def protocols_for_patient(protocols, event_type, patient_key):
    patient = Patient(patient_key)

    return [protocol(patient=patient) for protocol in protocols[event_type]]
