'''
Tool for tagging coordinates with the London borough they are within.
Based on London borough geometry of 2017.
'''

import pickle

borough_paths = pickle.load(open("borough_paths.pkl", "rb"))


def get_borough_of_coordinates(lng, lat):
    '''
    Find what London borough a set of coordinates resides within.
    Returns None if coordinates are not within a borough,
    otherwise it returns the name of the borough.
    '''
    for borough in borough_paths:
        if borough_paths[borough].contains_point([lng, lat]):
            return borough
    return None
