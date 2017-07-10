import json

from quark_utilities import json_helpers


def to_response(handler, status_code, documents=None, count=None, formatter=None):
    handler.set_status(status_code)
    if not documents:
        return

    if type(documents) == dict:
        handler.write(
            json.dumps(
                formatter(documents), default=json_helpers.bson_to_json
            ))
    elif isinstance(documents, (list, set)):
        handler.write(
            json.dumps({
                "data": {
                    "items": [formatter(document) for document in documents],
                    "count": count or len(documents)
                }
            }, default=json_helpers.bson_to_json))

    handler.set_header('Content-Type', 'application/json')