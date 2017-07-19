from django.db import close_old_connections

from mushroom.rpc.middleware import Middleware


class CloseOldConnectionsMiddleware(Middleware):

    def __call__(self, request):
        try:
            return self.get_response(request)
        finally:
            close_old_connections()
