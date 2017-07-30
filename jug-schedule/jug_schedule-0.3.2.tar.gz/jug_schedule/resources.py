# -*- coding: utf-8 -*-

from jug.task import TaskGenerator

__all__ = [
    "ResourcesTaskGenerator",
]

VALID_PARAMS = ("cpu", "mem", "queue")


class _WrapTaskGenerator(TaskGenerator):
    def __init__(self, f, resources):
        super(_WrapTaskGenerator, self).__init__(f)
        self._resources = resources

    def __call__(self, *args, **kwargs):
        task = super(_WrapTaskGenerator, self).__call__(*args, **kwargs)
        task._resources = self._resources
        return task


def ResourcesTaskGenerator(**resources):
    """
    @ResourcesTaskGenerator(cpu=10, mem=100)
    def f(arg0, arg1, ...)
        ...

    Behaves the same as jug's TaskGenerator but allows specifying resources
    which will then be used by the scheduler on requests to the queueing
    system.

    Current list of supported arguments ::

        cpu   = Number of cpu cores/threads to allocate
        mem   = Maximum memory necessary (in MB)
        queue = Name of queue to use

    All of the above are optional.

    Also note that these arguments are ignored if running with 'jug execute'.
    They are only relevant when using 'jug schedule'
    """
    for key in resources:
        assert key in VALID_PARAMS, "Invalid argument given {0}".format(key)

    def task_generator_wrapper(f):
        return _WrapTaskGenerator(f, resources)

    return task_generator_wrapper


# vim: ai sts=4 et sw=4
