from core import BasePipeline
from utils import rando_name
from uuid import uuid4
import pandas as pd

#################################################################################################################################################################
# new types, don't need to create the pipeline first, it already exists

class PortfolioStressTest():
    def __init__(self, dataset = None, name = None, target_col = None, client = None):
        self.client  = client
        self.type     = "stress_test"
        if dataset is not None:
            self.__full_init__(dataset, name, None, target_col, client)
        else:
            self.__lazy_init__(name)

    def __full_init__(self, dataset, name = None, pipeline = None, target_col = None, client = None):
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.target_col = target_col
        # YOOOOOOOOOOOOOOOOUUUU ARE HERE!!!!!!!!!!!!!!!!!!!!!!
        # need to upload the dataset
        dataset_name = rando_name()
        self.client.put_df(dataset_name, dataset)
        self.response = self.client.run_pipeline("",  self.name, type = self.type, dataset = dataset_name, extra_params = {"target_col": self.target_col})
        try:
            # model will be key if success
            model = self.response['model']
            self.name = model
        except:
            # something went wrong creating the model
            raise StandardError(self.response)

    # lazy loading for already persisted models
    def __lazy_init__(self, model_name):
        self.name     = model_name

    # update the model with new data and return updated state info
    def simulate(self, target_rtn, N = 1):
        extra_params = {"N": N, "target_rtn": target_rtn}
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "simulate",
                                          extra_params = extra_params)
        try:
           return response['simulate']
        except:
           raise StandardError(response)