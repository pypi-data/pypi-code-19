import json
import requests

login = {'bbmdev': 'bbmdev'}
admin = {'admin': 'bbmdev'}
metric_keys = ['bugs', 'vulnerabilities', 'code_smells', 'duplicated_lines_density']
project_key = 'alaska:android-client-ui:master'
url = 'http://localhost:9000/'
api = 'api/measures/component'

def getAnalysis (PROJECT_KEY):
    parameters = ",".join(metric_keys)
    payload = {'componentKey': PROJECT_KEY, 'metricKeys': parameters}
    r = requests.get('%s%s' % (url, api), params=payload, auth=('bbmdev', 'bbmdev'))
    response = r.json()
    stringResponse = json.dumps(response, sort_keys=True, indent=2, separators=(',', ': '))
    dict = json.loads(stringResponse)
    return dict['component']['measures']