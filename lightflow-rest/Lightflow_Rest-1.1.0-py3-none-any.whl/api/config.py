from flask import Blueprint, current_app
import ruamel.yaml as yaml

from lightflow.config import Config

from lightflow_rest.core.response import ApiResponse


api = Blueprint('config', __name__, url_prefix='/config')


@api.route('/')
def list_config():
    """ Endpoint for listing the current configuration.

    The result is a dictionary of the current lightflow configuration.
    """
    return ApiResponse({'config': current_app.config['LIGHTFLOW'].to_dict()})


@api.route('/default')
def default_config():
    """ Endpoint for listing the default configuration of lightflow.

    The result is a dictionary of the default lightflow configuration.
    """
    return ApiResponse({'config': yaml.safe_load(Config.default())})
