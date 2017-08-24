import arrow

from . import cds_client

CODE_SYSTEM_MAPPING = {
    'icd10cm': 'ICD-10',
    'icd10pcs': 'ICD-10',
    'snomedct': 'http://snomed.info/sct',
}

SYSTEM_CODE_MAPPING = {
    'ICD-10': ['icd10cm', 'icd10pcs'],
    'http://snomed.info/sct': ['snomedct'],
}

VALID_CONDITION_SYSTEMS = [
    'icd10cm',
    'icd10pcs',
    'snomedct',
]

VALID_LAB_SYSTEMS = [
    'loinc',
]


def coalesce(value_set, kwargs):
    if value_set:
        return value_set.values

    return kwargs


class Patient(object):
    """
    Wrapper around a Canvas patient to add convenience methods specific to science functionality.
    """

    def __init__(self, patient_key):
        # TODO replace this with call to CDS 'Chart' DRF view (to be created) that serializes
        # labs/meds/everything else
        self.patient = cds_client.get_patient(patient_key)

        self.conditions = cds_client.get_patient_conditions(patient_key)
        self.lab_results = cds_client.get_patient_conditions(patient_key)

    @property
    def first_name(self):
        return self.patient['firstName']

    @property
    def age(self):
        return float(self.patient['age'])

    # TODO timezones
    def age_at(self, time):
        birth_date = arrow.get(self.patient['birthDate'])

        return (time - birth_date).years

    def vaccines_within(self, timeframe, value_set=None, **kwargs):
        pass

    #   ____                _ _ _   _
    #  / ___|___  _ __   __| (_) |_(_) ___  _ __  ___
    # | |   / _ \| '_ \ / _` | | __| |/ _ \| '_ \/ __|
    # | |__| (_) | | | | (_| | | |_| | (_) | | | \__ \
    #  \____\___/|_| |_|\__,_|_|\__|_|\___/|_| |_|___/
    #

    def gather_conditions(self, **kwargs):
        conditions = []
        systems = [key for key, _ in kwargs.items() if key in VALID_CONDITION_SYSTEMS]

        for condition in self.conditions:
            if 'code' not in condition['resource']:
                continue

            for coding in condition['resource']['code']['coding']:
                coding_systems = SYSTEM_CODE_MAPPING[coding['system']]

                for coding_system in coding_systems:
                    if coding_system in systems:
                        if coding['code'] in kwargs[coding_system]:
                            conditions.append(coding)

        return conditions

    def filter_conditions(self, filter_fn, **kwargs):
        conditions = self.gather_conditions(**kwargs)

        return [condition for condition in conditions
                if condition['onsetDate'] and
                filter_fn(arrow.get(condition['onsetDate']))]

    def conditions_within(self, timeframe, value_set=None, **kwargs):
        """
        Called with e.g. kwargs = {'loinc': [...]} or {'icd10cm': [...]}
        """
        def filter_fn(onset):
            return onset >= timeframe.start and onset <= timeframe.end

        return self.filter_conditions(filter_fn, **coalesce(value_set, kwargs))

    def conditions_before(self, end, value_set=None, **kwargs):
        return self.filter_conditions(lambda onset: onset <= end, **coalesce(value_set, kwargs))

    def conditions_after(self, start, value_set=None, **kwargs):
        return self.filter_conditions(lambda onset: onset >= start, **coalesce(value_set, kwargs))

    # TODO move to Protocol class so we have access to self.timeframe; cleaner
    def conditions_after_one_year_before_timeframe_end(self, timeframe, value_set=None, **kwargs):
        return self.conditions_within(timeframe.end.shift(years=-1), **coalesce(value_set, kwargs))

    #  _          _
    # | |    __ _| |__  ___
    # | |   / _` | '_ \/ __|
    # | |__| (_| | |_) \__ \
    # |_____\__,_|_.__/|___/
    #

    def gather_lab_results(self, loinc):
        lab_results = []

        for lab_result in self.lab_results:
            for value in lab_result['values']:
                if value['loincNum'] in loinc:
                    lab_results.append(value)

        return lab_results

    def filter_lab_results(self, filter_fn, **kwargs):
        lab_results = self.gather_lab_results(**kwargs)

        return [lab_result for lab_result in lab_results
                if filter_fn(arrow.get(lab_result['created']))]

    def lab_results_within(self, timeframe, value_set=None, **kwargs):
        """
        Call with e.g. kwargs = {'loinc': [...]} or {'icd10cm': [...]}
        """
        def filter_fn(effective):
            return effective >= timeframe.start and effective <= timeframe.end

        return self.filter_lab_results(filter_fn, **coalesce(value_set, kwargs))

    def most_recent_result_within(self, timeframe, value_set=None, **kwargs):
        # TODO this will change from 'created' to 'effective' once that field exists on CDS
        lab_results = sorted(
            self.lab_results_within(timeframe, **coalesce(value_set, kwargs)),
            key=lambda lab_result: arrow.get(lab_result['created']),
            reverse=True)

        return lab_results[0]
