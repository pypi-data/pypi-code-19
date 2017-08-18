from __future__ import absolute_import, print_function, unicode_literals

import os
import io
import subprocess

from setuptools import sandbox
from oauth2client.client import GoogleCredentials
from googleapiclient import discovery

from dojo.runners.job import JobRunner


class CloudMLEngineRunner(JobRunner):

    def run(self, job, config):
        job.setup()
        package_path = self._upload_package(job)
        job_id = '%s_%s' % (job.config['name'], job.config['timestamp'])
        job_spec = self._build_job_spec(job, job_id, package_path)
        project_id = 'projects/%s' % (config['cloud']['project'], )
        credentials = GoogleCredentials.get_application_default()
        cloudml = discovery.build('ml', 'v1', credentials=credentials)
        request = cloudml.projects().jobs().create(body=job_spec, parent=project_id)
        response = request.execute()
        print(response)
        subprocess.check_call(['gcloud', 'beta', 'ml', 'jobs', 'stream-logs', job_id])

    def _upload_package(self, job):
        sandbox.run_setup('setup.py', ['clean', 'sdist'])
        package_filename = [key for key in os.listdir('dist') if key.endswith('.tar.gz')][-1]
        local_package_path = os.path.join('dist', package_filename)
        package_path = os.path.join(job.output_path('staging'), package_filename)
        with open(local_package_path, 'rb') as f:
            job.store.write_file(package_path, io.BytesIO(f.read()))
        return package_path

    def _build_job_spec(self, job, job_id, package_path):
        cloud_option_keys = {
            'scale_tier': 'scaleTier',
            'master_type': 'masterType',
            'worker_type': 'workerType',
            'parameter_server_type': 'parameterServerType',
            'worker_count': 'workerCount',
            'parameter_server_count': 'parameterServerCount',
            'region': 'region'
        }
        cloud_option_defaults = {
            'region': 'us-east1'
        }
        cloud_options = {}
        if 'cloud' in job.config and 'ml_engine' in job.config['cloud']:
            for from_key, to_key in cloud_option_keys.items():
                if from_key in job.config['cloud']['ml_engine']:
                    cloud_options[to_key] = job.config['cloud']['ml_engine'][from_key]
        for key, default_value in cloud_option_defaults.items():
            if key not in cloud_options:
                cloud_options[key] = default_value
        trainer_options = []
        for input_key, input_path in job.input_paths().items():
            trainer_options += ['--%s_uri' % (input_key, ), job.store.as_uri(input_path)]
        trainer_options += ['--output_uri', job.store.as_uri(job.output_path('models'))]
        for key, value in job.config['trainer'].items():
            if key not in ['module', ]:
                trainer_options += ['--%s' % (key, ), str(value)]
        options = {
            'packageUris': [job.store.as_uri(package_path), ],
            'pythonModule': job.config['trainer']['module'],
            'args': trainer_options,
            'runtimeVersion': '1.0'
        }
        options.update(cloud_options)
        return {
            'jobId': job_id,
            'trainingInput': options
        }
