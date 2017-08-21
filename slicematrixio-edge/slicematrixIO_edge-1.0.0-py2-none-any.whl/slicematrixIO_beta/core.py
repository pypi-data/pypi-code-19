""" 
Core classes
"""

from connect import ConnectIO, Uploader
from utils import rando_name

class BasePipeline():
    """ 
    The base class for every Pipeline 

    Parameters
    ==========

    name : string
        The desired name of the Pipeline

    type : string
        The type of the Pipeline

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request
    
    """
    def __init__(self, name, type, client = None, params = {}):
        self.name = name
        self.type = type
        self.params = params
        self.client = client
        # create the pipeline on IO cloud
        self.pipeline = self.client.create_pipeline(name = self.name,
                                                    type = self.type,
                                                    params = self.params)
        #print(self.pipeline)
        if "error" in self.pipeline.keys():
            raise StandardError(self.pipeline["error"])
        elif "errorMessage" in self.pipeline.keys():
            raise StandardError(self.pipeline["errorMessage"])        

    #def run(self, dataset, model, extra_params = {}):
    def run(self, model, type = None, dataset = None, matrix_name = None, matrix_type = None, X = None, Y = None, extra_params = {}):
        """ 
        Run the Pipeline and create a new model

        Parameters
        ==========

        dataset : pandas.DataFrame
            The dataset to pass into the Pipeline which will train a model using the parameters
            defined upon Pipeline creation. Pipelines are reusable sets of instructions to train a machine
            learning model.
        """
        # put the dataframe to the cloud
        if dataset is not None:
            dataset_name = rando_name()
            #print("putting dataset")
            #print(dataset_name)
            self.client.put_df(dataset_name, dataset)
        else:
            dataset_name = None
        if X is not None:
            X_name = rando_name()
            self.client.put_df(X_name, X)
        else:
            X_name = None
        if Y is not None:
            Y_name = rando_name()
            self.client.put_df(Y_name, Y)
        else:
            Y_name = None
        response = self.client.run_pipeline(name = self.name,
                                            model = model,
                                            type = self.type,
                                            dataset = dataset_name,
                                            matrix_name = matrix_name,
                                            matrix_type = matrix_type,
                                            X = X_name,
                                            Y = Y_name,
                                            extra_params = extra_params)
        return response

""" 
class BaseModel():
    def __init__(self, name, type, client = None):
        self.name = name
        self.type = type
        self.client = client


"""
