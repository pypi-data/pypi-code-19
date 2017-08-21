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

from . import operations as ops
from inquiry.framework.workflow import Workflow
from inquiry.framework import util
from inquiry.framework import task

class AlignmentWorkflow(Workflow):

    def __init__(self):
        """Initialize the workflow."""
        self.tag = 'bwa-align'
        self.arg_template = {
            'ref_fasta': {
                'help': 'The reference genome assembly.'
            },
            'reads': {
                'help': 'A comma-separated list of input read files for condition a.'
            }
        }
        super(AlignmentWorkflow, self).__init__()

    def define(self):
        """Perform sequence alignment with BWA MEM and optional pre- and post-ops.

        Args:
            param1 (int): The first parameter.
            param2 (str): The second parameter.

        .. _BWA Aligner:
           http://bio-bwa.sourceforge.net/
        """

        return (util.fc_create(self.p, self.args.reads)
                | task.ContainerTaskRunner(ops.BWAMem(self.args,
                                                      self.args.ref_fasta)))


def run(config=None):
    """Run as a Dataflow."""
    AlignmentWorkflow().run(config)


if __name__ == '__main__':
    run(sys.argv[1])
