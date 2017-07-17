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
"""General task execution interface."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import apache_beam as beam
import datetime
import pprint
import logging

from inquiry.framework import gcp
from inquiry.framework import local
from inquiry.framework import util


class ContainerTaskRunner(beam.PTransform):

    def __init__(self, task, tag=None, task_args=None):
        self.task = task
        self.label = util.update_label_if_tag(task.task_label, tag)

    def expand(self, pcoll):
        return (pcoll
               | util.dev_ladd(self.label, 'crun') >> beam.ParDo(self.task)
               | util.dev_ladd(self.label, 'wait') >> beam.FlatMap(gcp.poll_until_complete)
               | util.dev_ladd(self.label, 'verify') >> beam.FlatMap(gcp.verify))

def declare_outputs(output_dir, templates):
    out = []
    for template in templates:

        out.append(f.File(file_type=template['file_type'],
                        remote_path=util.localize(
                            template['name'], output_dir
                            )))

    return out


class ContainerTaskResources(object):

    def __init__(self, image='ubuntu:16.04', cpu_cores=2, disk=20,
                 ram=2):
        self.cpu_cores = cpu_cores
        self.disk = disk
        self.ram = ram
        self.image = image


# TODO: Duplicated
def construct_outdir(output_dir_arg, label, tag):
    salt = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    output_dir = output_dir_arg + '/' + label + '-'
    if label is not None and tag is not None:
        output_dir += (label + '-')
    output_dir += (salt + '/')
    return output_dir


class ContainerTask(beam.DoFn):

    def __init__(self, task_label, args, container, task_tag=None,
                 out_path='/mnt/data/output', input_path='/mnt/data/input'):
        self.task_label = task_label
        self.args = args
        self.container = container
        self.out_path = out_path
        self.input_path = input_path

    def wrap_command(self, command):
        """Wrap command with pre and post steps."""

        # pre = Command([
        # 'set', '-e'
        # ])
        # pre.chain([
        # 'finish()', '{if', '(($?!= 0));', 'then',
        # 'echo', '"run did not finish successfully."', 'fi'
        # ])
        # pre.chain([
        # 'trap', 'finish', 'EXIT'
        # ])
        # pre.chain([
        # 'mkdir', '-p', '/mnt/data/output'
        # ])

        # These can probably be performed by the attached sync/logging VM.
        pre = util.Command([
            'mkdir', '-p', '/mnt/data/output'
        ])
        pre.chain([
            'mkdir', '-p', '/mnt/data/input'
        ])

        cmd = util.Command()
        cmd.txt = str(command) # hack...
        pre.chain_command(cmd)
        #command.prepend_command(pre)

        post = util.Command([
            # TODO: There are some failure cases here.
        "echo", "'", cmd.txt, "'", ">", self.out_path + "/log.txt"
        ])
        post.chain([
        'echo', '"run finished successfully."'
        ])

        #command.chain_command(post)
        pre.chain_command(post)

        return pre

    def post(self, command):
        command.log_self(self.out_path)
        command.chain(['echo', '"run finished successfully."'])

    def submit(self, command, inputs=[], tag='',
               expect=[], dry_run=None, expected_outputs=[]):
        command = self.wrap_command(command)

        logging.info('executing command: %s' % command.txt)

        if hasattr(self.args, 'dry_run') and self.args.dry_run:
            dry_run = True

        output_dir = construct_outdir(self.args.output_dir, self.task_label, tag)

        job_spec = {
            'input_files': inputs, 'log_output_path': output_dir,
            'disk_size': self.container.disk, 'min_ram': self.container.ram, 'command': command.txt,
            'project_id': self.args.project, 'runtime_image': self.container.image, 'job_args': {},
            'job_name': self.args.job_name, 'region': 'us-central1-f',
            'dry_run': dry_run, 'output_dir': output_dir, 'cpu_cores': self.container.cpu_cores,
            'timeout': datetime.timedelta(hours=3)
        }

        pp = pprint.PrettyPrinter(indent=2)
        logging.debug(pp.pprint(job_spec))

        if hasattr(self.args, 'local') and self.args.local:
            response = local.local_run(**job_spec)
        else:
            response = gcp.run(**job_spec)

        response['output_files'] = self._outputs_from_template(
            expected_outputs, output_dir)

        logging.debug(pp.pprint(response))

        return response

    def _outputs_from_template(self, templates, output_dir):

        out = []
        for template in templates:

            file_type = None if 'file_type' not in template else template['file_type']

            out.append(util.File(remote_path=util.localize(template['name'],
                                                           output_dir),
                            file_type=file_type))

        return out
