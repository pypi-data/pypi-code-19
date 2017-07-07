import time
from pymental.meta import SKIP

RUNNING_STATS = ['pending', 'preprocessing', 'running', 'postprocessing']


def poll_status(client, job_id, timeout=60):
    start_time = time.time()
    running = True
    while running:
        status = client.jobs.status(job_id)
        print(
            'Status: {}\t\t'
            'Percentage: {}%\t\t'
            'Started: {}\t\t'
            'Elapsed: {}\t\t'
            'Elapsed in words: {}\t\t'
            'Average FPS: {}\t\t'
            'Errors: {}\t\t'.format(
                status.status,
                status.pct_complete,
                status.start_time,
                status.elapsed,
                status.elapsed_time_in_words,
                status.average_fps,
                [x.message for x in status.error_messages.errors]
                if status.error_messages != SKIP else [],
            )
        )
        if status.status not in RUNNING_STATS:
            running = False
        elif time.time() - start_time > timeout:
            print('Timeout of {}s exceeded.'.format(timeout))
            running = False
        else:
            time.sleep(3)
