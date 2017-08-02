from sonarhelper import getAnalysis
from csvhelper import insertMetric
import os
def run (ROOT_DIR, PROJECT_KEY, PROJECT_NAME) :
    PROJECT_DIR = ROOT_DIR + '/sonar_%s' % PROJECT_NAME

    if not (os.path.isdir(PROJECT_DIR)):
        os.makedirs(PROJECT_DIR)
    analysis = getAnalysis(PROJECT_KEY)
    for i in range (0 , len(analysis)):
            insertMetric(PROJECT_DIR, [analysis[i]['metric'].upper()],[analysis[i]['value']])