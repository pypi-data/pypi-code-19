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
import uuid

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
    #salt = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    salt = str(uuid.uuid4())
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


class Prefixer(object):
    def __init__(self):
        self.salt = str(uuid.uuid4())
    def apply(self, path):
        arr = path.split('/')
        arr[-1] = self.salt + '.' + arr[-1]
        return '/'.join(arr)

def _outputs_from_template(templates, output_dir):

    out = []
    for template in templates:

        file_type = None if 'file_type' not in template else template['file_type']

        out.append(util.File(remote_path=util.localize(template['name'],
                                                       output_dir),
                        file_type=file_type))

    return out


def wrap_task_command(task, command):
    """Wrap command with pre and post steps."""

    prefix = Prefixer()

    # These can probably be performed by the attached sync/logging VM.
    pre = util.Command([
        'mkdir', '-p', '/mnt/data/output'
    ])
    pre.chain([
        'mkdir', '-p', '/mnt/data/input'
    ])

    cmd = util.Command()
    cmd.txt = str(command)
    pre.chain_command(cmd)

    post = util.Command([
        # TODO: There are some failure cases here.
    "echo", "'", cmd.txt, "'", ">", prefix.apply(task.out_path + "/log.txt")
    ])
    post.chain([
    'echo', '"run finished successfully."'
    ])

    pre.chain_command(post)
    return pre


class Provider(object):
    def __init__(self, provider_string):
        # Todo: validation, obviously
        arr = provider_string.split(':')
        self.name = arr[0]
        self.region = arr[1]


class JobSpec(object):
    def __init__(self, inputs, output_dir, command, container, args,
                 timeout=datetime.timedelta(hours=3),
                 dry_run=False, provider="gcp:us-central1-f"):
        self.input_files = inputs
        self.log_output_path = output_dir
        self.disk_size = container.disk
        self.min_ram = container.ram
        self.command = command.txt
        self.runtime_image = container.image
        self.job_args = {}
        self.project_id = args.project
        self.job_name = args.job_name
        provider = Provider(provider)
        self.region = provider.region
        self.output_dir = output_dir
        self.cpu_cores = container.cpu_cores
        self.timeout = timeout
        self.dry_run = dry_run


def _construct_job_spec(task, command, inputs=[], tag='',
                        expect=[], dry_run=None, expected_outputs=[]):
    command = wrap_task_command(task, command)

    logging.info('executing command: %s' % command.txt)

    if hasattr(task.args, 'dry_run') and task.args.dry_run:
        dry_run = True
    else:
        dry_run = False

    output_dir = construct_outdir(task.args.output_dir,
                                  task.task_label, tag)

    job_spec = JobSpec(inputs, output_dir, command, task.container, task.args,
                       dry_run)

    pp = pprint.PrettyPrinter(indent=2)
    logging.debug(pp.pprint(job_spec.__dict__))

    return job_spec


def submit(task, command, inputs=[], tag='',
           expect=[], dry_run=None, expected_outputs=[]):

    task.job_spec = _construct_job_spec(task, command, inputs, tag,
                                        expect, dry_run,
                                        expected_outputs)

    if hasattr(task.args, 'local') and task.args.local:
        response = local.local_run(**task.job_spec.__dict__)
    else:
        response = gcp.run(**task.job_spec.__dict__)

    response['output_files'] = _outputs_from_template(expected_outputs,
                                                      task.job_spec.output_dir)

    pp = pprint.PrettyPrinter(indent=2)
    logging.debug(pp.pprint(response))

    return response
