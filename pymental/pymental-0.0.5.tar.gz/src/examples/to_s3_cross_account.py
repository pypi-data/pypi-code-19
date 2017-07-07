import os
import time
from examples.poll_status import poll_status
from pymental.client import Conductor
from pymental.models import Job, AuthenticationDetails, PostProcess

now = time.time()
destination = 's3://foo.bar.bucket/elemental/{}/outputs/'.format(now)
client = Conductor()

job_xml = open('examples/payloads/job_example.xml', 'rb')

job = Job.parse(job_xml)

output_group = job.output_groups[0]
settings = getattr(output_group, output_group.type)
settings.destination.uri = destination

auth = AuthenticationDetails(
    authentication_type='cross_account',
    external_account_id=os.environ.get('AWS_ACCOUNT_ID'),
    external_role_name=os.environ.get('AWS_ROLE_NAME'),
    external_id=os.environ.get('AWS_ID'),
)

settings.destination.authentication_details = auth

created_job = client.jobs.create(instance=job)

poll_status(client, created_job.id)
