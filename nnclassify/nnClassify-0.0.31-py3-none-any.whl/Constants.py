# This file as all the constants for the project
from os.path import expanduser
import os

# Paths
BASE_DIR = expanduser(os.path.join('~','nnClassify','data'))
MODELS_DIR = os.path.join(BASE_DIR, 'Models')
INCEPTION_DIR = os.path.join(BASE_DIR, 'inception')
TRAIN_DIR = os.path.join(BASE_DIR, 'Train')
PRED_DIR = os.path.join(BASE_DIR, 'Predictions')
TEST_WELLS_DIR = os.path.join(BASE_DIR, 'Test_Wells')
TEST_INDL_DIR = os.path.join(BASE_DIR, 'Test_Individual')

PICKLES = "Pickles"
RESULTS_DIR = "Results"
TRANSFER = "Transfer_Values"

# Categories
ABNORMAL = "Abnormal"
NORMAL = "Normal"
WEIRD = "Weird"
NOT_SURE = "Not_Sure"

# Files
RESULTS = "results.txt"
