from fhirclient.models.bundle import Bundle
from fhirclient.models.relatedperson import RelatedPerson

import requests
import base64
import re
import random


def flatten_consent(incoming_json):

    participant_record = dict()

    participant_record["consent_start"] = incoming_json['entry'][0]['resource']['period']['start']
    participant_record["status"] = incoming_json['entry'][0]['resource']['status']

    return participant_record


def flatten_questionnaire_response(incoming_json):

    answers = []

    for answer in incoming_json['entry'][0]['resource']['item']:
        answers.append(answer['answer'][0]['valueString'])

    return answers


def flatten_consent_composition(incoming_json, fhir_url):

    incoming_bundle = Bundle(incoming_json)

    # Prepare the object.
    consent_object = {
        'consent_questionnaires': [],
        'assent_questionnaires': [],
    }
    consent_exceptions = []
    assent_exceptions = []

    if incoming_bundle.total > 0:

        for bundle_entry in incoming_bundle.entry:
            if bundle_entry.resource.resource_type == "Consent":

                signed_consent = bundle_entry.resource

                # We can pull the date from the Consent Resource. It's stamped in a few places.
                consent_object["date_signed"] = signed_consent.dateTime.origval

                # Exceptions are for when they refuse part of the consent.
                if signed_consent.except_fhir:
                    for consent_exception in signed_consent.except_fhir:
                        consent_exceptions.append(consent_exception.code[0].display)

            elif bundle_entry.resource.resource_type == 'Composition':

                composition = bundle_entry.resource

                entries = [section.entry for section in composition.section if section.entry is not None]
                references = [entry[0].reference for entry in entries if
                              len(entry) > 0 and entry[0].reference is not None]
                text = [section.text.div for section in composition.section if section.text is not None][0]

                # Check the references for a Consent object, making this comp the consent one.
                if len([r for r in references if 'Consent' in r]) > 0:
                    consent_object['consent_text'] = text
                else:
                    consent_object['assent_text'] = text

            elif bundle_entry.resource.resource_type == "RelatedPerson":
                pass
            elif bundle_entry.resource.resource_type == "Contract":

                contract = bundle_entry.resource

                # Contracts with a binding reference are either the individual consent or the guardian consent.
                if contract.bindingReference:

                    # Fetch the questionnaire and its responses.
                    url = fhir_url + "/QuestionnaireResponse/"
                    params = {
                        '_id': re.search('[^\/](\d+)$', contract.bindingReference.reference).group(0),
                        '_include': 'QuestionnaireResponse:questionnaire'
                    }
                    r = requests.get(url, params=params)
                    r.raise_for_status()

                    # Add link IDs.
                    json = inject_link_ids(r.json())

                    # Parse out the request.
                    questionnaire_bundle = Bundle(json)

                    # Get the questionnaire and its response.
                    questionnaire = [entry.resource for entry in questionnaire_bundle.entry if
                                     entry.resource.resource_type == 'Questionnaire'][0]
                    questionnaire_response = [entry.resource for entry in questionnaire_bundle.entry if
                                entry.resource.resource_type == 'QuestionnaireResponse'][0]

                    # The reference refers to a Questionnaire which is linked to a part of the consent form.
                    if questionnaire_response.questionnaire.reference == "Questionnaire/individual-signature-part-1"\
                            or questionnaire_response.questionnaire.reference == "Questionnaire/neer-signature":

                        # This is a person consenting for themselves.
                        consent_object["type"] = "INDIVIDUAL"
                        consent_object["signor_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)
                        consent_object["participant_name"] = contract.signer[0].signature[0].whoReference.display

                        # These don't apply on an Individual consent.
                        consent_object["participant_acknowledgement_reason"] = "N/A"
                        consent_object["participant_acknowledgement"] = "N/A"
                        consent_object["signor_name"] = "N/A"
                        consent_object["signor_relationship"] = "N/A"
                        consent_object["assent_signature"] = "N/A"
                        consent_object["assent_date"] = "N/A"
                        consent_object["explained_signature"] = "N/A"

                    elif questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-1":

                        # This is a person consenting for someone else.
                        consent_object["type"] = "GUARDIAN"

                        # Get the Related Person resource who signed the contract.
                        related_person_get = requests.get(fhir_url + "/" + contract.signer[0].party.reference)
                        related_person = RelatedPerson(related_person_get.json())

                        consent_object["signor_name"] = related_person.name[0].text
                        consent_object["signor_relationship"] = related_person.relationship.text

                        consent_object["participant_name"] = contract.signer[0].signature[0].onBehalfOfReference.display
                        consent_object["signor_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)

                    elif questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-2":

                        # This is the question about being able to get acknowledgement from the participant by the guardian/parent.
                        consent_object["participant_acknowledgement"] = questionnaire_response.item[0].answer[0].valueString

                        # If the answer to the question is no, grab the reason.
                        if consent_object["participant_acknowledgement"] == "no":
                            consent_object["participant_acknowledgement_reason"] = questionnaire_response.item[1].answer[0].valueString

                        # This is the Guardian's signature letting us know they tried to explain this study.
                        consent_object["explained_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)

                    elif questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-3":

                        # A contract without a reference is the assent page.
                        consent_object["assent_signature"] = base64.b64decode(contract.signer[0].signature[0].blob)
                        consent_object["assent_date"] = contract.issued.origval

                        # Append the Questionnaire Text if the response is true.
                        for current_response in questionnaire_response.item:

                            if current_response.answer[0].valueBoolean:
                                answer = [item for item in questionnaire.item if item.linkId == current_response.linkId][0]
                                assent_exceptions.append(answer.text)

                    # Prepare to parse the questionnaire.
                    questionnaire_object = {
                        'template': 'dashboard/{}.html'.format(questionnaire.id),
                        'questions': []
                    }

                    for item in questionnaire.item:

                        question_object = {
                            'type': item.type,
                        }

                        if item.type == 'display':
                            question_object['text'] = item.text

                        elif item.type == 'boolean' or item.type == 'question':
                            # Get the answer.
                            for response in questionnaire_response.item:
                                if response.linkId == item.linkId:
                                    # Process the question, answer and response.
                                    if item.type == 'boolean':
                                        question_object['text'] = item.text
                                        question_object['answer'] = response.answer[0].valueBoolean

                                    elif item.type == 'question':
                                        question_object['yes'] = item.text
                                        question_object['no'] = 'I was not able to explain this study to my child or ' \
                                                                'individual in my care who will be participating'
                                        question_object['answer'] = response.answer[0].valueString is 'yes'

                        # Add it.
                        questionnaire_object['questions'].append(question_object)

                    # Check the type.
                if questionnaire_response.questionnaire.reference == "Questionnaire/guardian-signature-part-3":
                    consent_object['assent_questionnaires'].append(questionnaire_object)
                else:
                    consent_object['consent_questionnaires'].append(questionnaire_object)

    consent_object["exceptions"] = consent_exceptions
    consent_object["assent_exceptions"] = assent_exceptions

    return consent_object


def inject_link_ids(json):

    # Appeases the FHIR library by ensuring question items all have linkIds, regardless of an associated answer.
    for question in [entry['resource'] for entry in json['entry']
                     if entry['resource']['resourceType'] == 'Questionnaire']:
        for item in question['item']:
            if 'linkId' not in item:
                # Assign a random string for the linkId
                item['linkId'] = "".join([random.choice("abcdefghijklmnopqrstuvwxyz1234567890") for _ in range(10)])

    return json


def flatten_participant(incoming_json):

    resource_record = incoming_json['entry'][0]['resource']

    participant_record = dict()

    participant_record["email"] = resource_record['identifier'][0]['value']
    participant_record["fhir_id"] = resource_record['id']

    try:
        participant_record["firstname"] = resource_record['name'][0]['given'][0]
    except (KeyError, IndexError):
        participant_record["firstname"] = ""

    try:
        participant_record["lastname"] = resource_record['name'][0]['family']
    except (KeyError, IndexError):
        participant_record["lastname"] = ""

    try:
        participant_record["street_address1"] = resource_record['address'][0]['line'][0]
    except (KeyError, IndexError):
        participant_record["street_address1"] = ""

    try:
        participant_record["street_address2"] = resource_record['address'][0]['line'][2]
    except (KeyError, IndexError):
        participant_record["street_address2"] = ""

    try:
        participant_record["city"] = resource_record['address'][0]['city']
    except (KeyError, IndexError):
        participant_record["city"] = ""

    try:
        participant_record["state"] = resource_record['address'][0]['state']
    except (KeyError, IndexError):
        participant_record["state"] = ""

    try:
        participant_record["zip"] = resource_record['address'][0]['postalCode']
    except (KeyError, IndexError):
        participant_record["zip"] = ""

    if resource_record.get('telecom'):
        for telecom in resource_record['telecom']:
            if telecom['system'] == "phone":
                try:
                    participant_record["phone"] = telecom['value']
                except (KeyError, IndexError):
                    participant_record["phone"] = ""

            if telecom['system'] == "other":
                try:
                    participant_record["twitter_handle"] = telecom['value']
                except (KeyError, IndexError):
                    participant_record["twitter_handle"] = ""
    else:
        participant_record["phone"] = ""
        participant_record["twitter_handle"] = ""

    return participant_record


def flatten_list(incoming_json):

    points = []

    for entry in incoming_json['entry']:
        if entry['resource']['resourceType'] == "Organization":
            points.append(entry['resource']['name'])

    return points
