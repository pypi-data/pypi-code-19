import json
import logging

from configfactory.utils import get_client_ip

logger = logging.getLogger(__name__)


def logging_middleware(get_response):
    """
    Logging middleware.
    """
    def middleware(request):
        if '/logs/serve' not in request.path:
            logger.info('[{ip_address}] {method} {path}: {params}'.format(
                ip_address=get_client_ip(request),
                method=request.method.upper(),
                path=request.path,
                params=json.dumps(
                    obj=request.GET if request.method == 'GET' else request.POST
                ),
            ))
        response = get_response(request)
        return response
    return middleware
