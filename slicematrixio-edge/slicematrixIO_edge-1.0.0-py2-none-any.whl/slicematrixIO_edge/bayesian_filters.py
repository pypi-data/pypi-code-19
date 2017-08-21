from core import BasePipeline
from utils import rando_name
from uuid import uuid4
import pandas as pd

#################################################################################################################################################################
class KalmanOLSPipeline(BasePipeline):
    """ 
    Create a Pipeline for training :class:`.KalmanOLS` models from input datasets

    Parameters
    ==========
    name : string
        The desired name of the Pipeline

    init_alpha : float, optional
        Initial value for alpha in OLS model (ignored if optimizations are enabled)

    init_beta : float, optional
        Initial value for beta in OLS model (ignored if optimizations are enabled)

    trans_cov : array-like, optional
        Transition covariance, shape = (2, 2)

    init_cov : array-like, optional
        Initial covariance, shape = (2, 2)

    optimizations : list, optional
        List of optimizations. Can include multiple optimizations. Default includes all:

        - 'transition_covariance'
        - 'observation_covariance'
        - 'initial_state_mean'
        - 'initial_state_covariance'

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========

    Create a KalmanOLSPipeline for processing multiple datasets

    >>> io = ConnectIO(api_key)
    >>> pipe = KalmanOLSPipeline(client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())

    """
    def __init__(self, name, init_alpha = None, init_beta = None, trans_cov = None, obs_cov = None, init_cov = None, optimizations = [], client = None):
        params = {"init_alpha": init_alpha,
                  "init_beta": init_beta,
                  "trans_cov": trans_cov,
                  "obs_cov": obs_cov,
                  "init_cov": init_cov,
                  "optimizations": optimizations}
        BasePipeline.__init__(self, name, "kalman_ols", client, params)

    def run(self, dataset, model):
        """ 
        Run the Pipeline and create a new :class:`.KalmanOLS` model

        Parameters
        ==========

        dataset : pandas.DataFrame
            The dataset to pass into the Pipeline which will train a KernelPCA model using the parameters
            defined upon Pipeline creation. Pipelines are reusable sets of instructions to train a machine
            learning model.

        Returns
        =======

        response : dict
            success or failure response to model creation request
            
        """
        return BasePipeline.run(self, dataset = dataset, model = model)

class KalmanOLS():
    """ 
    Train / Reload a Kalman Filter model for online estimation of the parameters of Ordinary Least Squares (KalmanOLS)

    Parameters
    ==========

    dataset: pandas.DataFrame
        Input DataFrame. shape = (nrows, 2) where the first column is Y and the second is X in OLS model

    init_alpha : float, optional
        Initial value for alpha in OLS model (ignored if optimizations are enabled)

    init_beta : float, optional
        Initial value for beta in OLS model (ignored if optimizations are enabled)

    trans_cov : array-like, optional
        Transition covariance, shape = (2, 2)

    init_cov : array-like, optional
        Initial covariance, shape = (2, 2)

    optimizations : list, optional
        List of optimizations. Can include multiple optimizations. Default includes all:

        - 'transition_covariance'
        - 'observation_covariance'
        - 'initial_state_mean'
        - 'initial_state_covariance'

    name : string, optional
        The desired name of the model. If None then a random name will be generated

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    pipeline : BasePipeline, optional
        Pipeline to use. Defaults to None. If None then a pipeline will be created for use in creating the model

    Returns
    =======

    model : :class`.KalmanOLS`
        Trained Kalman Filter model

    Examples
    ========

    Create a KalmanOLS model for a given dataset

    >>> sm = SliceMatrix(api_key)
    >>> kf = sm.KalmanOLS(dataset = dataframe)

    Get the current internal state of the model (i.e. current alpha and beta and covariance)

    >>> kf.getState()

    Update the model will new information, and get updated state

    >>> kf.update(X = 128.17, Y = 45.85)

    """

    def __init__(self, dataset = None, name = None, pipeline = None, init_alpha = None, init_beta = None, trans_cov = None, obs_cov = None, init_cov = None, optimizations = [], client = None):
        self.client  = client
        self.type     = "kalman_ols"
        if dataset is not None:
            self.__full_init__(dataset, name, pipeline, init_alpha, init_beta, trans_cov, obs_cov, init_cov, optimizations, client)
        else:
            self.__lazy_init__(name)

    def __full_init__(self, dataset, name = None, pipeline = None, init_alpha = None, init_beta = None, trans_cov = None, obs_cov = None, init_cov = None, optimizations = [], client = None):
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.pipeline = pipeline
        self.init_alpha = init_alpha
        self.init_beta = init_beta
        self.trans_cov = trans_cov
        self.obs_cov   = obs_cov
        self.init_cov  = init_cov
        self.optimizations = optimizations
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = KalmanOLSPipeline(pipeline_name, init_alpha, init_beta, trans_cov, obs_cov, init_cov, optimizations, client)
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

    def getState(self):
        """ 
        Get the current internal state of the Kalman Filter OLS model

        Returns
        =======

        state : dict
            Dictionary with the current state of model i.e. 
            - means (Beta and Alpha, respectively)
            - covariance 

        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "getState",
                                          extra_params = {})
        try:
           return response['getState']
        except:
           raise StandardError(response)

    def getTrainingData(self):
        """ 
        Get the historical state of the model over time

        Returns
        =======

        history : dict
            Historical state of both mean and covariance of the model over time.
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "getTrainingData",
                                          extra_params = {})
        try:
           return response['getTrainingData']
        except:
           raise StandardError(response)

    # update the model with new data and return updated state info
    def update(self, X, Y):
        """ 
        Step the model through a new learning iteration with new datapoints for input (X) and output (Y)

        This will permanently change the state of the model as it adjusts to new information. 

        In a distributed setting, updates to the same :class:`KalmanOLS` model are not guaranteed to be atomic 

        Parameters
        ==========

        X : float
            The newly observed value for the input of the OLS model (X)

        Y : float
            The newly observed value for the output of the OLS model (Y)

        Returns
        =======

        state : dict
            Dictionary with the current state of model i.e.
            - means (Beta and Alpha, respectively)
            - covariance

        """
        extra_params = {"Y": Y, "X": X}
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "update",
                                          extra_params = extra_params)
        try:
           return response['update']
        except:
           raise StandardError(response)
