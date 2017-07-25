'''
When script is executed:

- POST following to server:
    * All param values
    * File name
    * Git status
- Receive job ID

During execution:
    - Report progress
    - Report final result

Head-node service:
    - Persist progress
    - Serves web view
    - Adjust priority of jobs based on progress

Example:

Submit tasks:
    quora_text_pair.py --width 50 --depth 2 --L2 1e-6
    ...
    quora_text_pair.py --width 300 --depth 2 --L2 1e-6
    quora_text_pair.py --width 50 --depth 1 --L2 1e-6
    ...
    quora_text_pair.py --width 300 --depth 1 --L2 1e-6
    etc

width = [50, 100, 150, 200, 250, 300]
depth = [0, 1, 2, 3, 4]
L2 = [1e-8, 1e-7, 1e-6, 1e-5, 1e-4]
6 * 5 * 5 = 150 jobs

All jobs are submitted to the Torque scheduler, which queues them. The jobs declare how
many processors and how much memory they require. The scheduler uses this to
allocate jobs to machines. When a job finishes, the next one from the queue
begins.

When the job begins to execute, it POSTs its config to the server, and receives
back a job ID, so that it can publish its progress.

Let's say we start off with the following jobs running, and all others queued:

a) width=50, depth=0, L2=1e-8
b) width=100, depth=1, L2=1e-8
c) width=300, depth=4, L2=1e-4
d) width=300, depth=4, L2=0.0

Let's say job d is both slow and inaccurate. Instead of running this to
completion, we'd like to pause the job and try out other settings. The head
service can do this: as we POST results in, the head service can see that the
job is less promising, and tell Torque to assign it a low priority.
'''


