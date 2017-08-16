import os

import arrow
import requests

CLINICAL_DATA_URL = os.getenv('CLINICAL_DATA_URL', 'https://cab-cds.canvasmedical.com')

CODE_SYSTEM_MAPPING = {
    'icd10cm': 'ICD-10',
    'icd10pcs': 'ICD-10',
    'snomedct': 'http://snomed.info/sct',
}

SYSTEM_CODE_MAPPING = {
    'ICD-10': ['icd10cm', 'icd10pcs'],
    'http://snomed.info/sct': 'snomedct',
}

VALID_SYSTEMS = [
    'icd10cm',
    'icd10pcs',
    'snomedct',
]


# TODO copied from canvas/pharmacy; move to CDS client library
def get_canvas_patient(patient_key):
    response = requests.get(f'{CLINICAL_DATA_URL}/Patient/{patient_key}')

    if response.status_code != 200:
        raise Exception(f"Patient '{patient_key}' not found")

    return response.json()


# TODO add to future CDS client library
# TODO generalize pagination; use cursors
def get_canvas_patient_conditions(patient_key, page_size=100):
    all_conditions = []
    offset = 0
    total = -1

    # XXX could run indefinitely if condition is added after first loop, would cursor pagination be
    # better?
    while len(all_conditions) != total:
        response = requests.get(f'{CLINICAL_DATA_URL}/Condition/'
                                f'?patient__key={patient_key}&offset={offset}&limit={page_size}')

        conditions = response.json()

        if total < 0:
            total = conditions['total']

        all_conditions.extend(conditions['entry'])

        offset += page_size

    return all_conditions


class Patient(object):
    """
    Wrapper around a Canvas patient to add convenience methods specific to science functionality.
    """

    def __init__(self, patient_key):
        # TODO replace this with call to CDS 'Chart' DRF view (to be created) that serializes
        # labs/meds/everything else
        self.patient_data = get_canvas_patient(patient_key)
        self.patient_conditions = get_canvas_patient_conditions(patient_key)

    @property
    def age(self):
        return float(self.patient_data['age'])

    # TODO timezones
    def age_at(self, time):
        birth_date = arrow.get(self.patient_data['birthDate'])

        return (time - birth_date).years

    def has_vaccine(self):
        pass

    def has_visit_within(self, timeframe):
        pass

    def gather_conditions(self, **kwargs):
        conditions = []
        systems = [key for key, _ in kwargs.items() if key in VALID_SYSTEMS]

        for condition in self.patient_conditions:
            for coding in condition['code']['coding']:
                system = SYSTEM_CODE_MAPPING[coding['system']]

                if system in systems:
                    if coding['code'] in kwargs[system]:
                        conditions.append(coding)

        return conditions

    def has_filter(self, filtern_fn, **kwargs):
        conditions = self.gather_conditions(**kwargs)

        return [condition for condition in conditions if filtern_fn(condition)]

    def has_any_within(self, timeframe, **kwargs):
        """
        Called with e.g. kwargs = {'loinc': [...]} or {'icd10cm': [...]}
        """
        def filter_fn(condition):
            if not condition['onsetDate']:
                return False

            onset_date = arrow.get(condition['onsetDate'])

            return onset_date >= timeframe.start and onset_date <= timeframe.end

        return self.has_filter(filter_fn, **kwargs)

    def has_any_before(self, end, **kwargs):
        def filter_fn(condition):
            if not condition['onsetDate']:
                return False

            onset_date = arrow.get(condition['onsetDate'])

            return onset_date <= end

        return self.has_filter(filter_fn, **kwargs)

    def has_any_after(self, start, **kwargs):
        def filter_fn(condition):
            if not condition['onsetDate']:
                return False

            onset_date = arrow.get(condition['onsetDate'])

            return onset_date >= start

        return self.has_filter(filter_fn, **kwargs)

    def most_recent_result_within(self, timeframe, value_set):
        return None

    # TODO move to Protocol class so we have access to self.timeframe; cleaner
    def value_set_match_after_one_year_before_timeframe_end(self, timeframe, value_set):
        one_year_before_timeframe_end = timeframe.end.shift(years=-1)

        return self.has_any_within(one_year_before_timeframe_end, **value_set.values)

    def value_set_match_within(self, timeframe, value_set):
        return self.has_any_within(timeframe, **value_set.values)

    def value_set_match_before(self, timeframe, value_set):
        return self.has_any_before(timeframe, **value_set.values)

    def value_set_match_after(self, timeframe, value_set):
        return self.has_any_after(timeframe, **value_set.values)
