""" 
Regressors are machine learning models which learn a function between an input (X) and an output (Y).

In particular, SliceMatrix-IO offers a number of what are known as "multi-output" regression models.

This is a special type of regression which can have an output with a dimension greater than 1, useful for:

- Prediction
- Out of Sample Manifold Learning
- As a step within a classification workflow

"""
from core import BasePipeline
from utils import rando_name, r_squared
from uuid import uuid4
import pandas as pd
import numpy as np

# Random Forest Regressor pipeline #############################################################################################################################################3
class RFRegressorPipeline(BasePipeline):
    """ 
    Random Forest Regression.

    Create a Pipeline for training :class:`RFRegressor` models.

    Parameters
    ==========

    name : string
        The desired name of the Pipeline.

    n_trees : integer, greater than 0
        The number of trees to use in the regression forest

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========

    Create a Pipeline for training multiple :class:`.RFRegressor` models

    >>> io = ConnectIO(api_key)
    >>> pipe = RFRegressorPipeline(n_trees = 100, client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())

    """
    def __init__(self, name, n_trees = 8, client = None):
        params = {"n_trees": n_trees,}
        BasePipeline.__init__(self, name, "raw_rfr", client, params)

    def run(self, X, Y, model):
        """ 
        Run the Pipeline and create a new :class:`RFRegressor` model

        Parameters
        ==========

        dataset : pandas.DataFrame
            The dataset to pass into the Pipeline which will train a :class:`RFRegressor` model using the
            parameters defined upon Pipeline creation. Pipelines are reusable sets of instructions to train
            a machine learning model.

        Returns
        =======

        response : dict
            success or failure response to model creation request
        """
        return BasePipeline.run(self, X = X, Y = Y, model = model)

# Random Forest Regressor model; if pipeline == None then create a pipeline for use with this model
class RFRegressor():
    """ 
    Train / Reload a :class:`.RFRegressor` model for multi-output regression

    A Random Forest Regressor finds a function which maps the input space (X) to the lower dimension output space (Y) using decision trees

    Parameters
    ==========

    X : pandas.DataFrame
        Input DataFrame. shape = (n_rows, input_features) where each row is a data point and the columns are numeric features

    Y : pandas.DataFrame
        Output DataFrame. shape = (n_rows, output_features) where output_features < input_features and each row is a data point
        and the columns are numeric features

    n_trees : integer greater than 1, optional
        The number of trees to use in construction of the Random Forest model. Default is 8 trees

    name : string, optional
        The desired name of the model. If None then a random name will be generated

    pipeline : string, optional
        An extant Pipeline to use for model creation. If None then one will be created

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======
    model : :class:`.RFRegressor`
        Trained Random Forest Regressor model

    Examples
    ========

    Train a Random Forest Regressor model

    >>> sm = SliceMatrix(api_key)
    >>> rfr = sm.RFRegressor(dataset = dataset, n_trees = 50)

    Make a prediction

    >>> rfr.predict([...])

    """
    def __init__(self, X = None, Y = None, name = None, pipeline = None, n_trees = 8, client = None):
        self.client  = client
        self.type     = "raw_rfr"
        if X is not None and Y is not None:
            self.__full_init__(X, Y, name, pipeline, n_trees, client)
        else:
            self.__lazy_init__(name)

    def __full_init__(self, X, Y, name = None, pipeline = None, n_trees = 8, client = None):
        self.n_trees = n_trees 
        if name == None:
            name = rando_name()
        # else:
        #    todo: add feature to instantiate RFRegressor just from name
        #    i.e. an already created model
        self.name     = name
        self.X        = X
        self.Y        = Y
        self.pipeline = pipeline
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = RFRegressorPipeline(pipeline_name, n_trees, client)
        self.response = self.pipeline.run(X = self.X, Y = self.Y, model = self.name)
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
        
    def predict(self, point):
        """ 
        Make a prediction using the given input features.

        Also used for out of sample manifold learning.

        I.e.

        1) Perform manifold learning embedding of input data (high dimension, H) to low dimension (D, D < H), however
            - Many manifold learnin algorithms don't have straightforward out of sample generalizatons...
        2) Learn the "interpolation" function between high dim space and low dim space with a multi-output regression
            - Regress high dim (H) data points against the embedding (D) data points to learn the manifold embedding
        3) When presented with a new data point, an H dimension vector, or tensor or whatever term is fashionable,
           and "embed" it using the multi-output regression to output a D dimension vector

        Parameters
        ==========

        point : list
            List of points to use as inputs to a prediction

        Result
        ======

        prediction : list
            A list of output predictions
        """
        extra_params = {"features": point.values.tolist()}
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "predict",
                                          extra_params = extra_params)
        try:
           return pd.DataFrame(response['predict'])
        except:
           raise StandardError(response)

    def score(self):
        """ 
        Get the R^2 of the training dataset / predictions

        Returns
        =======

        r2 : float
            The R^2 of the training dataset
        """
        Y_hat = self.predict(self.X)
        return r_squared(Y_hat, self.Y)

