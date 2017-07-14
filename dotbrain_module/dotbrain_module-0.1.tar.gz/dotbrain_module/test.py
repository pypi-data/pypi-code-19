def sendAnswerd(api_key=None,api_key_secret=None,token=None,value=None,base=None,numeric=None,user=None,weigth_key=None, printInfo=True):
    import requests

    url = 'http://127.0.0.1:8000/api/save/answer/'

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
    data = {
        'validate': True,
        'text': r.text,
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