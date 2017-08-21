""" 
Distance / Similarity Matrix Models

Generalization of the correlation matrix for different metrics / kernels / similarity measures
"""
from core import BasePipeline
from utils import rando_name
from uuid import uuid4
import pandas as pd

class DistanceMatrixPipeline(BasePipeline):
    """ 
    Create a Pipeline to train :class:`.DistanceMatrix` models from input datasets

    Parameters
    ==========

    name : string, optional
        The desired name of the Pipeline.

    K : integer greater than 1, optional, ignored if geodesic == False
        The number of neighbors to use in building the geodesic distance matrix. Geodesic distance is constructed by computing the
        K Nearest Neighbors graph for the input dataset, then constructing all pairwise distances using the geodesic distance, i.e.
        the number of edges in a shortest path between two points on the graph.

    kernel : string, optional
        The distance kernel / metric to use in constructing the distance matrix. Default is euclidean.

    kernel_params : dict, optional
        Any extra parameters specific to the chosen kernel

    geodesic : boolean, optional
        Whether to create the geodesic distance matrix or the brute force pairwise distance matrix. Default is False

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========

    Create a Pipeline for processing multiple datasets into :class:`.DistanceMatrix` models

    >>> io = ConnectIO(api_key)
    >>> matrix_pipe = DistanceMatrixPipeline(kernel = "correlation", client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = matrix_pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())

    """
    def __init__(self, name, kernel = "euclidean", geodesic = False, K = 5, kernel_params = {}, client = None):
        params = {"k": K,
                  "kernel": kernel,
                  "kernel_params": kernel_params,
                  "geodesic": geodesic}
        BasePipeline.__init__(self, name, "dist_matrix", client, params)

    def run(self, dataset, model):
        """ 
        Run the Pipeline and create a new :class:`.DistanceMatrix` model

        Parameters
        ==========

        dataset : pandas.DataFrame
            The dataset to pass into the Pipeline which will train a :class:`.DistanceMatrix` model using the parameters
            defined upon Pipeline creation. Pipelines are reusable sets of instructions to train a machine
            learning model.
        """
        return BasePipeline.run(self, dataset = dataset, model = model)

