import pandas as pd
import numpy as np

from IPython.display import display, HTML, Markdown

class DataService(object):
    def __init__(self, parent, raw_data, name):
        self.parent = parent
        self.name = name
        self.raw_data = raw_data
    
    def __str__(self):
        return str(self.data)
    



