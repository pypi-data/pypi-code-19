import os
import json

import requests
from urllib.parse import urlencode


class Stashy:
    base_url = 'https://stashy.io/api'
    """
    A session stores configuration state and allows you to create service
    clients and resources.
    :type api_key: string
    :param api_key: Stashy.io API key
    """

    def __init__(self, api_key=None):
        self.headers = {'content-type': 'application/json', 'Authorization': 'Bearer ' + api_key}

    def get(self, endpoint, filter_by=None, sort_by=None, order_by=None):
        if isinstance(endpoint, str) is False:
            raise Exception("Endpoint is not a valid string")
        query_params = ""
        if filter_by is not None:
            query_params = '?' + urlencode(filter_by)
        if sort_by is not None:
            query_params = query_params + '&sort=' + sort_by
        if order_by is not None:
            if order_by.lower() == 'asc' or order_by == 1 or order_by.lower() == 'desc' or order_by == -1:
                query_params = query_params + '&order=' + order_by

        url = self.base_url + '/d/' + endpoint + '/docs' + query_params
        r = requests.get(url, headers=self.headers)

        if r.status_code == 200:
            json_data = r.json()
            return {
                "url": url,
                "count": len(json_data),
                "data": json_data
            }
        else:
            return {"status": r.status_code, "message": r.reason}

    def save(self, endpoint, data=None, explode=None):
        if isinstance(endpoint, str) is False:
            raise Exception("Endpoint is not a valid string")
        query_params = ""
        if explode is not None:
            query_params = '?st::explode=' + explode
        url = self.base_url + '/d/' + endpoint + '/docs' + query_params
        r = requests.post(url, headers=self.headers, data=json.dumps(data))
        json_data = r.json()
        if r.status_code == 200:
            return {
                "url": url,
                "count": len(json_data),
                "data": json_data
            }
        else:
            return json_data

    def delete_all(self, endpoint):
        if isinstance(endpoint, str) is False:
            raise Exception("Endpoint is not a valid string")
        url = self.base_url + '/d/' + endpoint + '/docs/delete_all'
        r = requests.delete(url, headers=self.headers)
        return r.json()

    def delete(self, endpoint, filter_by=None):
        print(filter_by['st::filter'])
        if isinstance(endpoint, str) is False:
            raise Exception("Endpoint is not a valid string")
        query_params = ""
        if filter_by is not None:
            if 'st::filter' not in filter_by:
                query_params = '?' + urlencode(filter_by)
            else:
                query_params = '?st::filter=' + json.dumps(filter_by['st::filter']).replace(" ", "")
        url = self.base_url + '/d/' + endpoint + '/docs/delete' + query_params
        print(url)
        r = requests.delete(url, headers=self.headers)
        return r.text
