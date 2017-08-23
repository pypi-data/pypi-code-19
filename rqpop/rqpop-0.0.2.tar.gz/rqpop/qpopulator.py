# -*- coding: utf-8 -*-
""" This module has two useful functions:
        generate_test_job_box: generates a BlockBox with n JobBlocks containing jobs with x cpu width and z cpu height
        enqueue_box: enqueues the jobs in the blocks in the input box
    This module is designed to test a fork of rq modified to optimize tree alignment job queues.
"""


# ------------------- #
# Third Party Imports #
# ------------------- #
from stressypy import cpustresser
from redis import Redis
from rq import Queue
import multiprocessing as mp
from scipy import random as rdm


JobBlock = cpustresser.JobBlock



class BlockBox:
    """# A class designed to hold the JobBlocks
    this allows multiple job creating sessions to be done concurrently and each saved to
    a unique 'box'
    """

    total_boxes = 0

    def __init__(self, block_list, boxid):
        self.blocks = block_list
        self.blocksheld = len(block_list)
        self.id = boxid
        BlockBox.total_boxes = len(block_list)

    def add_block(self, block):
        self.blocks.append(block)
        BlockBox.total_boxes += 1

    def remove_block(self, blockid):
        for block in self.blocks:
            if block.id == blockid:
                self.blocks.remove()
                BlockBox.total_boxes -= 1
            else:
                raise KeyError('that block id is not found in this box')


def generate_test_job_box(job_count,
                          max_time,
                          min_time=1,
                          min_cpu=1,
                          max_cpu=mp.cpu_count(),
                          distribution='normal',
                          seed=None):
    """ Generates job_count nmber of test jobs and stores
    :param job_count: Number of jobs desired
    :param max_time: maximum amount of time the jobs should run for
    :param min_time: minimum amount of time the jobs should run for, default 1
    :param min_cpu: minimum number of cores the jobs should run on, default 1
    :param max_cpu: maximum number of cores a job should be able to require, default: maximum configured cores
    :param distribution: the distribution type that the random sizes of the jobs should be pulled from
    :param seed: the seed that the distribution should use - allows for repeatable results
    :return: box holding block objects which hold the functions and their relevant specifications
    """



    rdm.seed(seed=seed)
    random_cpu_list = []
    random_time_list = []
    mean_cpu = (max_cpu-min_cpu)/2
    cpudev = mean_cpu-min_cpu/4
    mean_time = (max_time - min_time) / 2
    timedev = mean_time - min_time / 4
    # use the appropriate scipy function for the appropriate case
    if distribution == 'normal':  # Gaussian
        random_cpu_list = rdm.normal(mean_cpu, cpudev, job_count)
        random_time_list = rdm.normal(mean_time, timedev, job_count)
    elif distribution == 'power':  # Exponential
        random_cpu_list = [int(round(num*max_cpu)) for num in rdm.power(2, job_count)]
        random_time_list = [int(round(num*max_time)) for num in rdm.power(2, job_count)]
    elif distribution == 'spike':  # Extreme Dirac - One value only
        random_cpu_list = [rdm.randint(min_cpu, max_cpu) for _ in range(job_count)]
        random_time_list = [rdm.randint(min_time, max_time) for _ in range(job_count)]
    elif distribution == 'box':  # Uniform or box distribution
        random_cpu_list = rdm.uniform(min_cpu, max_cpu, job_count)
        random_time_list = rdm.uniform(min_time, max_time, job_count)
        pass

    estimate_uncertainty_time = [rdm.normal(0, num/10, None) for num in random_time_list]

    # cap the outer limits of the random numbers so they dont give negative time or more cpu cores than
    # possible/ more than max time
    for i, num in enumerate(random_cpu_list):
        if num < 1:
            random_cpu_list[i] = 1
        elif num > max_cpu:
            random_cpu_list[i] = max_cpu
        else:
            random_cpu_list[i] = int(round(random_cpu_list[i]))

    for i, num in enumerate(random_time_list):
        if num < 1:
            random_time_list[i] = 1
        elif num > max_time:
            random_time_list[i] = max_time
        else:
            random_time_list[i] = int(round(random_time_list[i]))

    # Create a new box to store each block in, create a list of blocks, store it in the box
    block_lst = []
    for i, num in enumerate(random_cpu_list):
        job = cpustresser.create_job(random_cpu_list[i], random_time_list[i])
        block_lst.append(job)
    box = BlockBox(block_lst, 1)

    return box


def enqueue_box(inputbox, queue='default'):
    """Simply enqueues every job in every block in the input box."""

    redis_conn = Redis()
    q = Queue(queue, connection=redis_conn)
    for block in inputbox.blocks:
        q.enqueue(block.func, args=block.func_args, kwargs=block.func_kwargs)

    for i, _ in enumerate(inputbox.blocks):
        print(inputbox.blocks[i].job)
