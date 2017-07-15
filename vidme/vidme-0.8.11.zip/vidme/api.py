
from requests import get, post, delete
import socket
import base64

API_URL = "https://api.vid.me"

def do_request(uri, session=None, method='POST', extraheaders=None, **kwargs):    
    headers = {
        'User-Agent': "KingFredrickVI API Interface Python Bot - https://github.com/KingFredrickVI/VidMeAPI",
    }

    if extraheaders is not None:
        headers.update(extraheaders)
    if session is not None:
        if session.get_token():
            headers['AccessToken'] = session.get_token()

        if session.get_oauth():
            headers['Authorization'] = session.get_oauth()

    func = post

    if method == 'POST':
        func = post
    elif method == 'GET':
        func = get
    elif method == 'DELETE':
        func = delete
 
    result = func(API_URL + uri, headers=headers, **kwargs)

    # print "[%%]", result.url

    result_json = result.json()

    if result.status_code >= 400:
        print "uri:", uri
        print "headers:", extraheaders
        print "result text:", result.text
        print "result code:", result.status_code
        if result_json and 'code' in result_json and result_json['code'] != "internal_server_error":
            print "request failed!", result_json['code'], result_json['error']
        else:
            print "request failed!!!", result_json
        return False
 
    if result_json is None or not 'status' in result_json or result_json['status'] is False:
        print 'request failed!!', result_json['code'], result_json['error']
        return False

    return result_json

def request(*args, **kwargs):
    return do_request(*args, **kwargs)
