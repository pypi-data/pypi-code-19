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
"""PubSub GCS change notification listener."""

import json
from google.cloud import pubsub
import uuid
from google.cloud import logging
import time

from inquiry.toolkit.simple.workflow import SimpleWorkflow

# def dev_conf_from_message(change):
#     return {'op': SimpleWorkflow,
#             'config': {
#                 "file_path": change,
#                 "scalar_param": "7"
#                 },
#             'expected': []
#             }


class Service(object):
    def __init__(self, topic_name, subscription_name):
        pubsub_client = pubsub.Client()
        self.topic = pubsub_client.topic(topic_name)
        self.subscription = self.topic.subscription(subscription_name)

    def receive(self):
        # Change return_immediately=False to block until messages are
        # received.
        results = self.subscription.pull(return_immediately=True)
        print('Received {} messages.'.format(len(results)))
        for ack_id, message in results:
            print('* {}: {}, {}'.format(
                message.message_id, message.data, message.attributes))

        # Acknowledge received messages. If you do not acknowledge, Pub/Sub will
        # redeliver the message.
        if results:
            self.subscription.acknowledge([ack_id for ack_id,
                                           message in results])
        return results

    def log(self, message):
        """Issue cloud logging message that storage event was received."""
        client = logging.Client()
        logger = client.logger('log_name')
        logger.log_text(message)

    def run(self):
        while True:
            change = str(self.receive())
            self.log(change)
            time.sleep(2)
            # iqf.local.e2e_test_runner(dev_conf_from_message(change))


if __name__ == "__main__":
    Service('dev-topic', 'dev-subscription').run()
