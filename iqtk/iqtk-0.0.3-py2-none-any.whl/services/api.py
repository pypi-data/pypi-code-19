#!/usr/bin/env bash
# Copyright 2017 The Regents of the University of California
#
# Licensed under the BSD-3-clause license (the "License"); you may not
# use this file except in compliance with the License.
# You are provided a copy of the license in LICENSE.md at the root of
# this project.
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Inquiry toolkit workflows API service."""

import base64
import json
import logging
import os
import uuid

from google.cloud import pubsub

from flask import Flask, jsonify, request
from six.moves import http_client
import datetime

from inquiry.services import base


# TODO: Do things like API's belong in inquiry.services or imported in a more
# abstract from from another module?


app = Flask(__name__)


class WorkflowQueue(object):
    def __init__(self, topic_name='iqtk-api-dev-topic', sub_name='iqtk-api-dev-sub'):

        pubsub_client = pubsub.Client()
        self.ps_client = pubsub.Client()
        self.topic = self.ps_client.topic(topic_name)
        if not self.topic.exists():
            self.topic.create()
        self.subscription = self.topic.subscription(sub_name)
        if not self.subscription.exists():
            self.subscription.create()

    def enqueue(self, message):
        # Data must be a bytestring
        data = json.dumps(message).encode('utf-8')
        message_id = self.topic.publish(data)


def _base64_decode(encoded_str):
    # Add paddings manually if necessary.
    num_missed_paddings = 4 - len(encoded_str) % 4
    if num_missed_paddings != 4:
        encoded_str += b'=' * num_missed_paddings
    return base64.b64decode(encoded_str).decode('utf-8')


@app.route('/health', methods=['GET'])
def health():
    """Return API health stats."""
    return jsonify({'hp': 100})


@app.route('/list', methods=['GET'])
def list():
    """List all jobs present and past."""
    return jsonify({'message': 'Listing jobs is not yet implemented.'})


@app.route('/describe', methods=['POST'])
def describe():
    """Obtain a job description object given a job ID."""
    job_id = request.get_json().get('id', '')
    message = "Description of jobs is not yet implemented. You requested to describe a job with ID: %s" % job_id
    return jsonify({'message': message})


@app.route('/delete', methods=['POST'])
def delete():
    """Delete a job given its ID."""
    job_id = request.get_json().get('id', '')
    message = "Deletion of jobs is not yet implemented. You requested to delete a job with ID: %s" % job_id
    return jsonify({'message': message})


@app.route('/submit', methods=['POST'])
def submit():
    """Submit a workflow config to run as a job on the flow runner service."""
    auth = auth_info()

    wq = WorkflowQueue()

    config = request.get_json().get('config', '')
    job_config = {
        'submitter': auth['id'],
        'submission_config': config,
        'submission_date_time': datetime.datetime.now().isoformat(),
        'job_id': str(uuid.uuid4()),
        'status': 'queued'
    }
    wq.enqueue(job_config)

    return jsonify({'code': 200,
                    'message': 'Successfully submitted job.',
                    'job': job_config})

    workflow_config = request.get_json().get('config', '')
    return jsonify({'message': 'Submitting workflow jobs is not yet implemented.'})


def auth_info():
    """Retrieves the authenication information from Google Cloud Endpoints."""
    encoded_info = request.headers.get('X-Endpoint-API-UserInfo', None)
    if encoded_info:
        info_json = _base64_decode(encoded_info)
        user_info = json.loads(info_json)
    else:
        user_info = {'id': 'anonymous'}
    return user_info


@app.route('/auth/info/googleidtoken', methods=['GET'])
def auth_info_google_id_token():
    """Auth info with Google ID token."""
    return jsonify(auth_info())


@app.errorhandler(http_client.INTERNAL_SERVER_ERROR)
def unexpected_error(e):
    """Handle exceptions by returning swagger-compliant json."""
    logging.exception('An error occured while processing the request.')
    response = jsonify({
        'code': http_client.INTERNAL_SERVER_ERROR,
        'message': 'Exception: {}'.format(e)})
    response.status_code = http_client.INTERNAL_SERVER_ERROR
    return response


def _port_from_env(default_port=8080):
    """Get the $PORT variable from the runtime environment or return 8080."""
    # TODO
    return port


class APIService(base.Service):

    def run(self):
        logging.info('The API service started successfully')
        app.run(host='127.0.0.1', port=_port_from_env(), debug=True)
