import os
import time

from examples.poll_status import poll_status
from pymental.client import Conductor
from pymental.models import Job, AuthenticationDetails, Location, PostProcess

now = time.time()
destination = 's3://foo.bar.bucket/elemental/{}/original/'.format(now)

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

client = Conductor()
job_xml = open('examples/payloads/job_example.xml', 'rb')

job = Job.parse(job_xml)

auth = AuthenticationDetails(
    authentication_type='basic',
    username=AWS_ACCESS_KEY_ID,
    password=AWS_SECRET_ACCESS_KEY,
)

# this seems to not have any effect, waiting for elemental support reply on this
job.post_process = PostProcess(
    processed=Location(
        uri=destination,
        authentication_details=auth
    )
)

created_job = client.jobs.create(instance=job)

poll_status(client, created_job.id)
