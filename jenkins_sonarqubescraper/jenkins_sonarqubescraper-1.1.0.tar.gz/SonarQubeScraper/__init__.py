from sonarhelper import getAnalysis
from csvhelper import insertMetric
import os
def run (ROOT_DIR, PROJECT_NAME) :
    PROJECT_DIR = ROOT_DIR + '/sonar_%s' % PROJECT_NAME

    if not (os.path.isdir(PROJECT_DIR)):
        os.makedirs(PROJECT_DIR)
    analysis = getAnalysis()
    for i in range (0, len(analysis)):
        data = analysis[i]
        metric = data['metric']
        value = data['value']
        insertMetric(PROJECT_DIR, metric, value)
