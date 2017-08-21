""" 
Classifier models are examples of supervised machine learning techniques which aim to predict the class label of a given input datapoint
"""
from core import BasePipeline
from utils import rando_name
from uuid import uuid4

# K Nearest Neighbors classifier pipeline
class KNNClassifierPipeline(BasePipeline):
    """ 
    Create a Pipeline for training :class:`.KNNClassifier` models from input datasets

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
        Should voting be uniform (i.e. independent of distance) or weighted by distance (i.e. closer neighbor's have higher weighted votes)

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

    Create a Pipeline for training multiple :class:`.KNNClassifier` models

    >>> io = ConnectIO(api_key)
    >>> pipe = KNNClassifierPipeline(K = 7, client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())
 
    """
    def __init__(self, name, K = 5, kernel = "euclidean", algo = "auto", weights = "uniform", kernel_params = {}, client = None):
        params = {"k": K,
                  "kernel": kernel,
                  "algo": algo,
                  "weights": weights,
                  "kernel_params": kernel_params}
        BasePipeline.__init__(self, name, "raw_knn_classifier", client, params)

    def run(self, dataset, model, class_column):
        """ 
        Run the Pipeline and create a new :class:`KNNClassifier` model

        Parameters
        ==========

        dataset : pandas.DataFrame
            The dataset to pass into the Pipeline which will train a :class:`KNNClassifier` model using the
            parameters defined upon Pipeline creation. Pipelines are reusable sets of instructions to train
            a machine learning model.

        Returns
        =======

        response : dict
            success or failure response to model creation request
        """
        return BasePipeline.run(self, dataset = dataset, model = model, extra_params = {"class_column": class_column})

# K Nearest Neighbors classifier model; if pipeline == None then create a pipeline for use with this model
class KNNClassifier():
    """ 
    Train / Reload a :class:`KNNClassifier` model

    Parameters
    ==========

    dataset : pandas.DataFrame
        Input DataFrame. shape = (n_rows, n_features + 1) where each row is a data point and the columns are numeric features and a
        column with the class labels

    name : string
        The desired name of the Pipeline.

    class_column : string
        The name of the column in the input dataset which describes the class labels

    K : integer, optional
        The desired K in the Nearest Neighbor classifier model

    kernel : string [ 'euclidean' | 'minkowski' | 'hammond' | 'etc...'], optional
        The desired kernel for defining distance in our classifier. Default is 'euclidean'

    algo : string ['auto' | 'ball' | 'kd_tree' | 'brute'], optional
        The algorithm to use in determining Nearest Neighbors. Default is 'auto'

    weights : string ['uniform' | 'weighted'], optional
        Should voting be uniform (i.e. independent of distance) or weighted by distance (i.e. closer neighbor's have higher weighted votes)

    kernel_params : dict, optional
        Any parameters specific to the chosen kernel

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    pipeline : string, optional
       An extant Pipeline to use for model creation. If None then one will be created

    Returns
    =======

    model : :class:`KNNClassifier`
        KNNClassifier model object

    Examples
    ========

    Create a KNNClassifier model for a given dataset

    >>> sm = SliceMatrix(api_key)
    >>> knn = sm.KNNClassifier(dataset = dataframe, K = 5)

    Predict the class of some new data

    >>> knn.predict([...])

    """
    def __init__(self, dataset = None, class_column = None, name = None, pipeline = None, K = 5, kernel = "euclidean", algo = "auto", weights = "uniform", kernel_params = {}, client = None):
        self.client  = client 
        self.type     = "raw_knn_classifier"
        if dataset is not None:
            self.__full_init__(dataset, class_column, name, pipeline, K, kernel, algo, weights, kernel_params, client)
        else:
            self.__lazy_init__(name)     
   
    def __full_init__(self, dataset, class_column, name = None, pipeline = None, k = 5, kernel = "euclidean", algo = "auto", weights = "uniform", kernel_params = {}, client = None):
        self.class_column = class_column
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.pipeline = pipeline
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = KNNClassifierPipeline(pipeline_name, k, kernel, algo, weights, kernel_params, client)
        self.response = self.pipeline.run(self.dataset, self.name, self.class_column)
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
        Predict the class of new input datapoints

        Parameters
        ==========

        point : list
            A list of new datapoints. Shape = (n_points, n_features)

        Returns
        =======

        prediction : list
            A list of new predictions for each input datapoint. Shape = (n_points, 1)

        """
        extra_params = {"features": point}
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "predict",
                                          extra_params = extra_params)
        try:
           return response['predict']
        except:
           raise StandardError(response)

    def score(self):
        """ 
        Get the training prediction R^2 

        Returns
        =======

        r2 : float
            The R^2 of the training predictions
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "score",
                                          extra_params = {})
        try:
           return response['score']
        except:
           raise StandardError(response)

    def training_preds(self):
        """ 
        Get the training predictions

        Returns
        =======

        prediction : list
            A list of the training predictions
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "training_preds",
                                          extra_params = {})
        try:
           return response['training_preds']
        except:
           raise StandardError(response)

    def training_data(self):
        """ 
        Get the input data used to train the model

        Returns
        =======

        data : list
            The training data
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "training_data",
                                          extra_params = {})
        try:
           return response['training_data']
        except:
           raise StandardError(response)

