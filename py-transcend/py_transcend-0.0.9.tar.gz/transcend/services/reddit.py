import pandas as pd
from transcend.services.data_service import DataService

class Reddit(DataService):
    def __init__(self, parent, raw_data, name='reddit'):
        super(self.__class__, self).__init__(parent, raw_data,name)
