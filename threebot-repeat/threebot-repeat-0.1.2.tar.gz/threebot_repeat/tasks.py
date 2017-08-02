# -*- coding: utf-8 -*-
from threebot.tasks import run_workflow
from threebot.models import WorkflowLog
from background_task import background


@background(schedule=1)
def repeat_workflow(workflow_log_id):
    """
    expects an sucessfully logged workflow_log,
    copies the log and runs the workflow
    """
    old_log = WorkflowLog.objects.get(id=workflow_log_id)
    new_log = WorkflowLog(
        workflow=old_log.workflow,
        inputs=old_log.inputs,
        outputs={},
        performed_by=old_log.performed_by,
        performed_on=old_log.performed_on
    )
    new_log.save()
    run_workflow(new_log.id)
