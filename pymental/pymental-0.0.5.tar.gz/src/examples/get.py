from examples.poll_status import poll_status
from pymental.client import Conductor


client = Conductor()
job = client.jobs.get(210)
stat = client.jobs.status(268)

poll_status(client=client, job_id=job.id)
