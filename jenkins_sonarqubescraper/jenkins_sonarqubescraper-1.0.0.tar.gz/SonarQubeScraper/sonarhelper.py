import json
import urllib2

metric_keys = ['bugs', 'vulnerabilities', 'duplicated_lines', 'sqale_debt_ratio']
project_key = 'alaska:android-client-ui:master'
url = 'http://localhost:9000/'
api = 'api/measures/component'

def getAnalysis ():
    parameters = ",".join(metric_keys)
    response = urllib2.urlopen('%s%s?componentKey=%s&metricKeys=%s&format=json' % (url, api, project_key, parameters)).read()
    dict = json.loads(response)
    return dict['component']['measures']

getAnalysis()