# probalistic neural network classifier pipeline
class PNNClassifierPipeline(BasePipeline):
    """ 
    Create a Pipeline for training :class:`.PNNClassifier` models from input datasets

    Parameters
    ==========

    name : string
        The desired name of the Pipeline.

    sigma : float in (0., 1.), optional
        The desired smoothing parameter for the PNN model. Default is 0.1

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========

    Create a Pipeline for training multiple :class:`.PNNClassifier` models

    >>> io = ConnectIO(api_key)
    >>> pipe = PNNClassifierPipeline(sigma = 0.05, client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())

    """

    def __init__(self, name, sigma = 0.1, client = None):
        params = {"sigma": sigma}
        BasePipeline.__init__(self, name, "raw_pnn", client, params)

    def run(self, dataset, model, class_column):
        """ 
        Run the Pipeline and create a new :class:`PNNClassifier` model

        Parameters
        ==========

        dataset : pandas.DataFrame
            The dataset to pass into the Pipeline which will train a :class:`PNNClassifier` model using the
            parameters defined upon Pipeline creation. Pipelines are reusable sets of instructions to train
            a machine learning model.

        Returns
        =======

        response : dict
            success or failure response to model creation request
        """
        return BasePipeline.run(self, dataset = dataset, model = model, extra_params = {"class_column": class_column})

# probalistic neural network classifier model; if pipeline == None then create a pipeline for use with this model
class PNNClassifier():
    """ 
    Train / Reload a :class:`PNNClassifier` model

    Parameters
    ==========

    dataset : pandas.DataFrame
        Input DataFrame. shape = (n_rows, n_features + 1) where each row is a data point and the columns are numeric features and a
        column with the class labels

    name : string
        The desired name of the Pipeline.

    class_column : string
        The name of the column in the input dataset which describes the class labels


    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    pipeline : string, optional
       An extant Pipeline to use for model creation. If None then one will be created

    Returns
    =======

    model : :class:`PNNClassifier`
        PNNClassifier model object

    Examples
    ========

    Create a PNNClassifier model for a given dataset

    >>> sm = SliceMatrix(api_key)
    >>> pnn = sm.PNNClassifier(dataset = dataframe, sigma = 0.12)

    Predict the class of some new data

    >>> pnn.predict([...])

    """
    def __init__(self, dataset, class_column, name = None, pipeline = None, sigma = 0.1, client = None):
        self.client  = client
        self.class_column = class_column
        self.type     = "raw_pnn"
        if dataset is not None:
            self.__full_init__(dataset, name, pipeline, sigma, client)
        else:
            self.__lazy_init__(name)

    def __full_init__(self, dataset, name = None, pipeline = None, sigma = 0.1, client = None):
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.pipeline = pipeline
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = PNNClassifierPipeline(pipeline_name, sigma, client)
        self.response = self.pipeline.run(self.dataset, self.name, self.class_column)
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
        Predict the class of new input datapoints

        Parameters
        ==========

        point : list
            A list of new datapoints. Shape = (n_points, n_features)

        Returns
        =======

        prediction : list
            A list of new predictions for each input datapoint. Shape = (n_points, 1)

        """
        extra_params = {"features": point}
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "predict",
                                          extra_params = extra_params)
        try:
           return response['predict']
        except:
           raise StandardError(response)

    def score(self):
        """ 
        Get the training prediction R^2

        Returns
        =======

        r2 : float
            The R^2 of the training predictions
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "score",
                                          extra_params = {})
        try:
           return response['score']
        except:
           raise StandardError(response)

    def training_preds(self):
        """ 
        Get the training predictions

        Returns
        =======

        prediction : list
            A list of the training predictions
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "training_preds",
                                          extra_params = {})
        try:
           return response['training_preds']
        except:
           raise StandardError(response)

    def training_data(self):
        """ 
        Get the input data used to train the model

        Returns
        =======

        data : list
            The training data
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "training_data",
                                          extra_params = {})
        try:
           return response['training_data']
        except:
           raise StandardError(response)


