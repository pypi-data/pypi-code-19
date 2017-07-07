from examples.poll_status import poll_status
from pymental.models import Input, JobProfile
from pymental.client import Conductor


client = Conductor()

profile_xml = open('examples/payloads/job_profile_example.xml', 'rb')
input_xml = open('examples/payloads/input_example.xml', 'rb')

job_input = Input.parse(input_xml)
job_input.file_input.uri = 'http://foobar.com/testvideo/quz.mp4'

job_profile = JobProfile.parse(profile_xml)

created_job = client.jobs.create_from_profile(
    input=job_input,
    profile=job_profile,
)

poll_status(client=client, job_id=created_job.id)
