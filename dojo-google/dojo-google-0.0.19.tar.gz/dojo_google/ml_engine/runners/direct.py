from __future__ import absolute_import, print_function, unicode_literals

import os
import json
import tempfile
import subprocess

from dojo.runners.job import JobRunner


class GoogleCloudAuth(object):

    def __init__(self, secrets):
        self.secrets = secrets

    def __enter__(self):
        self.f = tempfile.NamedTemporaryFile('w')
        json.dump(self.secrets, self.f)
        self.f.flush()
        self.previous_credentrials_file = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.f.name

    def __exit__(self, *args):
        if self.previous_credentrials_file:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.previous_credentrials_file
        else:
            del os.environ['GOOGLE_APPLICATION_CREDENTIALS']
        self.f.close()


class DirectMLEngineRunner(JobRunner):

    def run(self, job, config):
        job.setup()
        with GoogleCloudAuth(job.secrets['store']['connection']):
            options = []
            for input_key, input_path in job.input_paths().items():
                options += ['--%s_uri' % (input_key, ), job.store.as_uri(input_path)]
            options += ['--output_uri', job.store.as_uri(job.output_path('models'))]
            for key, value in job.config['trainer'].items():
                if key not in ['module', ]:
                    options += ['--%s' % (key, ), str(value)]
            subprocess.check_call([
                'gcloud', 'ml-engine', 'local', 'train',
                '--module-name', job.config['trainer']['module'],
                '--package-path', config['package'],
                '--distributed',
                '--'
            ] + options)
