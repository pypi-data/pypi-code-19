
from flask import jsonify

def format_json_response(data, code):
    resp = {'data': data}
    if code >= 400:
        resp = {'error': data}
    return resp

def create_json_output_handler(json_formatter=None):
    def output_json(data, status, headers=None):
        # json formatter for data envelopes
        if callable(json_formatter):
            data = json_formatter(data, status)

        resp = jsonify(data)
        resp.status_code = status
        resp.headers.extend(headers)

        return resp
    return output_json
