from widget import ModelAPI

def _models_with_cache(request, model_name_slug = None, model_pk = None, model_uuid=None, **kwargs):
    api = ModelAPI(request = request, model_name = model_name_slug, model_pk = model_pk, model_uuid = model_uuid, **kwargs)
    cache = api.api_cache
    
    if request.method == 'GET':
        
        if api.should_use_cache() == True:
            response = cache.get()
        else:
            response = None
            
        if response == None:
            api.run()
            response = api.get_response()
            if api._need_to_cache_results == True:
                cache.set(value = response)
    else:
        api.run()
        response = api.get_response()
        cache.clear_level(level= api._need_to_clear_cache, model_name = cache.model_name, token = cache.token)
    return response

def api_models(request, model_name_slug=None):
    response = _models_with_cache(request, model_name_slug=model_name_slug)
    return response


def api_model(request, model_name_slug=None, model_pk = None, model_uuid=None):
    response = _models_with_cache(model_name_slug = model_name_slug, request = request, model_pk = model_pk, model_uuid = model_uuid)
    return response


def api_admin_models(request, model_name_slug=None):
    response = _models_with_cache(request, model_name_slug=model_name_slug, admin = True)
    return response


def api_admin_model(request, model_name_slug=None, model_pk = None, model_uuid=None):
#     raise LoginError(message = 'woops', notes = 'hey this is a test', http_status = 404, error_code = 4040)
    response = _models_with_cache(admin = True, model_name_slug = model_name_slug, request = request, model_pk = model_pk, model_uuid = model_uuid)
    return response
    