class DistanceMatrix():
    """ 
    Train / Reload a :class:`.DistanceMatrix` model 

    Parameters
    ==========

    name : string, optional
        The desired name of the model. If None a random name will be generated

    K : integer greater than 1, optional, ignored if geodesic == False
        The number of neighbors to use in building the geodesic distance matrix. Geodesic distance is constructed by computing the
        K Nearest Neighbors graph for the input dataset, then constructing all pairwise distances using the geodesic distance, i.e.
        the number of edges in a shortest path between two points on the graph.

    kernel : string, optional
        The distance kernel / metric to use in constructing the distance matrix. Default is euclidean.

    kernel_params : dict, optional
        Any extra parameters specific to the chosen kernel

    geodesic : boolean, optional
        Whether to create the geodesic distance matrix or the brute force pairwise distance matrix. Default is False

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    pipeline : string, optional
       An extant :class:`DistanceMatrixPipeline` to use for model creation. If None then one will be created

    Returns
    =======
     
    """
    def __init__(self, dataset = None, name = None, pipeline = None, K = 5, kernel = "euclidean", geodesic = False, kernel_params = {}, client = None):
        self.client  = client
        self.type     = "dist_matrix" 
        if dataset is not None:
            self.__full_init__(dataset, name, pipeline, K, kernel, geodesic, kernel_params, client)
        else:
            self.__lazy_init__(name)
    
    # full construction, i.e. start from zero and create it all...
    def __full_init__(self, dataset, name = None, pipeline = None, K = 5, kernel = "euclidean", geodesic = False, kernel_params = {}, client = None):
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.pipeline = pipeline
        self.kernel   = kernel
        self.kernel_params = kernel_params
        self.K        = K
        self.geodesic = geodesic
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = DistanceMatrixPipeline(name = pipeline_name, 
                                                   K    = K, 
                                                   kernel = kernel,
                                                   geodesic = geodesic,
                                                   kernel_params = kernel_params, 
                                                   client = client)
        self.response = self.pipeline.run(self.dataset, self.name)
        try:
            # model will be key if success
            model = self.response['model']
            self.name = model.split("/")[-1]
        except:
            # something went wrong creating the model
            raise StandardError(self.response)

    # lazy loading for already persisted models
    def __lazy_init__(self, model_name):
        self.name     = model_name
        
    def rankDist(self, target, page = 0):
        """ 
        Get the closest datapoints to the given target

        Parameters
        ==========

        page : integer, optional
            The current page. Responses come in chunks of 100. To iterate through the full list increase the page number.

        Returns
        =======

        distances : pandas.DataFrame
            DataFrame with list of datapoints sorted by distance from target point
        """
        extra_params = {"target": target,
                        "page": page}
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "rankDist",
                                          extra_params = extra_params)
        try:
           return pd.DataFrame(response['rankDist'], index = ['distance']).T.sort(columns = "distance")
        except:
           raise StandardError(response)

    def getKeys(self):
        """ 
        Get the names of the datapoints in the model's training dataset

        Returns
        =======

        keys : list
            The names of the datapoints in the model's training dataset
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "getKeys",
                                          extra_params = {})
        try:
           return response['getKeys']
        except:
           raise StandardError(response)

class LazyMatrixPipeline(BasePipeline):
    def __init__(self, name, kernel = "euclidean", kernel_params = {}, client = None):
        params = {"kernel": kernel,
                  "kernel_params": kernel_params}
        BasePipeline.__init__(self, name, "lazy_matrix", client, params)

    def run(self, dataset, model):
        return BasePipeline.run(self, dataset = dataset, model = model)

class LazyMatrix():
    def __init__(self, dataset = None, name = None, pipeline = None, kernel = "euclidean", kernel_params = {}, client = None):
        self.client  = client
        self.type     = "lazy_matrix"
        if dataset is not None:
            self.__full_init__(dataset, name, pipeline, kernel, kernel_params, client)
        else:
            self.__lazy_init__(name)

    # full construction, i.e. start from zero and create it all...
    def __full_init__(self, dataset, name = None, pipeline = None, kernel = "euclidean", kernel_params = {}, client = None):
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.pipeline = pipeline
        self.kernel   = kernel
        self.kernel_params = kernel_params
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = LazyMatrixPipeline(name = pipeline_name,
                                               kernel = kernel,
                                               kernel_params = kernel_params,
                                               client = client)
        self.response = self.pipeline.run(self.dataset, self.name)
        try:
            # model will be key if success
            model = self.response['model']
            self.name = model.split("/")[-1]
        except:
            # something went wrong creating the model
            raise StandardError(self.response)

    # lazy loading for already persisted models
    def __lazy_init__(self, model_name):
        self.name     = model_name

    def rankDist(self, target, page = 0):
        """ 
        Get the closest datapoints to the given target

        Parameters
        ==========

        page : integer, optional
            The current page. Responses come in chunks of 100. To iterate through the full list increase the page number.

        Returns
        =======

        distances : pandas.DataFrame
            DataFrame with list of datapoints sorted by distance from target point
        """
        extra_params = {"target": target,
                        "page": page}
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "rankDist",
                                          extra_params = extra_params)
        try:
           return pd.DataFrame(response['rankDist'], index = ['distance']).T.sort(columns = "distance")
        except:
           raise StandardError(response)

    def getKeys(self):
        """ 
        Get the names of the datapoints in the model's training dataset

        Returns
        =======

        keys : list
            The names of the datapoints in the model's training dataset
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "getKeys",
                                          extra_params = {})
        try:
           return response['getKeys']
        except:
           raise StandardError(response)

