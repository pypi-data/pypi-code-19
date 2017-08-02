# -*- coding: utf-8 -*-
import re

from django import template

from threebot.models import WorkflowLog

register = template.Library()


@register.assignment_tag
def repetitive_task_to_workflow_log(bg_task):
    """Given a repetitive background task, parses the task_params to retrieve the workflow log."""
    # assuming the first integer in task_params is the WorkflowLog.id
    try:
        log = WorkflowLog.objects.get(id=re.findall(r'^\D*(\d+)', bg_task.task_params)[0])
    except Exception:
        log = None

    return log
