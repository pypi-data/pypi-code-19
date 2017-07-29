import sys
import os
import nibabel
import warnings
import networkx as nx
import numpy as np

list_modalities = np.array(['t1w', 'rs-fmri', 'dti'])
list_formats = ['bids', 'generic']

def extract(subject_id, out_dir):
    """Run the extraction with default parameters and output features for the given subject."""