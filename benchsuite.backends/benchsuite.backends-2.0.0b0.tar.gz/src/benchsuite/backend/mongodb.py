# Benchmarking Suite
# Copyright 2014-2017 Engineering Ingegneria Informatica S.p.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Developed in the ARTIST EU project (www.artist-project.eu) and in the
# CloudPerfect EU project (https://cloudperfect.eu/)
import logging

from pymongo import MongoClient

from benchsuite.core.model.execution import ExecutionResult
from benchsuite.core.model.storage import StorageConnector

logger = logging.getLogger(__name__)



class MongoDBStorageConnector(StorageConnector):

    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    def save_execution_result(self, execution_result: ExecutionResult):
        r = self.collection.insert_one({
            'start': execution_result.start,
            'duration': execution_result.duration,
            'tool': execution_result.tool,
            'workload': execution_result.workload,
            'provider': execution_result.provider,
            'service_type': execution_result.service_type
        })

        logger.info('New execution results stored with id=%s', r.inserted_id)

    @staticmethod
    def load_from_config(config):
        logger.debug('Loading %s', MongoDBStorageConnector.__module__ + "." + __class__.__name__)

        o = MongoDBStorageConnector()
        o.client = MongoClient(config['Storage']['connection_string'])
        o.db = o.client[config['Storage']['db_name']]
        o.collection = o.db[config['Storage']['collection_name']]

        logger.info('MongoDBStorageConnector created for %s, db=%s, coll=%s', config['Storage']['connection_string'], config['Storage']['db_name'], config['Storage']['collection_name'])

        return o


