
from webargs.flaskparser import use_args
from flask_restful import Resource

from .exceptions import AuthResolveRequestUserError

def create_auth_endpoint(AuthTokenFlow):

    flow = AuthTokenFlow

    class AuthEndpoint(Resource):

        @use_args(flow.endpoint_args)
        def post(self, args):
            user_id = None
            token = args.get('token')
            if token:
                flow.check_token(token)
                token = flow.renew_token(token)
            else:
                user_id = flow.resolve_request_user_id()
                if not user_id:
                    raise AuthResolveRequestUserError(
                        "Could not resolve user from request")
                token = flow.new_token(user_id)

            return {'token': token}

    return AuthEndpoint
