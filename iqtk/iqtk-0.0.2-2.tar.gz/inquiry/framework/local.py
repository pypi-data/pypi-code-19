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
"""Local container run."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import docker
import json
import os
import tempfile
import time

from inquiry.framework import gcp
from inquiry.framework import util


logging = util.Logger(severity='DEBUG')


class LocalContainerRuntimeError(Exception):
    """Error thrown when a container task exits with error status code.

    This error indicates that an error occurred within the container runtime,
    such as a result of a malformed command or a bug in the container itself
    such that exit_code != 0, i.e. self.cli.api.wait(self.container['Id']) != 0.
    """


def local_run(polling_interval=4,
                input_files=None,
                disk_size=20,
                log_output_path=None,
                min_ram=1,
                command=None,
                project_id=None,
                runtime_image=None,
                output_dir=None,
                job_args=None,
                region='us-central1-f',
                job_name='untitled',
                timeout=datetime.timedelta(hours=3),
                dry_run=False,
                cpu_cores=1,
                debug=False,
                keep_inputs=False,
                keep_outputs=False,
                **kwargs):
    """Wrapper for LocalDockerTask handling data staging.

    Args:
        keep_inputs (bool): Whether to keep the staged-in inputs.

    """

    host_tmp_dir = tempfile.mkdtemp(dir='/tmp/iq')
    local_input_dir = util.safe_mkdir(os.path.join(host_tmp_dir, 'input'))
    local_output_dir = util.safe_mkdir(os.path.join(host_tmp_dir, 'output'))

    logging.info(local_input_dir)

    # Copy files in 'input_files' into the container /mnt/data/inputs dir
    for f in input_files:
        logging.info(f)
        gcp.stage_data(f, local_input_dir)

    # Write the job command script to the inputs directory.
    # TODO
    with open(local_input_dir + '/__job_script.sh', 'w') as f:
        f.write(command)

    # Run 'command' in a container made from 'image' locally.
    #logs = LocalDockerTask(image=runtime_image, command=command).execute()
    script_cmd = 'sh /mnt/data/input/__job_script.sh'
    logs = LocalDockerTask(image=runtime_image, command=script_cmd,
                           host_tmp_dir=host_tmp_dir).execute()

    # Copy the files from /mnt/data/outputs to 'output_dir'
    for f in util._subprocess('ls %s' % local_output_dir):
        if len(f) > 0:
            gcp.stage_data(local_output_dir + '/' + f, output_dir)

    if not keep_inputs:
        safe_remove(local_input_dir)

    if not keep_outputs:
        safe_remove(local_output_dir)

    return {'done': True, 'name': job_name, 'logs': logs}


def safe_remove(dir):
    """Recursively delete directory on local filesystem only if /tmp/iq/..."""
    if not dir.startswith('/tmp/iq/tmp'):
        raise ValueError('safe_remove does not allow recursive deletion of '
                         'directories on local filesystem other than those '
                         'prefixed with /tmp/iq/tmp. safety first.')
    logging.debug('removing directory %s' % dir)


def write_conf(conf):

    assert isinstance(conf, dict)

    tf = tempfile.NamedTemporaryFile(delete=False)
    tf.writelines([json.dumps(conf)])
    tf.close()
    DUMMY_CONF = tf.name
    return DUMMY_CONF

# def e2e_test_runner(case, tag, hack_time_sleep=20, arg_template={}):
#
#     if not isinstance(case, dict):
#         raise ValueError('case must be of type dict, saw %s' % case)
#
#     #conf = write_conf(case['config'])
#     class TestWorkflow(workflow.Workflow):
#         def define(self):
#             return case['op'](self.p, self.args)
#
#     tw = TestWorkflow(('test-e2e-%s' % tag))
#     tw.run(case['config'], test_case=True)
#     args, p = prepare_pipeline(job_tag=('test-e2e-%s' % tag))
#     result = case['op'](args, p)
#     verified = verify_workflow_outputs(args.output, case['expected'])
#
#     return verified


# # TODO: this is the new one fixme
def e2e_test_runner(case):
    return case['op']().run(case['config'], test_case=case)


class LocalDockerTask(object):
    """Run a containerized task locally.

    In a development setting it's valuable to be able to test commands in a
    local container before running these on remote services. As Google's
    Pipelines API for batch tasks is the target this operation presumes data
    has already been staged in and will be staged out by some parent process.

    Example:
        Run the `pwd` command in the Dockerhub base ubuntu container.

            $ LocalDockerTask(image='ubuntu', command='pwd').execute()

    Args:
        image (str): The docker machine image inside of which to run commands.
        command (str): The bash shell command (chain) to run.

    Returns:
        str: A raw string capturing the container logs.

    Todo:
        * The structure of the returned object should replicate that returned
            by the GCG Pipelines run() call as the same code will be used for
            both in downstream polling and verification of existence of outputs.

    .. _Derived from AirFlow DockerOperator:
       https://github.com/apache/incubator-airflow/blob/master/airflow/operators/docker_operator.py
    """

    def __init__(self,
                 image,
                 api_version=None,
                 command=None,
                 cpus=1.0,
                 docker_url='unix://var/run/docker.sock',
                 environment=None,
                 force_pull=False,
                 mem_limit=None,
                 network_mode=None,
                 tls_ca_cert=None,
                 tls_client_cert=None,
                 tls_client_key=None,
                 tls_hostname=None,
                 tls_ssl_version=None,
                 tmp_dir='/mnt/data',
                 host_tmp_dir=None,
                 user='root',
                 volumes=None):

        self.api_version = api_version
        self.command = command
        self.cpus = cpus
        self.docker_url = docker_url
        self.environment = environment or {}
        self.force_pull = force_pull
        self.image = image
        self.mem_limit = mem_limit
        self.network_mode = network_mode
        self.tls_ca_cert = tls_ca_cert
        self.tls_client_cert = tls_client_cert
        self.tls_client_key = tls_client_key
        self.tls_hostname = tls_hostname
        self.tls_ssl_version = tls_ssl_version
        self.tmp_dir = tmp_dir
        self.user = user
        self.volumes = volumes or []
        self.host_tmp_dir = host_tmp_dir

        self.cli = None
        self.container = None

    def execute(self):

        logging.debug('Starting docker container from image ' + self.image)

        tls_config = None
        if self.tls_ca_cert and self.tls_client_cert and self.tls_client_key:
            tls_config = tls.TLSConfig(
                    ca_cert=self.tls_ca_cert,
                    client_cert=(self.tls_client_cert, self.tls_client_key),
                    verify=True,
                    ssl_version=self.tls_ssl_version,
                    assert_hostname=self.tls_hostname
            )
            self.docker_url = self.docker_url.replace('tcp://', 'https://')

        self.cli = docker.from_env()

        if ':' not in self.image:
            image = self.image + ':latest'
        else:
            image = self.image

        if self.force_pull or len(self.cli.api.images(name=image)) == 0:
            logging.info('Pulling docker image ' + image)
            for l in self.cli.api.pull(image, stream=True):

                try:
                    output = json.loads(l.decode('utf-8'))
                    if 'status' not in output:
                        output['status'] = None
                except:
                    output = {'status': 'working...'} # Hack
                    # docker-py is producing {} fields in json which cause
                    # ValueError: Extra data... in json.loads()
                    # Doing this skips the first few messages but displays the
                    # rest that don't have {} entries normally.

                logging.info("{}".format(output['status']))



        cpu_shares = int(round(self.cpus * 1024))

        self.environment['INQUIRY_TMP_DIR'] = self.tmp_dir
        self.volumes.append('{0}:{1}'.format(self.host_tmp_dir, self.tmp_dir))

        self.container = self.cli.api.create_container(
                command=self.get_command(),
                cpu_shares=cpu_shares,
                environment=self.environment,
                host_config=self.cli.api.create_host_config(
                    binds=self.volumes,
                    network_mode=self.network_mode
                    ),
                image=image,
                mem_limit=self.mem_limit,
                user=self.user
        )

        self.cli.api.start(self.container['Id'])

        line = ''
        for line in self.cli.api.logs(container=self.container['Id'], stream=True):
            line = line.strip()
            if hasattr(line, 'decode'):
                line = line.decode('utf-8').encode('ascii', 'ignore')
            logging.info(line)

        exit_code = self.cli.api.wait(self.container['Id'])
        if exit_code != 0:
            raise LocalContainerRuntimeError()

        return self.cli.api.logs(container=self.container['Id'])

    def get_command(self):
        return self.command
        # if self.command is not None and self.command.strip().find('[') == 0:
        #     commands = ast.literal_eval(self.command)
        # else:
        #     commands = self.command
        # return commands

    def on_kill(self):
        if self.cli is not None:
            logging.info('Stopping docker container')
            self.cli.stop(self.container['Id'])