# K Nearest Neighbors regressor pipeline
class KNNRegressorPipeline(BasePipeline):
    """ 
    K Nearest Neighbors Regression.

    Create a Pipeline for training :class:`KNNRegressor` models.

    Parameters
    ==========

    name : string
        The desired name of the Pipeline.

    K : integer, optional
        The desired K in the Nearest Neighbor classifier model

    kernel : string [ 'euclidean' | 'minkowski' | 'hammond' | 'etc...'], optional
        The desired kernel for defining distance in our classifier. Default is 'euclidean'

    algo : string ['auto' | 'ball' | 'kd_tree' | 'brute'], optional
        The algorithm to use in determining Nearest Neighbors. Default is 'auto'

    weights : string ['uniform' | 'weighted'], optional
        Should voting be uniform (i.e. independent of distance) or weighted by distance (i.e. closer neighbor's have higher weighted predictions)

    kernel_params : dict, optional
        Any parameters specific to the chosen kernel

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========

    Create a Pipeline for training multiple :class:`.KNNRegressor` models

    >>> io = ConnectIO(api_key)
    >>> pipe = KNNRegressorPipeline(K = 5, client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())


    """
    def __init__(self, name, K = 5, kernel = "euclidean", algo = "auto", weights = "uniform", kernel_params = {}, client = None):
        params = {"k": K,
                  "kernel": kernel,
                  "algo": algo,
                  "weights": weights,
                  "kernel_params": kernel_params}
        BasePipeline.__init__(self, name, "raw_knn_regressor", client, params)

    def run(self, X, Y, model):
        """ 
        Run the Pipeline and create a new :class:`KNNRegressor` model

        Parameters
        ==========

        dataset : pandas.DataFrame
            The dataset to pass into the Pipeline which will train a :class:`KNNRegressor` model using the
            parameters defined upon Pipeline creation. Pipelines are reusable sets of instructions to train
            a machine learning model.

        Returns
        =======

        response : dict
            success or failure response to model creation request
        """
        return BasePipeline.run(self, X = X, Y = Y, model = model)

