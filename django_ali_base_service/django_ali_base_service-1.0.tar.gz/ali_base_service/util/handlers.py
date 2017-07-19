import json

from rest_framework import status
from rest_framework.response import Response


def convert_body_to_dict(body):
    decode = body.decode('utf-8')

    if decode == "":
        return {}

    return json.loads(decode)


def get_successful_response(data):
    return Response({
        "status": status.HTTP_200_OK,
        "latest_available_version": 1,
        "data": data,
        "error": None
    })


def get_error_response(error):
    return Response({
        "status": status.HTTP_400_BAD_REQUEST,
        "latest_available_version": 1,
        "data": None,
        "error": error
    })


def read_get_request_data(request_get):
    start = request_get.get("from")
    count = request_get.get("count")
    search_object = request_get.get("search_object", "{}")

    if start is not None:
        start = start.strip()

    if count is not None:
        count = count.strip()

    if search_object is not None:
        search_object = search_object.strip()

        if len(search_object) > 0:
            search_object = json.loads(search_object)
        else:
            search_object = None

    return search_object, start, count


def string_to_json(string):
    return json.loads(string)



