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
"""Simple example of containerized analysis pipeline."""

from __future__ import absolute_import

from inquiry.framework.workflow import Workflow

from inquiry.framework import util
from inquiry.framework import task


class SimpleOp(task.ContainerTask):

    def __init__(self, args, scalar_param):
        self.scalar_param = scalar_param
        container = task.ContainerTaskResources(
            disk=60, cpu_cores=4, ram=8,
            image='gcr.io/jbei-cloud/tophat:0.0.1')
        super(SimpleOp, self).__init__(task_label='simple', args=args,
                                     container=container)

    def process(self, file_path):

        cmd = util.Command(['pwd'])

        # cmd = util.Command(['wc -c', util.localize(file_path),
        #                     '>', self.out_path + 'count.txt'])

        yield self.submit(cmd.txt, inputs=[file_path])


class SimpleWorkflow(Workflow):
    """Provides a simple illustration of workflow structure."""

    def __init__(self):
        self.tag = 'simple-workflow'
        self.arg_template = {'file_path': {'help': 'path to a gcs file'},
                             'scalar_param': {'help': 'some scalar'}}
        super(SimpleWorkflow, self).__init__()

    def define(self):
        return (util.fc_create(self.p, [self.args.file_path])
                | task.ContainerTaskRunner(SimpleOp(self.args,
                                                    self.args.scalar_param)))


if __name__ == '__main__':
    run(sys.argv[1])
