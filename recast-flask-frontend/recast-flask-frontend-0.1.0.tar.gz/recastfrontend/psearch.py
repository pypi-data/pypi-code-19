import requests
import json

from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import IndexAlreadyExistsError


def cleanJson(json_data):
    data = json.loads(json_data)
    del data['_updated']
    del data['_created']
    del data['_links']
    del data['_id']
    return data

#es = ElasticSearch('http://localhost:9200')
#ELASTIC_SEARCH_URL = 'http://ylkzd2ykl8:7wsblwtdbe@recast-791793413.us-east-1.bonsai.io'
ELASTIC_SEARCH_URL = '127.0.0.1:9200'
es = ElasticSearch(ELASTIC_SEARCH_URL)

try:
    es.create_index('recast')
except IndexAlreadyExistsError, e:
    pass


r = requests.get(ELASTIC_SEARCH_URL)
i=1
while r.status_code == 200:
    url = 'http://recast-rest-api.herokuapp.com/analysis/{}'.format(i)
    r = requests.get(url)
    if not r.status_code == 200:
        break

    data = cleanJson(r.content)
    es.index('recast', 'analysis', json.dumps(data))
    i = i+1


r = requests.get(ELASTIC_SEARCH_URL)
i=1
while r.status_code == 200:
    url = 'http://recast-rest-api.herokuapp.com/requests/{}'.format(i)
    r = requests.get(url)
    if not r.status_code == 200:
        break
    
    data = cleanJson(r.content)
    es.index('recast', 'requests', json.dumps(data))
    i = i+1

r = requests.get(ELASTIC_SEARCH_URL)
i=1
while r.status_code == 200:
    url = 'http://recast-rest-api.herokuapp.com/users/{}'.format(i)
    r = requests.get(url)
    if not r.status_code == 200:
        break
    
    data = cleanJson(r.content)
    es.index('recast', 'users', json.dumps(data))
    i = i+1
