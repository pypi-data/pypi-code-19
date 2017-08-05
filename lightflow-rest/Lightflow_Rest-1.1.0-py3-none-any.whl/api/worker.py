from flask import Blueprint, current_app, request

from lightflow.workers import list_workers, stop_worker
from lightflow.workflows import list_jobs

from lightflow_rest.core.response import ApiResponse, ApiError, StatusCode


api = Blueprint('worker', __name__, url_prefix='/worker')


@api.route('/', methods=['GET'])
def api_list_workers():
    """ Endpoint for listing all workers and, if requested, all running jobs.

    The result is a list of workers. The result can be limited to certain queues by
    using the 'queue' argument. This argument can be used multiple times, e.g.
    ?queue=dag&queue=task. If the 'detail' is set to '1', all jobs running on a
    particular worker are returned as well.
    """

    queues = request.args.getlist('queue')
    if queues is not None and len(queues) == 0:
        queues = None

    details = request.args.get('details', None)
    if details is not None:
        if details not in ['0', '1']:
            raise ApiError(StatusCode.BadRequest,
                           'The details argument must be either 0 or 1.')
        else:
            details = bool(int(details))
    else:
        details = False

    workers = [worker.to_dict() for worker in list_workers(
        config=current_app.config['LIGHTFLOW'],
        filter_by_queues=queues)]

    if details:
        for worker in workers:
            worker['jobs'] = [job.to_dict() for job in
                              list_jobs(current_app.config['LIGHTFLOW'],
                                        filter_by_worker=worker['name'])]

    return ApiResponse({'workers': workers})


@api.route('/', methods=['DELETE'])
@api.route('/<name>', methods=['DELETE'])
def api_stop_worker(name=None):
    """ Endpoint for stopping a single worker or all workers.

    The dynamic path variable <name> is the name of the worker that should be stopped.
    If no <name> is given, all workers are stopped.
    """
    stop_worker(current_app.config['LIGHTFLOW'],
                worker_ids=[name] if name is not None else None)

    return ApiResponse({'success': True})
