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
"""Argument handling tests."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import apache_beam as beam
import argparse
from datetime import datetime
import json
import os
import uuid
import subprocess
import tempfile

from inquiry.framework import util
from inquiry.framework import gcp
from inquiry.framework import task


class Workflow(object):
    """Base Workflow class."""

    def __init__(self):
        """Initialize the base workflow class.."""
        pass

    def define(self):
        """Override this method in defining child workflows."""
        pass

    def run(self, config, test_case=None, config_mode='file'):
        """Run the workflow."""
        self.args, pargs = parse_arguments(job_tag=self.tag,
                                           arg_template=self.arg_template,
                                           config=config)

        if test_case is not None:
            self.args.local = True
            self.args.debug = True
            self.args.dry_run = False
            self.args.job_name = ('test-e2e-%s' % self.args.job_name)

        with beam.Pipeline(argv=pargs) as p:  # will block, fwiw TODO
            self.p = p
            result = self.define()
            util.write_dev(util.dev_fc_to_dict(result),
                           self.args.output,
                           '_workflow-outputs')
            # Question: Does this block until the resulting file arrives at the
            # output location or just until the last operation in the workflow
            # is initiated?

        if test_case is not None:
            return gcp.verify_workflow_outputs(self.args.output,
                                               test_case['expected'])

def load_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config


def apply_config(args, config):

    if config is None:
        return args

    if isinstance(config, unicode):
        config = str(config)

    if isinstance(config, str):
        if not os.path.exists(config):
            msg = ('Tried to load config that does not exist on local'
                   'system: %s' % config)
            util.logging.error(msg)
            raise ValueError(msg)
        util.logging.debug('loaded config: %s' % config)
        config = load_config(config)

    for k, v in config.items():
        if hasattr(args, k):
            setattr(args, k, v)
        else:
            util.logging.debug('saw config with key not known to existing args')

    return args


def get_runner(cloud):
    if cloud:
        return 'DataflowRunner'
    else:
        return 'DirectRunner'


def parse_arguments(job_tag, bucket=None, num_workers=5, project=None,
                    worker_machine_type='n1-standard-1',
                    arg_template=None, requirements=[],
                    config=None):
                     #worker_cache_mb=1000):
    """Build and extend the base argument parser."""

    parser = argparse.ArgumentParser()
    parser.add_argument('--output',
                        dest='output',
                        help='Output stem to use when writing output.')
    parser.add_argument('--output_dir',
                        dest='output_dir',
                        help='Output dir to use when writing output.')
    parser.add_argument('--bucket',
                        dest='bucket',
                        default=bucket,
                        help='Name of the bucket to use for output.')
    parser.add_argument('--project',
                        dest='project',
                        help='Name of the bucket to use for output.')
    parser.add_argument('--cloud',
                        action='store_true',
                        help='Whether to run on the cloud.')
    parser.add_argument('--debug',
                        action='store_true',
                        default=False,
                        help='Whether to run in debug mode.')
    parser.add_argument('--dry_run',
                        action='store_true',
                        default=False,
                        help='Whether to run in dry_run mode.')
    parser.add_argument('--num_workers',
                        dest='num_workers',
                        default=num_workers,
                        help='')
    parser.add_argument('--worker_machine_type',
                        dest='worker_machine_type',
                        default=worker_machine_type,
                        help='')
    parser.add_argument('--local',
                        action='store_true',
                        default=False,
                        help='Whether to run containerized tasks locally (dev).')

    parser = extend_parser(parser, arg_template)

    known_args, pargs = parser.parse_known_args()

    known_args = apply_config(known_args, config)

    # pp = pprint.PrettyPrinter(indent=2)
    # logging.debug(pp.pprint(known_args))
    # logging.info(ppknown_args)

    if known_args.debug:
        import logging as local_logging
        local_logging.getLogger('iqtk').setLevel(local_logging.DEBUG)
    else:
        import logging as local_logging
        local_logging.getLogger('iqtk').setLevel(local_logging.INFO)

    if known_args.project is None:
        known_args.project = util.default_project()

    if known_args.bucket is None:
        known_args.bucket = "gs://" + known_args.project + "-iqtk"
    if not known_args.bucket.startswith("gs://"):
        known_args.bucket = "gs://" + known_args.bucket
    gcp.maybe_create_bucket(known_args.bucket)

    job_name = (str(job_tag) + '-' + datetime.now().strftime('%Y%m%d%H%M%S')
                + '-' + str(uuid.uuid4())) # for now unique and sorted
    known_args.job_name = job_name  # TODO
    known_args.job_tag = job_tag

    if known_args.output_dir is None:
        known_args.output_dir = '%s/output/%s' % (known_args.bucket,
                                                  job_name)

    if known_args.output is None:
        # TODO: can you os.path.join a gs:// path? is that relevant? not like
        # you need cross-system compatibility.
        known_args.output = known_args.output_dir  # + '/' + job_tag

    # staging_location = known_args.bucket + "/staging"
    # temp_location = known_args.bucket + "/temp"
    staging_location = os.path.join(known_args.output_dir, 'staging')
    temp_location = os.path.join(known_args.output_dir, 'tmp')

    pargs.extend([
        '--runner=%s' % get_runner(known_args.cloud),
        '--project=%s' % known_args.project,
        '--staging_location=%s' % staging_location,
        '--temp_location=%s' % temp_location,
        '--job_name=%s' % job_name,
        '--num_workers=%d' % int(known_args.num_workers),
        '--worker_machine_type=%s' % known_args.worker_machine_type,
        '--save_main_session'
        ])

    if known_args.cloud:
        #path = bundle(known_args)
        # pargs.extend(['--extra_package=%s' % bundle_path])
        #path = make_sdist()
        path = '/Users/cb/Desktop/release/iqtk/pip_test/whl/iqtk-0.0.3-py2-none-any.whl'
        #path = 'gs://iqtk/source/iqtk-0.0.3-py2-none-any.whl'
        pargs.extend(['--extra_package=%s' % path])

    if requirements is not None:
        reqs = util.dump_reqs(requirements)
        pargs.extend(['--requirements_file=%s' % reqs])

    return known_args, pargs


def extend_parser(parser, template):
    """Given a parser, extend it with arguments specified in a dictionary."""

    for key, value in template.items():
        if isinstance(value, dict):
            default = (value['default'] if 'default' in value else None)
            h = (value['help'] if 'help' in value else None)
            action = (value['action'] if 'action' in value else None)
            req = (value['required'] if 'required' in value else False)
            req = (True if req else False)
            parser.add_argument('--'+key, default=default, help=h,
                                action=action, required=req)
    return parser
