def sendAnswerd(api_key=None,api_key_secret=None,token=None,value=None,base=None,numeric=None,user=None,weigth_key=None, printInfo=True):
    import requests

    url = 'http://dev.dotbrain.co/api/save/answer/'

    data = {
        'api_key': api_key,
        'api_key_secret': api_key_secret,
        'token': token,
        'value': value,
        'base': base,
        'numeric': numeric,
        'user': user,
        'weigth_key': weigth_key,
    }

    r = requests.post(url=url, params=data)
    import json
    data = {
        'validate': True,
        'text': json.loads(r.text),
        'status_code': r.status_code
    }
    if r.status_code != 200:
        data['validate'] = False
        if printInfo:
            print('Error: %s' % str(r.text))
        return data
    else:
        if printInfo:
            print('All ok')
        return data

def getServiceBasicInfo(api_key=None,api_key_secret=None,token=None, printInfo=False):
    import requests

    url = 'http://dev.dotbrain.co/api/get/service/info/basic/'

    data = {
        'api_key': api_key,
        'api_key_secret': api_key_secret,
        'token': token,
    }

    r = requests.get(url=url, params=data)
    import json
    data = {
        'validate': True,
        'text': json.loads(r.text),
        'status_code': r.status_code
    }
    if r.status_code != 200:
        data['validate'] = False
        if printInfo:
            print('Error: %s' % str(r.text))
        return data
    else:
        if printInfo:
            print('All ok')
        return data

def setQuestionKey(api_key=None,api_key_secret=None,token=None, key=None, weigth=None, printInfo=False):
    import requests

    url = 'http://dev.dotbrain.co/api/set/weigth/key/'

    data = {
        'api_key': api_key,
        'api_key_secret': api_key_secret,
        'token_service': token,
        'key': key,
        'weigth': weigth,
    }

    r = requests.post(url=url, params=data)
    data = {
        'validate': True,
        'text': r.text,
        'status_code': r.status_code
    }
    if r.status_code != 200:
        if printInfo:
            print('Error: %s' % str(r.text))
        return data
    else:
        if printInfo:
            print('All ok')
        return data

def create_service(api_key=None,api_key_secret=None,name=None, email=None, normal_mean=True, printInfo=False):
    import requests

    url = 'http://dev.dotbrain.co/api/create/service/'

    if normal_mean:
        normal_mean = '1'
    else:
        normal_mean = '0'

    data = {
        'api_key': api_key,
        'api_key_secret': api_key_secret,
        'name': name,
        'email': email,
        'normal_mean': normal_mean,
    }

    r = requests.post(url=url, params=data)
    import json
    data = {
        'validate': True,
        'text': json.loads(r.text),
        'status_code': r.status_code
    }
    if r.status_code != 200:
        if printInfo:
            print('Error: %s' % str(r.text))
        return data
    else:
        if printInfo:
            print('All ok')
        return data

def get_info_service(api_key=None,api_key_secret=None,token=None, ordering_by=None, get_answers='n', printInfo=False):
    import requests

    url = 'http://dev.dotbrain.co/api/get/service/info/'

    data = {
        'api_key': api_key,
        'api_key_secret': api_key_secret,
        'token': token,
        'ordering_by': 'blank',
        'get_answers': get_answers,
    }

    r = requests.get(url=url, params=data)
    import json
    data = {
        'validate': True,
        'text': json.loads(r.text),
        'status_code': r.status_code
    }
    if r.status_code != 200:
        if printInfo:
            print('Error: %s' % str(r.text))
        return data
    else:
        if printInfo:
            print('All ok')
        return data