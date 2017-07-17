import clarus.services

def im(output=None, **params):
    return clarus.services.api_request('ETD', 'IM', output=output, **params)

