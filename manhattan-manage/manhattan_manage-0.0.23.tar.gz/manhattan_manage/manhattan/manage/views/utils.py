"""
Utilities functions for manhattan views.
"""

import flask

__all__ = [
    'json_fail',
    'json_success'
    ]


def json_fail(reason, issues=None):
    """Return a fail response"""
    response = {'status': 'fail', 'payload': {'reason': reason}}
    if issues:
        response['payload']['issues'] = issues
    return flask.jsonify(response)

def json_success(payload=None):
    """Return a success response"""
    response = {'status': 'success'}
    if payload:
        response['payload'] = payload
    return flask.jsonify(response)