import csv
import os

def insertMetric (ROOT_DIR, metric, metric_data):
    METRIC_PATH = ROOT_DIR + '/metric_%s.csv' % metric[0].lower()
    METRIC_HEADERS = metric
    METRIC_DATA = metric_data
    if not (os.path.isfile(METRIC_PATH)):
        with open(METRIC_PATH, 'w') as test_file:
            wr = csv.writer(test_file, quoting=csv.QUOTE_ALL)
            wr.writerow(METRIC_HEADERS)
    with open(METRIC_PATH, 'a') as test_file:
        wr = csv.writer(test_file, quoting=csv.QUOTE_ALL)
        wr.writerow(METRIC_DATA)