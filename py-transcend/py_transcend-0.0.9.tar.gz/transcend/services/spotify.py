import pandas as pd
import numpy as np
from transcend.services.data_service import DataService

from collections import Counter


class Spotify(DataService):
    '''
        Object to manipulate spotify data
    '''
    def __init__(self, parent, raw_data, name="spotify"):
        super(self.__class__, self).__init__(parent, raw_data, name)

    def clean_saved_tracks(self):
        def merge_two_dicts(z):
            x,y = z
            """Given two dicts, merge them into a new dict as a shallow copy."""
            y['meta'] = x
            return y
        meta_w_track = zip(self.raw_data['savedTracks']['metaData'], self.raw_data['savedTracks']['tracks'])
        saved_tracks = map(merge_two_dicts, meta_w_track)
        keys = ['energy', 'tempo', 'danceability']
        for key in keys:
            vals = map(lambda x : x['meta'][key], saved_tracks)
            if len(vals) > 0:
                mn, mx = min(vals), max(vals) 
                scaled =map(lambda x : 100. * (x - mn) / (mx - mn) if (mx - mn) > 0 else  0., vals)
                
                zp = zip(saved_tracks, scaled)
                def comb(z):
                    x,y = z
                    x['meta'][key + '_scaled'] = y
                _  = map(comb, zp)

        return saved_tracks