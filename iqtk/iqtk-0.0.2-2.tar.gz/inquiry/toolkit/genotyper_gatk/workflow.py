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

from . import operations as ops
from inquiry.framework.workflow import Workflow
from inquiry.framework import util


class GenotypeGATKWorkflow(Workflow):

    def __init__(self):
        """Initialize the workflow."""
        self.tag = 'genotype-gatk'
        self.arg_template = {
            "ref_fasta": {
                "help": "The reference genome assembly."
            },
            "reads": {
                "help": "An array of read pairs to use in the genotype analysis"
            }
        }
        super(GenotypeGATKWorkflow, self).__init__()

    def define(self, p):
        ref = args.ref_fasta
        reads = util.fc_create(p, self.args.reads)
        return ops.genotype(reads, self.args)

def run(config=None):
    """Run as a Dataflow."""
    GenotypeGATKWorkflow().run(config)

if __name__ == '__main__':
    run(sys.argv[1])
