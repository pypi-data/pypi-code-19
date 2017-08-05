from flask import Blueprint, current_app, request

from lightflow.workflows import start_workflow, stop_workflow, list_workflows, list_jobs
from lightflow.models.exceptions import WorkflowArgumentError, WorkflowImportError
from lightflow.queue.const import JobStatus, JobType

from lightflow_rest.core.response import StatusCode, ApiResponse, ApiError


api = Blueprint('workflow', __name__, url_prefix='/workflow')


@api.route('/<name>', methods=['POST'])
def api_start_workflow(name):
    """ Endpoint for starting a new workflow.

    The dynamic path variable <name> is the name of the workflow that should be started.
    The endpoint accepts a parameter keep_data (e.g. ?keep_data=1) that tells the system
    to not delete the workflow data in the persistent storage. Arguments for the
    workflow are sent as form-encoded data.
    """
    try:
        keep_data = request.args.get('keep_data', None)
        if keep_data is not None:
            if keep_data not in ['0', '1']:
                raise ApiError(StatusCode.BadRequest,
                               'The keep_data argument must be either 0 or 1.')
            else:
                keep_data = bool(int(keep_data))
        else:
            keep_data = False

        job_id = start_workflow(name=name,
                                config=current_app.config['LIGHTFLOW'],
                                clear_data_store=not keep_data,
                                store_args=request.form.to_dict())

        return ApiResponse({'id': job_id})
    except (WorkflowArgumentError, WorkflowImportError) as err:
        raise ApiError(StatusCode.InternalServerError, str(err))


@api.route('/', methods=['DELETE'])
@api.route('/<name>', methods=['DELETE'])
def api_stop_workflow(name=None):
    """ Endpoint for stopping all or a single running workflow.

    This endpoint can be called with either a dynamic path variable <name>, specifying
    the job that should be stopped, or without one which will stop all running workflows.
    """
    try:
        stop_workflow(current_app.config['LIGHTFLOW'],
                      names=[name] if name is not None else None)
        return ApiResponse({'success': True})
    except Exception as err:
        raise ApiError(StatusCode.InternalServerError, str(err))


@api.route('/', methods=['GET'])
@api.route('/active', methods=['GET'])
def api_list_active_workflows():
    """ Endpoint for listing all active workflows together with their dags and tasks.

    The result is a list of dictionaries comprised of the workflow fields with workflow
    information and lists of all the dags and tasks that are currently running.
    """
    workflows = {}
    for job in list_jobs(current_app.config['LIGHTFLOW'], status=JobStatus.Active):
        if job.workflow_id not in workflows:
            workflows[job.workflow_id] = {'dags': [], 'tasks': []}

        if job.type == JobType.Dag:
            workflows[job.workflow_id]['dags'].append(job.to_dict())
        elif job.type == JobType.Task:
            workflows[job.workflow_id]['tasks'].append(job.to_dict())
        else:
            workflows[job.workflow_id] = {**workflows[job.workflow_id],
                                          **job.to_dict()}

    return ApiResponse({'workflows': list(workflows.values())})


@api.route('/registered', methods=['GET'])
def api_list_registered_workflows():
    """ Endpoint for listing all registered workflows.

    The result is a list of dictionaries comprised of the workflow fields with workflow
    information.
    """
    return ApiResponse({'workflows': [
        job.to_dict() for job in list_jobs(current_app.config['LIGHTFLOW'],
                                           status=JobStatus.Registered,
                                           filter_by_type=JobType.Workflow)]})


@api.route('/reserved', methods=['GET'])
def api_list_reserved_workflows():
    """ Endpoint for listing all reserved workflows.

    The result is a list of dictionaries comprised of the workflow fields with workflow
    information.
    """
    return ApiResponse({'workflows': [
        job.to_dict() for job in list_jobs(current_app.config['LIGHTFLOW'],
                                           status=JobStatus.Reserved,
                                           filter_by_type=JobType.Workflow)]})


@api.route('/available', methods=['GET'])
def api_list_available_workflows():
    """ Endpoint for listing all available workflows.

    Returns a list of available workflows as json under the key 'workflows'.
    The name, parameters and docstring for each workflow is returned.
    """
    result = {'workflows': []}

    for wf in list_workflows(current_app.config['LIGHTFLOW']):
        result['workflows'].append({
            'name': wf.name,
            'parameters': [
                {
                    'name': param.name,
                    'type': param.type.__name__,
                    'docs': param.help,
                    'default': param.default
                } for param in wf.parameters
            ],
            'docs': wf.docstring.split('\n')[0] if wf.docstring is not None else ''

        })

    return ApiResponse(result)
