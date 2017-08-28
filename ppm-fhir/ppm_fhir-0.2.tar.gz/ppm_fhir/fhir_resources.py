def enrollment_flag(patient_id, status='proposed', start=None, end=None):

    data = {
        'resourceType': 'Flag',
        'status': 'active' if status == 'accepted' else 'inactive',
        'category': {
            'coding': [{
                'system': 'http://hl7.org/fhir/flag-category',
                'code': 'admin',
                'display': 'Admin',
            }],
            'text': 'Admin'
        },
        'code': {
            'coding': [{
                'system': 'https://peoplepoweredmedicine.org/enrollment-status',
                'code': status,
                'display': status.title(),
            }],
            'text': status.title(),
        },
        "subject": {
            "reference": patient_id
        }
    }

    # Set dates if specified.
    if start:
        data['period'] = {
            'start': start.isoformat()
        }
        if end:
            data['period']['end'] = end.isoformat()

    return data
