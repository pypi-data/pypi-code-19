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
"""Genotype analysis pipeline."""

from __future__ import absolute_import

import apache_beam as beam

from . import operations as ops
from inquiry.framework.workflow import Workflow
from inquiry.framework import util
from inquiry.framework import task


class GenotypeSamtoolsWorkflow(Workflow):

    def __init__(self):
        """Initialize the workflow."""
        self.tag = 'genotype-samtools'
        self.arg_template = {
            "ref_fasta": {
                "help": "The reference genome assembly."
            },
            "reads": {
                "help": "An array of read pairs to use in the genotype analysis"
            },
            'bq_dataset_name': {
                'help': 'the name of a bigquery dataset'
            },
            'bq_table_name': {
                'help': 'the name of a bigquery table'
            }
        }
        super(GenotypeSamtoolsWorkflow, self).__init__()

    def define(self):
        geno = (util.fc_create(self.p, self.args.reads)
                | task.ContainerTaskRunner(
                    ops.CombinedSamtoolsGenotyper(
                        self.args,
                        self.args.ref_fasta
                        )))

        (util.match(geno, {'file_type': 'VCFBody'})
        | 'bq-upload' >> beam.ParDo(
             ops.GenotypeBQUpload(self.args.bq_dataset_name,
                                  self.args.bq_table_name)
             ))

        return geno



def run(config=None):
    """Run as a Dataflow."""
    GenotypeSamtoolsWorkflow().run(config)

if __name__ == '__main__':
    run(sys.argv[1])
