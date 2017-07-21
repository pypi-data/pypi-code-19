from requests.exceptions import HTTPError


def parsePresignResponse(response_object):
    try:
        response_body_object = response_object.json()
    except:
        response_object.raise_for_status()

    if response_body_object.get('error'):
        additional_possible_reason = ''
        if response_object.status_code == 404:
            additional_possible_reason = '(Check your model_id) '

        message = '{}: {} {}for url:{}'.format(
            response_object.status_code,
            response_object.reason,
            additional_possible_reason,
            response_object.url
        )

        raise HTTPError(message)

    return response_body_object
