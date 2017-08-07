from __future__ import division

from concurrent import futures
from contextlib import contextmanager
from functools import partial
import logging
import uuid

from watchbot_progress.progress import WatchbotProgress


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


def create_job(parts, jobid=None, workers=8, table_arn=None, topic_arn=None, metadata=None):
    """Create a reduce mode job

    Handles all the details of reduce-mode accounting (SNS, partid and jobid)
    """

    jobid = jobid if jobid else str(uuid.uuid4())

    progress = WatchbotProgress(table_arn=table_arn, topic_arn=topic_arn)
    progress.set_total(jobid, parts)

    if metadata:
        progress.set_metadata(jobid, metadata)

    annotated_parts = []
    for partid, part in enumerate(parts):
        part.update(partid=partid)
        part.update(jobid=jobid)
        part.update(metadata=metadata)
        annotated_parts.append(part)

    # Send SNS message for each part, concurrently
    _send_message = partial(progress.send_message, subject='map')
    with futures.ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(_send_message, annotated_parts)

    return jobid


@contextmanager
def Part(jobid, partid, table_arn=None, topic_arn=None, **kwargs):
    """Context Manager for parts of an ecs-watchbot reduce job.

    Params
    ------
    jobid
    partid
    table_arn
    topic_arn

    """
    progress = WatchbotProgress(table_arn=table_arn, topic_arn=topic_arn)

    if 'failed' in progress.status(jobid):
        raise RuntimeError('job {} already failed'.format(jobid))

    try:
        # yield control to the context block which processes the message
        yield
    except:
        progress.fail_job(jobid, partid)
        raise
    else:
        all_done = progress.complete_part(jobid, partid)
        if all_done:
            status = progress.status(jobid)
            metadata = status.get('metadata', None)
            message = {
                'jobid': jobid,
                'metadata': metadata}
            progress.send_message(message, subject='reduce')
