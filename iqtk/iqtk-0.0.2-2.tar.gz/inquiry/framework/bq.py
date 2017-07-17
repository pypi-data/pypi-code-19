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

from apache_beam.io import ReadFromText

from apache_beam.utils.pipeline_options import GoogleCloudOptions
from apache_beam.io.gcp.internal.clients import bigquery

from google.protobuf.json_format import MessageToDict


class WriteToBigQuery(beam.PTransform):
    """Generate, format, and write BigQuery table row information.
    """
    def __init__(self, table_name, schema, dataset='demonstration'):
        """Initializes the transform.
        Args:
            table_name (str): Name of the BigQuery table to use.
            dataset (str): Name of the dataset to use.
            schema (beam.bigquery.TableSchema): A BigQuery schema object.
        """
        super(WriteToBigQuery, self).__init__()
        self.table_name = table_name
        self.dataset = dataset
        self.schema = schema

    def get_table(self, pipeline):
        """Utility to construct an output table reference."""
        project = pipeline.options.view_as(GoogleCloudOptions).project
        return '%s:%s.%s' % (project, self.dataset, self.table_name)

    def row_fn(self, pcoll):
        pass

    def expand(self, pcoll):
        table = self.get_table(pcoll.pipeline)
        rows = self.row_fn(pcoll)
        return (
            rows
            | beam.io.Write(beam.io.BigQuerySink(
                table,
                schema=self.schema,
                create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)))


def build_schema(json_schema_string):
    """Builds a BigQuery schema object for beam.io.BigQuerySink from JSON.

    Suppose you have a bunch of schemas represented in Protobufs and you want
    to use these schemas for some BigQuery tables. We have the solution! Our
    special brand of build_schema() can generate that BigQuerySink()-compatible
    schema that you've been hoping for. No more doing it by hand!

    Args:
        json_schema_string (str): A string dump of a JSON object representing a
            BigQuery schema.

    Returns:
        bigquery.TableSchema: A beam.io.BigQuerySink-compatible schema object.
    """
    d = json.loads(json_schema_string)
    return bigquery.TableSchema(fields=_build_field(d))


def _build_field(field_array):
    """Recursive worker for build_schema()."""
    ret_fields = []

    for thing in field_array:

        if 'fields' in thing:
            fields = _build_field(thing['fields'])
            thing['fields'] = fields
        ret_fields.append(bigquery.TableFieldSchema(**thing))

    return ret_fields


def get_schema():
    return ', '.join(['%s:%s' % (s['name'], s['type']) for s in SCHEMA])
