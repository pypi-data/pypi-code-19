from json import loads
import os

def check_if_expired(response):
    try:
        j_res = loads(response.text)
    except:
        print('Could not authenticate, please refresh your api token')
        return True
    if "status" in j_res and j_res["status"] == 'Token is expired':
        print('Your authentication token is expired request a new one at https://dashboard.numina.co/authenticate and update the cli via numina authenticate <your token>')
        return True
    return False

def get_saved_token():
    try:
        authfile = open(os.path.expanduser('~') + '/.numina-token.txt', 'r')
        token = authfile.read()
        token = token.replace('"', '')
    except IOError:
        print("Please enter an authentication token before using other api features. (numina authenticate <token>)")
        return False
    authfile.close()
    return token
