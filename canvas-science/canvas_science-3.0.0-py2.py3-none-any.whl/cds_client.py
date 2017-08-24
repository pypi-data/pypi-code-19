import os

import requests

CLINICAL_DATA_URL = os.getenv('CLINICAL_DATA_URL', 'https://cab-cds.canvasmedical.com')

# TODO move this to its own module for use by pharmacy, messaging, etc.


def paginate(url, patient_key, page_size=100):
    results = []
    offset = 0
    total = -1

    # XXX could run indefinitely if condition is added after first loop, would cursor pagination be
    # better?
    while len(results) != total:
        response = requests.get(f'{CLINICAL_DATA_URL}{url}'
                                f'?patient__key={patient_key}&offset={offset}&limit={page_size}')

        response_json = response.json()

        if total < 0:
            total = response_json['total']

        results.extend(response_json['entry'])

        offset += page_size

    return results


def get_patient(patient_key):
    response = requests.get(f'{CLINICAL_DATA_URL}/Patient/{patient_key}')

    if response.status_code != 200:
        raise Exception(f"Patient '{patient_key}' not found")

    return response.json()


def get_patient_conditions(patient_key):
    return paginate('/Condition/', patient_key=patient_key)


def get_patient_lab_orders(patient_key):
    return paginate('/LabOrder/', patient_key=patient_key)


def get_patient_lab_results(patient_key):
    return paginate('/LabResult/', patient_key=patient_key)


def get_patient_procedures(patient_key):
    return paginate('/Procedure/', patient_key=patient_key)


def get_patient_encounters(patient_key):
    return paginate('/Encounter/', patient_key=patient_key)
