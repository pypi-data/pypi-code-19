import pandas as pd
from transcend.services.data_service import DataService

class UnderArmour(DataService):
    def __init__(self, parent, raw_data, name='underarmour'):
        super(self.__class__, self).__init__(parent, raw_data, name)
