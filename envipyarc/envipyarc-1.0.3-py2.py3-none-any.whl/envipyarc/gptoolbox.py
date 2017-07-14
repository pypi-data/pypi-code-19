"""
ENVI GPToolbox help goes heres
"""
from string import Template
from envipyarclib import GPToolbox as BaseToolbox
from . import templates

_IMPORTS_TEMPLATE = Template('''
import os
import time
import arcpy

from envipyengine import Task
from envipyengine.error import TaskEngineExecutionError, TaskEngineNotFoundError
''')

_EXECUTE_TEMPLATE = Template('''
        task = Task("$taskUri")

        try:
            task_results = task.execute(input_params, cwd=arcpy.env.scratchFolder)
        except (TaskEngineExecutionError, TaskEngineNotFoundError) as err:
            messages.addErrorMessage("Task failed to execute")
            messages.addErrorMessage(err.args[0])
            raise arcpy.ExecuteError

        task_results = task_results['outputParameters']



''')


class GPToolbox(BaseToolbox):  # pylint: disable=too-few-public-methods
    """
    Implementation of the GPToolbox class for ENVI/IDL.
    """
    def __init__(self, tasks=None, alias='envi'):
        super(GPToolbox, self).__init__(tasks,
                                        alias,
                                        _IMPORTS_TEMPLATE,
                                        _EXECUTE_TEMPLATE,
                                        templates)