class KNNRegressor():
    """ 
    Train / Reload a :class:`.KNNRegressor` model for multi-output regression

    Parameters
    ==========

    X : pandas.DataFrame
        Input DataFrame. shape = (n_rows, input_features) where each row is a data point and the columns are numeric features

    Y : pandas.DataFrame
        Output DataFrame. shape = (n_rows, output_features) where output_features < input_features and each row is a data point
        and the columns are numeric features

    K : integer, optional
        The desired K in the Nearest Neighbor classifier model

    kernel : string [ 'euclidean' | 'minkowski' | 'hammond' | 'etc...'], optional
        The desired kernel for defining distance in our classifier. Default is 'euclidean'

    algo : string ['auto' | 'ball' | 'kd_tree' | 'brute'], optional
        The algorithm to use in determining Nearest Neighbors. Default is 'auto'

    weights : string ['uniform' | 'weighted'], optional
        Should voting be uniform (i.e. independent of distance) or weighted by distance (i.e. closer neighbor's have higher weighted predictions)

    kernel_params : dict, optional
        Any parameters specific to the chosen kernel

    name : string, optional
        The desired name of the model. If None then a random name will be generated

    pipeline : string, optional
        An extant Pipeline to use for model creation. If None then one will be created

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======
    model : :class:`.RFRegressor`
        Trained Random Forest Regressor model

    Examples
    ========

    Train a K Nearest Neighbors Regressor model

    >>> sm = SliceMatrix(api_key)
    >>> knn = sm.KNNRegressor(dataset = dataset, K = 3)

    Make a prediction

    >>> knn.predict([...])

    """
    def __init__(self, X = None, Y = None, name = None, pipeline = None, K = 5, kernel = "euclidean", algo = "auto", weights = "uniform", kernel_params = {}, client = None):
        self.client  = client
        self.type     = "raw_knn_regressor"
        if X is not None and Y is not None:
            self.__full_init__(X, Y, name, pipeline, K, kernel, algo, weights, kernel_params, client)
        else:
            self.__lazy_init__(name)

    def __full_init__(self, X, Y, name = None, pipeline = None, K = 5, kernel = "euclidean", algo = "auto", weights = "uniform", kernel_params = {}, client = None):
        self.X       = X
        self.Y       = Y
        if name == None:
            name = rando_name()
        self.name     = name
        self.pipeline = pipeline
        self.K        = K
        self.kernel   = kernel
        self.kernel_params = kernel_params
        self.algo     = algo
        self.weights  = weights
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = KNNRegressorPipeline(pipeline_name, K, kernel, algo, weights, kernel_params, client)
        self.response = self.pipeline.run(X = self.X, Y = self.Y, model = self.name)
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

    def predict(self, point):
        """ 
        Make a prediction using the given input features.

        Also used for out of sample manifold learning.

        I.e.

        1) Perform manifold learning embedding of input data (high dimension, H) to low dimension (D, D < H), however
            - Many manifold learnin algorithms don't have straightforward out of sample generalizatons...
        2) Learn the "interpolation" function between high dim space and low dim space with a multi-output regression
            - Regress high dim (H) data points against the embedding (D) data points to learn the manifold embedding
        3) When presented with a new data point, an H dimension vector, or tensor or whatever term is fashionable,
           and "embed" it using the multi-output regression to output a D dimension vector

        Parameters
        ==========

        point : list
            List of points to use as inputs to a prediction

        Result
        ======

        prediction : list
            A list of output predictions
        """
        extra_params = {"features": point.values.tolist()}
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "predict",
                                          extra_params = extra_params)
        try:
           return pd.DataFrame(response['predict'])
        except:
           raise StandardError(response)

    def score(self):
        """ 
        Get the R^2 of the training dataset / predictions

        Returns
        =======

        r2 : float
            The R^2 of the training dataset
        """
        Y_hat = self.predict(self.X)
        return r_squared(Y_hat, self.Y)


#################################################################################################################################################################################
class KernelRidgeRegressorPipeline(BasePipeline):
    """ 
    Kernel Ridge Regression.

    Create a Pipeline for training :class:`KernelRidgeRegressor` models.

    Parameters
    ==========

    name : string
        The desired name of the Pipeline.

    alpha : float, optional
        Kernel Ridge Regressor model alpha value. Default 1.0

    kernel : string ['linear', 'rbf', 'poly']
        Kernel to use in regression. Linear is default. For nonlinear datasets, consider rbf or poly

        'linear' : linear kernel

        'rbf' : radial basis function kernel

        'poly' : polynomial kernel

    kernel_params : dict
        Kernel specific parameters

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======
    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========

    Create a Pipeline for training multiple :class:`.KernelRidgeRegressor` models

    >>> io = ConnectIO(api_key)
    >>> pipe = KernelRidgeRegressorPipeline(K = 5, client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())

    """
    def __init__(self, name, kernel = "linear", alpha = 1.0, kernel_params = {}, client = None):
        params = {"kernel": kernel,
                  "alpha": alpha,
                  "kernel_params": kernel_params}
        BasePipeline.__init__(self, name, "raw_krr", client, params)

    def run(self, X, Y, model):
        """ 
        Run the Pipeline and create a new :class:`KernelRidgeRegressor` model

        Parameters
        ==========

        dataset : pandas.DataFrame
            The dataset to pass into the Pipeline which will train a :class:`KernelRidgeRegressor` model using the
            parameters defined upon Pipeline creation. Pipelines are reusable sets of instructions to train
            a machine learning model.

        Returns
        =======

        response : dict
            success or failure response to model creation request
        """
        return BasePipeline.run(self, X = X, Y = Y, model = model)

