import clarus.services

def ladder(output=None, **params):
    return clarus.services.api_request('Upload', 'Ladder', output=output, **params)

def market(output=None, **params):
    return clarus.services.api_request('Upload', 'Market', output=output, **params)

def portfolio(output=None, **params):
    return clarus.services.api_request('Upload', 'Portfolio', output=output, **params)

def scenario(output=None, **params):
    return clarus.services.api_request('Upload', 'Scenario', output=output, **params)

def trades(output=None, **params):
    return clarus.services.api_request('Upload', 'Trades', output=output, **params)

