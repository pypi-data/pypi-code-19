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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import json

from google.cloud import pubsub

from inquiry.services import base

from inquiry.toolkit.rna_quantification.workflow import TranscriptomicsWorkflow
from inquiry.toolkit.genotyper_gatk.workflow import GenotypeSamtoolsWorkflow
from inquiry.toolkit.alignment.workflow import AlignmentWorkflow
from inquiry.toolkit.metabolomics.workflow import ConvertWorkflow


class WorkflowService(base.Service):

    def __init__(self, topic_name='dev-topic', sub_name='dev-sub'):
        self.ps_client = pubsub.Client()
        self.topic = self.ps_client.topic(topic_name)
        if not self.topic.exists():
            self.topic.create()
        self.subscription = self.topic.subscription(sub_name)
        if not self.subscription.exists():
            self.subscription.create()

    def _workflow_config_for_sync_message(self, message):
        try:
            config = json.loads(message)
            logging.info('interpreted workflow run message: %s' % config)
            return config
        except:
            logging.info('could not interpret workflow run message: %s' % message)
            return {}

    def _pubsub_receive(self):
        """Receives a message from a pull subscription."""
        results = self.subscription.pull(return_immediately=False)
        print('Received {} messages.'.format(len(results)))
        for ack_id, message in results:
            print('* {}: {}, {}'.format(
               message.message_id, message.data, message.attributes))
            # Will ack and return the first message if there are more than one.
            # Those not ack'd will be received by other workers.
            self.subscription.acknowledge([ack_id])
            return message.data

    def run(self):
        logging.info('starting workflow runnner service')
        while True:
            msg = self._pubsub_receive()
            config = self._workflow_config_for_sync_message(msg)
            if '_meta' in config and 'workflow' in config['_meta']:
                if str(config['_meta']['workflow']) == 'core:expression':
                    logging.info('running transcriptomics workflow')
                    TranscriptomicsWorkflow().run(config)
                elif str(config['_meta']['workflow']) == 'core:genotype':
                    logging.info('running genotyping workflow')
                    GenotypeSamtoolsWorkflow().run(config)
                elif str(config['_meta']['workflow']) == 'core:metabolomics':
                    logging.info('running metabolomics workflow')
                    ConvertWorkflow().run(config)
                elif str(config['_meta']['workflow']) == 'core:alignment':
                    logging.info('running alignment workflow')
                    AlignmentWorkflow().run(config)
            else:
                logging.info('received run request for unknown workflow, skipping')
