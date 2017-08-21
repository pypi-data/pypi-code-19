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
"""Functions for submitting and monitoring jobs on the GCG Pipelines service"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime
import pprint
import time
import logging
import os
import re
import tempfile
import json
import uuid

from googleapiclient import discovery

from oauth2client.client import GoogleCredentials

from inquiry.framework import util


def pipelines_service():
    credentials = GoogleCredentials.get_application_default()
    service = discovery.build('genomics', 'v1alpha2', credentials=credentials)
    return service

def _prepare_input_file_list(files):
    for i, f in enumerate(files):
        if isinstance(files[i], util.File):
            files[i] = files[i].remote_path
    return files

def run(polling_interval=4,
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
        debug=False):
    """Run a job on the Google Cloud Genomics job execution system.

    Constructs a job request dictionary which is then passed to the Discovery
    client for the G.C. Genomics service.

    Returns:
        dict: A dictionary containing the post-submission operation metadata.

    """
    service = pipelines_service()

    input_files = _prepare_input_file_list(input_files)

    job_body = {
      'ephemeralPipeline': {
        'projectId': project_id,
        'name': job_name,
        'description': 'Undescribed pipeline run',
        'resources': {
          'disks': [{
            'name': 'datadisk',
            'autoDelete': True,
            'mountPoint': '/mnt/data',
          }],
        },
        'docker': {
          'imageName': runtime_image,
          'cmd': command,
        },
        'inputParameters': [{
          'name': 'inputFile%d' % idx,
          'description': 'Cloud Storage path to an input file',
          'localCopy': {
            'path': 'input/',
            'disk': 'datadisk'
          }
        } for idx in range(len(input_files))],
        'outputParameters': [{
          'name': 'outputPath',
          'description': 'Cloud Storage path for where to copy output',
          'localCopy': {
            'path': 'output/*',
            'disk': 'datadisk'
          }
        }]
      },
      'pipelineArgs': {
        'projectId': project_id,
        'resources': {
          'minimumRamGb': min_ram,
          'zones': region,
          'disks': [{
            'name': 'datadisk',
            'sizeGb': disk_size,
          }],
          'minimumCpuCores': cpu_cores
        },
        'inputs': {
          'inputFile%d' % idx: value for idx, value in enumerate(input_files)
        },
        'outputs': {
          'outputPath': output_dir
        },
        'logging': {
          'gcsPath': log_output_path
        },
      }
    }

    # logging.debug('printing job body...')
    # pp = pprint.PrettyPrinter(indent=2)
    logging.info(job_body)

    job = service.pipelines().run(body=job_body)

    # Should be able to pass dry_run param to pipelines...
    if dry_run:
        ret = {'done': True, 'name': 'untitled_dry_run'}
        logging.debug('doing dry run, returning dummy response: %s' % ret)
        return ret

    op = job.execute()

    return op


def poll_until_complete(op, interval=4):

    logging.debug('Polling until job complete.')

    service = pipelines_service()

    assert interval > 0
    while not op['done']:
        logging.debug('Status: Runnning')
        time.sleep(interval)
        op = service.operations().get(name=op['name']).execute()

    logging.debug('Operation complete')

    time.sleep(30)

    yield op


def construct_outdir(output_dir_arg, label, tag):
    #salt = str(datetime.datetime.now().strftime('%Y%m%d%H%M%S'))
    salt = str(uuid.uuid4())
    output_dir = output_dir_arg + '/' + label + '-'
    if label is not None and tag is not None:
        output_dir += (label + '-')
    output_dir += (salt + '/')
    return output_dir


def job_data_format_validate(job_data):
    if 'done' not in job_data:
        logging.error('malformed job_data object, should have a done field.')
        raise ValueError()

    if 'name' not in job_data:
        logging.error('malformed job_data object, should have a name field.')
        raise ValueError()

    if 'output_files' not in job_data:
        logging.error('the job_data packet should have an '
                      'output_files key storing the array of expected output '
                      'files.')
        raise ValueError()
    if not isinstance(job_data['output_files'], list):
        logging.error('job_data output_files field should store a list of '
                      'File objects, found '
                      'type %s' % type(job_data['output_files']))
        raise ValueError()
    for f in job_data['output_files']:
        if not isinstance(f, util.File):
            logging.error('each element of the job_data output_files list '
                          'should be an object of type File')
            raise ValueError()


def poll_until_complete(job_data, interval=4, debug=False):

    if interval <= 0:
        logging.debug('polling interval should be >= 0, defaulting to 4s.')
        interval = 4

    logging.debug('polling until complete with job data: %s' % job_data)

    job_data_format_validate(job_data)
    name = job_data['name']
    done = job_data['done']
    start_time = datetime.datetime.now()

    logging.debug('Polling until job complete for job: %s' % name)

    service = pipelines_service()

    job_data_tmp = job_data
    while not done:
        elapsed = (datetime.datetime.now() - start_time)
        # TODO: So this elapsed time measure isn't that useful for jobs other
        # than the first one being polled because the elapsed time is reset to
        # zero...
        logging.debug('Running, elapsed time: %s' % elapsed)
        time.sleep(interval)
        job_data_tmp = service.operations().get(name=name).execute()
        #_job_data_format_validate(job_data_tmp)
        done = job_data_tmp['done']

    logging.debug('Completed job: %s' % name)

    #pp = pprint.PrettyPrinter(indent=2)
    #logging.debug(pp.pprint(job_data_tmp))

    # Add the file data to the new job data request object and return
    # TODO: Alternatively just backup output files and repeatedly over-write
    # job data obj...
    job_data_tmp['output_files'] = job_data['output_files']
    yield job_data_tmp


def verify(job_data, debug=False, fail_on_unverified=True):

    job_data_format_validate(job_data)

    verified = True
    logging.debug('Verifying existince of expected job output files.')

    # TODO: actually do the verification...

    logging.debug('Finished verifying expected outputs with '
                 'status: %s' % verified)

    if not verified:
        if fail_on_unverified:
            logging.error('Failed to verify the existence of expected outputs,'
                          ' failing pipeline run.')
            raise Exception()

    # Return only the output files now that we are done with the response
    # metadata.
    yield job_data['output_files']


def gsutil_list(path):
    """List the contents of a GCS storage path."""
    path = _validate_path_parameter(path)
    return util._subprocess('gsutil ls %s' % path)


def _fail_if_spaces(path):
    if len(path.split(' ')) > 1:
        msg
        logging.error()
        raise ValueError('path cannot have spaces: %s' % path)


def _path_type(path):
    assert isinstance(path, str)
    if path.startswith('gs://'):
        return 'GCS'
    elif path.startswith('http'):
        return 'HTTP'
    elif path.startswith('/'):
        return 'Local'
    else:
        return 'Unknown'


def _validate_path_parameter(path):

    # HACK: Adding this fix is a bit unnatural and could cause problems.

    if isinstance(path, util.File):
        if not hasattr(path, 'remote_path'):
            raise ValueError('a file object passed to _validate_path_parameter '
                             'must have a remote_path field')
        path = path.remote_path

    if isinstance(path, unicode):
        path = str(path)

    if not isinstance(path, str):
        raise ValueError('path parameter must be of type string, saw: '
                         '%s' % path)
    if len(path) == 0:
        raise ValueError('path parameter string must have length at least '
                         'one, saw: %s' % path)
    _fail_if_spaces(path)

    return path


def stage_data(source, target):
    """Copy the contents of one directory to another.

    Attributes:
        source (str): The directory whose contents will be copied.
        target (str): The directory to which the source contents will be copied.

    TODO: Looping through a set of files and gsutil cp ... on each is not nearly
    as fast as gsutil cp -m ... on all at once. Will become an issue for pipelines
    that generate a very large number of files.

    """
    logging.debug('staging files: %s to %s' % (source, target))
    source = _validate_path_parameter(source)
    target = _validate_path_parameter(target)

    pts, ptt = _path_type(source), _path_type(target)

    if pts is 'Unknown' or ptt is 'Unknown':
        raise ValueError('stage data received paths of unknown type: %s, %s' % (
            source, target
        ))

    if pts is 'Local' and ptt is 'Local':
        if not os.path.exists('/tmp/iq'):
            os.system('mkdir /tmp/iq')
        _local_dir_stage_data(source, target)
    elif (pts is 'Local' and ptt is 'GCS') or (pts is 'GCS' and ptt is 'Local'):
        _gsutil_stage_data(source, target)
    else:
        raise ValueError('staging between the path types provided is not yet '
                         'implemented: %s (%s), %s (%s)' % (source, pts,
                                                            target, ptt))


def _local_dir_stage_data(source, target):
    logging.debug('staging files with local copy: %s to %s' % (source, target))

    # safety for local development:
    if not target.startswith('/tmp/iq') or not source.startswith('/tmp/iq'):
        raise ValueError('during development, in the interest of safety, copy '
                         'between local directories not prefixed with /tmp/iq is '
                         'not allowed. Saw: %s, %s' % (source, target))

    if not os.path.exists(source):
        raise ValueError('attempted copy from source directory that does not '
                         'exist on the local file system: %s' % source)

    util._subprocess('cp %s %s/' % (source, target))


def _gsutil_stage_data(source, target):
    logging.debug('staging files with gsutil: %s to %s' % (source, target))
    # return util._subprocess('exit 1')
    return util._subprocess('gsutil cp %s %s/' % (source, target))


def gcs_path_exists(path):
    logging.debug('checking for path existence: %s' % path)
    return gsutil_list(path) is not None


def maybe_create_bucket(bucket):
    """Create a storage bucket if it does not already exist.

    TODO:
        * Gracefully handle cases where don't have access or already exists.
    """
    with open(os.devnull, 'w') as dev_null:
        try:
            subprocess.check_output(['gsutil', 'mb', bucket],
                                    stderr=dev_null).strip()
        except:
            # TODO catch cases where the bucket already exists and is not owned
            # by you or where the provided name is invalid.
            pass


def _checksum_from_lsL_garble(garble, cks_type="md5"):
    """

    Notes:
        * Assumes that there is a checksum to be found a fails if there isn't.
    """
    for thing in garble:
        if len(thing.split('(%s)' % cks_type)) > 1:
            return thing.split(' ')[-1]
    raise Exception('md5 record not found in gcs ls -L garbledigook.')


def _check_cks_type(cks_type):
    if cks_type not in ['md5', 'crc32c']:
        raise ValueError('cks_type must be either md5 or crc32c')


def _require_gcs_path_exists(file_path):
    if not gcs_path_exists(file_path):
        raise ValueError('Can not obtain checksum for non-existent GCS file.')


def gcs_get_checksum(file_path, cks_type="md5"):
    """Obtain the stored MD5 value for a file on GCS from its meta field.

    Each file stored on Google Cloud Storage has a set of metadata fields
    associated withit including an md5 hash value. Here we obtain the md5 hash
    value for the specified file.

    Example:

        assert gcs_file_md5('gs://bkt/file.txt') is 'iDsXcCeefxZv7OPaLmV+9w=='

    Args:
        file_path (str): The path to the file on cloud storage.

    Returns:
        str: The obtained MD5 value.

    """
    file_path = _validate_path_parameter(file_path)

    logging.debug('obtaining GCS file md5: %s' % file_path)

    _check_cks_type(cks_type)
    _require_gcs_path_exists(file_path)

    raw = util._subprocess('gsutil ls -L %s' % file_path)
    return _checksum_from_lsL_garble(raw, cks_type)


def collect_workflow_outputs(remote_directory):
    """Given a path in cloud storage, obtains workflow output file paths.

    The paradigm we're working with currently is to have the last step in a
    workflow be to write to storage a file prefixed with '_workflow-outputs'
    that lists the File objects that were generated by this run.

    Args:

        remote_directory (str): The remote directory on cloud storage where a
            a workflow outputs file should exist, that will be read.

    """

    if isinstance(remote_directory, unicode):
        remote_directory = str(remote_directory)

    logging.info('gcs_verify_checksums verifying file collection in '
                 'remote dir: %s' % remote_directory)
    contents = gsutil_list(remote_directory)
    logging.debug('collect_workflow_outputs: %s' % contents)
    outputs = [c for c in contents if c.split('/')[-1].startswith('_workflow-outputs')]
    if len(outputs) != 1:
        raise ValueError('collect_workflow_outputs expects to find only one '
                         'outputs file in the workflow output '
                         'directory, saw: %s' % outputs)

    # Copy the outputs file to local tmp and open it
    tmpdir = tempfile.mkdtemp(prefix='/tmp/iq')
    stage_data(outputs[0], tmpdir)
    fname = outputs[0].split('/')[-1]
    paths = []
    with open(tmpdir + '/' + fname, 'r') as f:
        # For each record in the outputs file, obtain the path and append it
        # to the output paths array.
        output = f.readline()
        # Parse the File JSON into a file object, then return its
        # remote_path attribute
        line = output.strip().replace('\'', '"').replace('None', 'null')
        logging.info(line)
        files = json.loads(line)
        for f in files:
            if 'remote_path' not in f:
                raise ValueError('all file objects should have remote_path '
                                 'attributes, saw: %s' % f)
            paths.append(f['remote_path'])

    return paths


def _require_type(val, ty, label='regex'):
    if not isinstance(val, ty):
        raise ValueError('%s must be a %s' % (label, ty))


def _regex_match_list(searchme, reg):
    logging.debug('regex_match_list, with regex %s, is searching %s' % (
        reg, searchme
    ))

    _require_type(reg, str, 'regex')
    if len(reg) == 0:
        raise ValueError('regex string must have len > 0')
    p = re.compile(reg, re.IGNORECASE)
    hits = []
    for t in searchme:
        if p.findall(t):
            hits.append(t)
    logging.debug('regex_match_list found hits: %s' % hits)
    return hits


def _path_list_verify_checksums(paths, cases):

    files = {c.split('/')[-1]:c for c in paths}

    if len(paths) == 0:
        logging.info('gcs_verify_checksums found remote directory empty')
        return False
    else:
        logging.info('gcs_verify_checksums found files in remote directory: '
                     '%s' % files)

    verified = True
    # For each case, obtain a list of files matchig the specified pattern.
    for c in cases:

        logging.info('gcs_verify_checksums considering case: %s' % c)

        hits = _regex_match_list(files.keys(), c['pattern'])

        # Note: The presumption here is that if a case is provided, it should match
        # something. So if it searches the remote dir for that pattern and doesn't
        # find a file it will indicate unverified instead of passive verified.
        if len(hits) == 0:
            verified = False
        else:
            logging.info('gcs_verify_checksums found hits in target dir: %s' % hits)

        for h in hits:
            # For each, match, verify the file matches the specified checksum
            cks = gcs_get_checksum(files[h])
            if not (cks == c['checksum']):
                verified = False

    return verified


def gcs_verify_checksums(remote_directory, cases):
    """
    This needs to be refactored. Originally I meant to checksum verify files in
    a single directory but instead we'll want to be able to do this for an
    arbitrary list of files.
    """

    logging.info('gcs_verify_checksums verifying file collection in '
                 'remote dir: %s' % remote_directory)
    logging.info('gcs_verify_checksums verifying cases: %s' % cases)

    if not isinstance(cases, list) or len(cases) == 0:
        raise ValueError('gcs_verify_checksum cases should be a non-empty '
                         'array')

    # Obtain the contents of the remote directory
    contents = gsutil_list(remote_directory)
    return _path_list_verify_checksums(contents, cases)


def verify_workflow_outputs(outputs_location, expected):
    outputs = collect_workflow_outputs(outputs_location)
    return _path_list_verify_checksums(outputs, expected)
