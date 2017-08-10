from flask import Blueprint, Response, request
import os
import datetime

blueprint = Blueprint('test_blueprint', __name__)

endpoint = os.getenv('TEST_BLUEPRINT.ENDPOINT', '/test')
http_methods = os.getenv('TEST_BLUEPRINT.HTTP_METHODS', 'GET').split(',')

@blueprint.route(endpoint, methods=http_methods)
def run():
    try:
        return Response("Test passed successfully", mimetype="text/plain")
    except:
        return Response("Exception raised", mimetype="text/plain")
