from localstack import config
from localstack.services.infra import *
from localstack.services.apigateway import apigateway_listener
from localstack_ext.utils import licensing


# register default plugins

def register_localstack_plugins():

    # read license and prepare environment
    initialized = licensing.prepare_environment()
    if not initialized:
        return

    # now import files
    try:
        from localstack_ext.services.cognito import cognito_starter
        from localstack_ext.services.cognito import cognito_idp_api
        from localstack_ext.services.iam import iam_starter
        from localstack_ext.services.sts import sts_starter
    finally:
        # clean up
        licensing.cleanup_environment()

    # add interceptors to all relevant APIs
    apigateway_listener.update_apigateway = cognito_idp_api.wrap_api_method(
        'apigateway', apigateway_listener.update_apigateway)

    # register_plugin(Plugin('ec2', start=ec2_starter.start_ec2))
    register_plugin(Plugin('sts', start=sts_starter.start_sts))
    register_plugin(Plugin('iam', start=iam_starter.start_iam))
    register_plugin(Plugin('cognito-idp', start=cognito_starter.start_cognito_idp))
    register_plugin(Plugin('cognito-identity', start=cognito_starter.start_cognito_identity))