class KernelRidgeRegressor():
    """ 
    Train / Reload a :class:`.KernelRidgeRegressor` model for multi-output regression

    Parameters
    ==========

    X : pandas.DataFrame
        Input DataFrame. shape = (n_rows, input_features) where each row is a data point and the columns are numeric features

    Y : pandas.DataFrame
        Output DataFrame. shape = (n_rows, output_features) where output_features < input_features and each row is a data point
        and the columns are numeric features

    K : integer, optional
        The desired K in the Nearest Neighbor classifier model

    kernel : string [ 'euclidean' | 'minkowski' | 'hammond' | 'etc...'], optional
        The desired kernel for defining distance in our classifier. Default is 'euclidean'

    algo : string ['auto' | 'ball' | 'kd_tree' | 'brute'], optional
        The algorithm to use in determining Nearest Neighbors. Default is 'auto'

    weights : string ['uniform' | 'weighted'], optional
        Should voting be uniform (i.e. independent of distance) or weighted by distance (i.e. closer neighbor's have higher weighted predictions)

    kernel_params : dict, optional
        Any parameters specific to the chosen kernel

    name : string, optional
        The desired name of the model. If None then a random name will be generated

    pipeline : string, optional
        An extant Pipeline to use for model creation. If None then one will be created

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======
    model : :class:`.RFRegressor`
        Trained Random Forest Regressor model

    Examples
    ========

    Train a Kernel Ridge Regressor model

    >>> sm = SliceMatrix(api_key)
    >>> krr = sm.KNNRegressor(dataset = dataset, kernel = "rbf")

    Make a prediction

    >>> krr.predict([...])


    """
    def __init__(self, X = None, Y = None, name = None, pipeline = None, kernel = "linear", alpha = 1.0, kernel_params = {}, client = None):
        self.client  = client
        self.type     = "raw_krr"
        if X is not None and Y is not None:
            self.__full_init__(X, Y, name, pipeline, kernel, alpha, kernel_params, client)
        else:
            self.__lazy_init__(name)        

    def __full_init__(self, X, Y, name = None, pipeline = None, kernel = "linear", alpha = 1.0, kernel_params = {}, client = None):
        self.X       = X
        self.Y       = Y
        if name == None:
            name = rando_name()
        self.name     = name
        self.pipeline = pipeline
        self.kernel   = kernel
        self.alpha    = alpha        
        self.kernel_params = kernel_params
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = KernelRidgeRegressorPipeline(pipeline_name, kernel, alpha, kernel_params, client)
        self.response = self.pipeline.run(X = self.X, Y = self.Y, model = self.name)
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

    def predict(self, point):
        """ 
        Make a prediction using the given input features. 

        Also used for out of sample manifold learning.

        I.e. 

        1) Perform manifold learning embedding of input data (high dimension, H) to low dimension (D, D < H), however
            - Many manifold learnin algorithms don't have straightforward out of sample generalizatons...
        2) Learn the "interpolation" function between high dim space and low dim space with a multi-output regression
            - Regress high dim (H) data points against the embedding (D) data points to learn the manifold embedding
        3) When presented with a new data point, an H dimension vector, or tensor or whatever term is fashionable, 
           and "embed" it using the multi-output regression to output a D dimension vector

        Parameters
        ==========

        point : list
            List of points to use as inputs to a prediction

        Result
        ======

        prediction : list
            A list of output predictions
        """
        extra_params = {"features": point.values.tolist()}
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "predict",
                                          extra_params = extra_params)
        try:
           return pd.DataFrame(response['predict'])
        except:
           raise StandardError(response)

    def score(self):
        """ 
        Get the R^2 of the training dataset / predictions

        Returns
        =======

        r2 : float
            The R^2 of the training dataset
        """
        Y_hat = self.predict(self.X)
        return r_squared(Y_hat, self.Y)

