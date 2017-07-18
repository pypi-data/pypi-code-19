import pandas as pd
from data_service import DataService

class LinkedIn(DataService):
    def __init__(self, parent, raw_data, name='linkedin'):
        super(self.__class__, self).__init__(parent, raw_data, name)
        