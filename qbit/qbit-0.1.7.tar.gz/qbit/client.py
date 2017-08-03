import grpc
import json
import time
import requests
import qbit_pb2

from google.protobuf.json_format import MessageToDict


def create_get_auth(access_token):

    def get_auth_token(context, callback):
        callback([('authorization', access_token)], None)

    return get_auth_token

# Client class takes care of authentication process in order to use our services
#
# Example -
# from qbit import client
# qbit_client = client('./qbit/license.json')
# qbit_client.stub has all the grpc functions 1qbit has
class grpc_channel(object):

    def __init__(self,
                 license=None,
                 client_id=None,
                 client_secret=None,
                 auth_url=None,
                 host='grpc.1qb.it'):
        auth_creds_given = False

        if license:
            auth_creds_given = True
            with open(license) as data_file:
                data = json.load(data_file)
            client_id = data["client_id"]
            client_secret = data["client_secret"]
        elif (client_id and client_secret):
            auth_creds_given = True
            client_id = client_id
            client_secret = client_secret

        root_certs = str(requests.get('http://api.1qb.it/ca.pem').text)
        channel_creds = grpc.ssl_channel_credentials(
            root_certificates=root_certs)

        if auth_creds_given:
            auth_url = auth_url if auth_url else "https://1qbit.auth0.com/oauth/token"

            req_dict = {
                "client_id": client_id,
                "client_secret": client_secret,
                "grant_type": "client_credentials",
                "audience": "http://api.1qb.it"
            }
            try:
                response = requests.post(auth_url, json=req_dict).json()
            except Exception as e:
                raise Exception("Request has Failed: ", e.message)

            if response.has_key("error"):
                if response.has_key("error_description"):
                    raise Exception(response["error"], ": ",
                                    response["error_description"])
                raise Exception(response)
            elif response.has_key("access_token"):
                token = response["access_token"]

            auth_creds = grpc.metadata_call_credentials(create_get_auth(token))
            channel_creds = grpc.composite_channel_credentials(
                channel_creds, auth_creds)
        self._channel = grpc.secure_channel(host, channel_creds)

def client(license=None,
            client_id=None,
            client_secret=None,
            auth_url=None,
            host='grpc.1qb.it'):
    c = grpc_channel(license, client_id, client_secret, auth_url, host)
    return qbit_pb2.QbitStub(c._channel)
