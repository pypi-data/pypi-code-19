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
"""A dev pipeline to write data from an expression table file to BigQuery."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import apache_beam as beam
import logging
from apache_beam.io import ReadFromText
# from apache_beam.io.gcp.internal.clients import bigquery
from google.protobuf.json_format import MessageToDict
from google.cloud import bigquery
import uuid
import time


class BQUpload(beam.DoFn):

    def __init__(self, schema, dataset_name, table_name):
        self.dataset_name = dataset_name
        self.table_name = table_name
        self.schema = schema

    def process(self, f):

        load_data_from_gcs(self.dataset_name, self.table_name,
                           f[0].remote_path, self.schema)


def load_data_from_gcs(dataset_name, table_name, source, schema):
    client = bigquery.Client()

    logging.info('loading data from GCS: %s' % source)
    logging.info('loading data to bigquery table: %s:%s' % (dataset_name,
                                                            table_name))

    dataset = client.dataset(dataset_name)
    if not dataset.exists():
        logging.info('dataset does not exist, creating')
        dataset.create()
    else:
        logging.info('dataset exists, skipping creation')

    table = dataset.table(table_name, schema)
    if not table.exists():
        logging.info('table does not exist, creating')
        table.create()
    else:
        logging.info('table exists, skipping creation')

    job_name = str(uuid.uuid4())

    job = bigquery.job.LoadTableFromStorageJob(name=job_name,
                                               destination=table,
                                               source_uris=[source],
                                               client=client, schema=schema)

    job.begin()
    logging.info('started job, polling for completion')
    _wait_for_job(job)
    logging.info('bq upload job complete')

    print('Loaded {} rows into {}:{}.'.format(
        job.output_rows, dataset_name, table_name))


def _wait_for_job(job):
    while True:
        job.reload()
        if job.state == 'DONE':
            if job.error_result:
                raise RuntimeError(job.errors)
            return
        time.sleep(1)
