import json
import urllib2

metric_keys = ['bugs', 'vulnerabilities', 'code_smells', 'duplicated_lines_density']
project_key = 'alaska:android-client-ui:master'
url = 'http://localhost:9000/'
api = 'api/measures/component'

def getAnalysis (PROJECT_KEY):
    parameters = ",".join(metric_keys)
    response = urllib2.urlopen('%s%s?componentKey=%s&metricKeys=%s&format=json' % (url, api, PROJECT_KEY, parameters)).read()
    dict = json.loads(response)
    return dict['component']['measures']