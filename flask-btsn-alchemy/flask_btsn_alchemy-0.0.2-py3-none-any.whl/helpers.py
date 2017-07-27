# Standard Lib imports
import os
import time
# Third-party imports
from flask import g
# from flask_restless import ProcessingException
# from jsonschema import validate, ValidationError, FormatChecker
from sqlalchemy.exc import OperationalError
# BITSON imports


def create_folders(app):
    """Creates folder structure and every config variable ending with
    '_FOLDER'. """
    for k, v in sorted(app.config.items()):
        if '_FOLDER' in k:
            if os.path.isdir(v):
                continue
            else:
                os.mkdir(v)


def wait_db_connection(app, db, timeout=0):
    connected_to_db = False
    while not connected_to_db:
        try:
            db.engine.connect()
            connected_to_db = True
            app.logger.debug('Connected to {}'.format(
                app.config.get('SQLALCHEMY_DATABASE_URI')
            ))
        except OperationalError as error:
            timeout += 2
            time.sleep(timeout)
            app.logger.critical(error)
            app.logger.critical('Retrying in %d seconds...' % timeout)


def register_blueprints(app, blueprints, url_prefix=None):
    for blueprint in blueprints:
        app.register_blueprint(blueprint,
                               url_prefix=url_prefix or blueprint.url_prefix)


def register_apis(apimanager, apis, url_prefix):
    for api in apis:
        apimanager.create_api(api, methods=api.methods, url_prefix=url_prefix,
                              preprocessors=api.preprocessors,
                              postprocessors=api.postprocessors,
                              results_per_page=api.results_per_page,
                              max_results_per_page=api.max_results_per_page,
                              include_methods=api.include_methods,
                              validation_exceptions=api.validation_exceptions,
                              include_columns=api.include_columns,
                              exclude_columns=api.exclude_columns,
                              allow_patch_many=api.allow_patch_many,
                              allow_delete_many=api.allow_delete_many,
                              )


def clean_search_preprocessor(search_params=None, filter_id=True,
                              filter_erased=True, **kw):
    # This checks if the preprocessor function is being called before a
    # request that does not have search parameters.
    if search_params is None:
        return
    # Create the filter you wish to add; in this case, we include only
    # instances with ``id`` not equal to 0.
    id_0 = dict(name='id', op='neq', val=0)
    not_erased = dict(name='erased', op='eq', val=False)
    # Check if there are any filters there already.
    if 'filters' not in search_params:
        search_params['filters'] = []
    # *Append* your filter to the list of filters.
    if filter_id:
        search_params['filters'].append(id_0)
    if filter_erased:
        search_params['filters'].append(not_erased)


def get_location_id_preprocessor(search_params=None, **kwargs):
    if search_params is None:
        return
    # Create the filter you wish to add; in this case, we include only
    # instances with ``id`` not equal to 0.
    location_id = dict(name='location_id', op='eq', val=g.location.id)
    if not location_id:
        return
    # Check if there are any filters there already.
    if 'filters' not in search_params:
        search_params['filters'] = []
    # *Append* your filter to the list of filters.
    if not g.location.id == 0:
        search_params['filters'].append(location_id)


def post_location_id_preprocessor(data=None, **kwargs):
    if g.location.id != 0:
        data['location_id'] = g.location.id


# def validate_post_json_schema(data, cls, **kwargs):
#     try:
#         validate(data, cls.schema, format_checker=FormatChecker())
#     except ValidationError as e:
#         raise ProcessingException(code=400, description=e.message)


def get_token_from_request(app, request):
    if app.config.get('AUTH_TOKEN_HEADER') in request.headers:
        return request.headers.get(app.config.get('AUTH_TOKEN_HEADER'))
    elif request.json \
            and app.config.get('AUTH_TOKEN_KEY') in request.json:
        return request.json.get(app.config.get('AUTH_TOKEN_KEY'))
    else:
        return False
