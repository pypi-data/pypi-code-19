import pandas as pd
from data_service import DataService

class RescueTime(DataService):
    def __init__(self, parent, raw_data, name="rescuetime"):
        super(self.__class__, self).__init__(parent, raw_data, name)
