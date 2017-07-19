import pandas as pd
from transcend.services.data_service import DataService

class YouTube(DataService):
    def __init__(self, parent, raw_data, name='youtube'):
        super(self.__class__, self).__init__(parent, raw_data, name)
