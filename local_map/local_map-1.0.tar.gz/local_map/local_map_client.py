import requests
import json

class LocalMapClient():

    def __init__(self, ip_address, port_number):
        self.url = 'http://' + ip_address + ':' + str(port_number) + '/'
        self.ip_address = ip_address
        self.port_number = port_number

    def get(self, key):
        url = self.url + key
        response = requests.get(url)
        if response.status_code == 200:
            j = response.json()['results']
            if len(j) == 0:
                return None
            else:
                return j[0]['value']
        else:
            return None


    def post(self, key, value):
        url = self.url + key
        data = {'value':str(value)}
        headers = {'content-type':'application/json'}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        return response.status_code

    def update(self, key, new_value):
        url = self.url + key
        data = {'value':str(new_value)}
        headers = {'content-type':'application/json'}
        response = requests.put(url, data=json.dumps(data), headers=headers)
        return response.status_code

    def delete(self, key):
        url = self.url + key
        response = requests.delete(url)
        return response.status_code
