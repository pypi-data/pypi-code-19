# -*- coding: utf-8 -*-

"""This Module controls all the command line operations.
It has two features of interest, Watson:

1. The group rqpop, which every other command is under
2. The command 'queue', which enqueues a certainn number of jobs with a number of specification options
"""

# ------------------- #
# Third Party Imports #
# ------------------- #
import click
import multiprocessing as mp


# ------------------- #
#    Local Imports    #
# ------------------- #
from .qpopulator import generate_test_job_box, enqueue_box


@click.group()
def rqpop():
    pass


@click.command()
@click.argument('num_jobs')
@click.argument('max_time')
@click.option('--seed', default=None, help='The seed to be internalized for the number distribution')
@click.option('--dist', default='normal', help='the distirbution to be used for psuedo-random generation')
@click.option('--mnc', default=1, help='the minimum number of cpus to be used, default 1')
@click.option('--mxc',
              default=mp.cpu_count(),
              help='maximum number of cores a job should be able to require, default: maximum configured cores')
@click.option('--mnt', default=1, help='minimum amount of time the jobs should run for, default 1')
@click.option('--q', default='default', help='the queue that the jobs should be enqueued to, default: "default"')
def queue_loads(num_jobs, max_time, seed, dist, mnc, mxc, mnt, q):
    testbox = generate_test_job_box(int(num_jobs),
                                    int(max_time),
                                    seed=seed,
                                    distribution=dist,
                                    min_time=mnt,
                                    min_cpu=mnc,
                                    max_cpu=mxc)
    enqueue_box(testbox, queue=q)


rqpop.add_command(queue_loads, name='queue')

if __name__ == '__main__':
    pass
