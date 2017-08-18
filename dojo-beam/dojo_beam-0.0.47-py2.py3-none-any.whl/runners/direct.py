from __future__ import absolute_import, print_function, unicode_literals

import os
import random
import subprocess
import apache_beam as beam

from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions
from dojo.runners.job import JobRunner


class DirectBeamRunner(JobRunner):

    def run(self, job, config):
        project_id = config['cloud']['project']

        dataset_name = job.config['name'].replace('_', '-')
        '%s--%s-%s' % (project_id, dataset_name, random.randint(1, 1000))

        options = PipelineOptions()
        setup_options = options.view_as(SetupOptions)
        setup_options.save_main_session = True
        setup_options.setup_file = os.path.join(os.getcwd(), 'setup.py')

        job.setup()

        keyfile_path = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        if keyfile_path and os.path.isfile(keyfile_path):
            subprocess.check_call(['gcloud', 'config', 'set', 'project', config['cloud']['project']])
            subprocess.check_call(['gcloud', 'auth', 'activate-service-account', '--key-file', keyfile_path])

        pipeline = beam.Pipeline(runner=str('direct'), options=options)

        job.run(pipeline)

        result = pipeline.run()
        result.wait_until_finish()
        job.teardown()
