from sonarhelper import getAnalysis
from csvhelper import insertMetric
import os
def run (ROOT_DIR, PROJECT_KEY, PROJECT_NAME) :
    PROJECT_DIR = ROOT_DIR + '/sonar_%s' % PROJECT_NAME

    if not (os.path.isdir(PROJECT_DIR)):
        os.makedirs(PROJECT_DIR)
    analysis = getAnalysis(PROJECT_KEY)
    bugIndex = {}
    for i in range (0 , len(analysis)):
        if 'bugs' in analysis[i]['metric'] or 'vulnerabilities' in analysis[i]['metric']:
            bugIndex[analysis[i]['metric']] = i
        else:
            insertMetric(PROJECT_DIR, [analysis[i]['metric'].upper()],[analysis[i]['value']])
    v_index = bugIndex['vulnerabilities']
    b_index = bugIndex['bugs']
    insertMetric(PROJECT_DIR, [analysis[b_index]['metric'].upper(), analysis[v_index]['metric'].upper()],[analysis[b_index]['value'], analysis[v_index]['value']])