""" 
Manifold Learning Pipelines and Models
"""
from core import BasePipeline
from utils import rando_name
from uuid import uuid4
import pandas as pd

#################################################################################################################################################################
class KernelPCAPipeline(BasePipeline):
    """ 
    Pipeline for creating Kernel Principal Component Analysis models

    For non-linear dimensionality reduction, simulation, classification, and regression. 

    Applies the kernel trick to PCA.

    Parameters
    ==========

    name : string
        The desired name of the Pipeline.

    D : int, optional
        The desired embedding dimension. Defaults to 2-D

    kernel : string, optional
        The distance kernel / metric to use in constructing the distance matrix. Default is euclidean.

    alpha : float, optional
        Parameter of ridge regression which learns the inverse transform. Ignored if invert == False

    invert : boolean, optional
        Whether to learn the inverse transform (from low dimension space back to high dimension space)

    kernel_params : dict, optional
        Any extra parameters specific to the chosen kernel

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========
    
    Create a KernelPCA Pipeline for processing multiple datasets

    >>> io = ConnectIO(api_key)
    >>> kpca_pipe = KernelPCAPipeline(D = 5, kernel = "rbf", client = io)
    >>> for dataframe in dataframes:
    >>>     current_kpca_model = kpca_pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())

    """
    def __init__(self, name, D = 2, kernel = "linear", alpha = 1.0, invert = False, kernel_params = {}, client = None):
        params = {"D": D,
                  "kernel": kernel,
                  "alpha": alpha,
                  "invert": invert,
                  "kernel_params": kernel_params}
        BasePipeline.__init__(self, name, "raw_kpca", client, params)

    def run(self, dataset, model):
        """ 
        Run the Pipeline and create a new KernelPCA model

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

class KernelPCA():
    """ 
    Kernel Principal Component Analysis model

    For non-linear dimensionality reduction, simulation, classification, and regression.

    Applies the kernel trick to PCA.

    Parameters
    ==========

    dataset : pandas.DataFrame, optional
        The dataset to use in training the KernelPCA model. If None, then lazy loading is in effect
        and a name parameter should be given which matches an already created model. 
        shape = (n_rows, n_features)

    name : string, optional
        The desired name of the model. If None then a random name will be generated. 
        If dataset == None, then the name will be used to lazy load the model from the SliceMatrix-IO 
        cloud. 

    D : int, optional
        The desired embedding dimension. Defaults to 2-D

    kernel : string, optional
        The distance kernel / metric to use in constructing the distance matrix. Default is euclidean.

    alpha : float, optional
        Parameter of ridge regression which learns the inverse transform. Ignored if invert == False

    invert : boolean, optional
        Whether to learn the inverse transform (from low dimension space back to high dimension space)

    kernel_params : dict, optional
        Any extra parameters specific to the chosen kernel

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    pipeline : string, optional
       An extant Pipeline to use for model creation. If None then one will be created

    Returns
    =======

    model : :class:`.KernelPCA`
        KPCA model object

    Examples
    ========

    Create a KernelPCA model for a given dataset

    >>> sm = SliceMatrix(api_key)
    >>> kpca = sm.KernelPCA(dataset = dataframe, D = 5, kernel = "rbf")
    
    Get the embedding

    >>> kpca.embedding()

    Learn the inverse transform

    >>> kpca = sm.KernelPCA(dataset = dataframe, invert = True)
    >>> kpca.inverse_embedding()

    """
    def __init__(self, dataset = None, name = None, pipeline = None, D = 2, kernel = "linear", alpha = 1.0, invert = False, kernel_params = {}, client = None):
        self.client  = client 
        self.type     = "raw_kpca"
        if dataset is not None:
            self.__full_init__(dataset, name, pipeline, D, kernel, alpha, invert, kernel_params, client)
        else:
            self.__lazy_init__(name)

    # full construction, i.e. start from zero and create it all...
    def __full_init__(self, dataset, name = None, pipeline = None, D = 2, kernel = "linear", alpha = 1.0, invert = False, kernel_params = {}, client = None):
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.pipeline = pipeline
        self.D        = D
        self.kernel   = kernel
        self.alpha    = alpha
        self.invert   = invert
        self.kernel_params = kernel_params
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = KernelPCAPipeline(pipeline_name, D, kernel, alpha, invert, kernel_params, client)
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

    def inverse_embedding(self, nodes = True):
        """ 
        Get the inverse embedding of the training data in original dimensions 

        I.e. 

        1) Take input data in high dimensions
        2) Transform via KPCA to D dimensions
        3) Tranform back to high dimensions using model

        Parameters
        ==========
        
        nodes : boolean, optional
            Whether to return with node names. Default == True

        Returns
        =======
        
        inverse_embedding : pandas.DataFrame
            Original dimension inverse embedding. shape = (n_rows, n_features)

        """
        nodes = self.nodes()
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "inverse_embedding",
                                          extra_params = {})
        try:
           return pd.DataFrame(response['inverse_embedding'], index = nodes)
        except:
           raise StandardError(response)

    def embedding(self, nodes = True):
        """ 
        Get the D dimensional embedding of the training data

        I.e. 
  
        1) Take input data in high dimensions
        2) Transform via KPCA to D dimensions

        Parameters
        ==========

        nodes : boolean, optional
            Whether to return with node names. Default == True

        Returns
        =======

        embedding : pandas.DataFrame
            D dimensional embedding. shape = (n_rows, D)

        """
        nodes = self.nodes()
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "embedding",
                                          extra_params = {})
        try:
           return pd.DataFrame(response['embedding'], index = nodes)
        except:
           raise StandardError(response)

    def nodes(self):
        """ 
        Get the names of the data points / nodes that make of the training dataset

        Returns
        =======

        nodes : list
            Data point names / indices
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "nodes",
                                          extra_params = {})
        try:
           return response['nodes']
        except:
           raise StandardError(response)

    def meta(self):
        """ 
        Get the model metadata such as D, kernel name, etc...

        Returns
        =======
        meta : dict
            Model metadata
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "meta",
                                          extra_params = {})
        try:
           return response['meta']
        except:
           raise StandardError(response)

    def feature_names(self):
        """ 
        Get the names of the features, if applicable

        Returns
        =======
        meta : dict
            Model feature names 
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "feature_names",
                                          extra_params = {})
        try:
           return response['feature_names']
        except:
           raise StandardError(response)


#################################################################################################################################################################
class LocalLinearEmbedderPipeline(BasePipeline):
    """ 
    Create a Pipeline for training Local Linear Embedder models

    Parameters
    ==========

    name : string
        The desired name of the Pipeline.

    D : int, optional
        The desired embedding dimension. Defaults to 2-D

    K : integer greater than 1, optional
        The number of neighbors to use in building the embedding. Default is 3

    method : string ['standard' | 'hessian' | 'modified' | 'ltsa']
        Which LLE algorithm should we use?

        'standard' : standard LLE method

        'hessian': hessian eigenmap LLE method, requires that K > D * (1 + (D + 1) / 2

        'modified' : modified LLE method

        'ltsa': local tangent space alignment LLE method

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========

    Create a :class:`LocalLinearEmbedder` Pipeline for processing multiple datasets

    >>> io = ConnectIO(api_key)
    >>> lle_pipe = LocalLinearEmbedderPipeline(D = 2, client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = lle_pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())
    
    """
    def __init__(self, name, D = 2, K = 3, method = "standard", client = None):
        params = {"D": D,
                  "k": K,
                  "method": method}
        BasePipeline.__init__(self, name, "raw_lle", client, params)

    def run(self, dataset, model):
        """ 
        Run the Pipeline and create a new LocalLinearEmbedder model

        Parameters
        ==========

        dataset : pandas.DataFrame
            The dataset to pass into the Pipeline which will train a LocalLinearEmbedder model using the 
            parameters defined upon Pipeline creation. Pipelines are reusable sets of instructions to train 
            a machine learning model.

        Returns
        =======

        response : dict
            success or failure response to model creation request

        """        
        return BasePipeline.run(self, dataset = dataset, model = model)

class LocalLinearEmbedder():
    """ 
    Create a Pipeline for training Local Linear Embedder models

    Parameters
    ==========

    name : string
        The desired name of the model.

    D : int, optional
        The desired embedding dimension. Defaults to 2-D

    K : integer greater than 1, optional
        The number of neighbors to use in building the embedding. Default is 3

    method : string ['standard' | 'hessian' | 'modified' | 'ltsa']
        Which LLE algorithm should we use?

        'standard' : standard LLE method

        'hessian': hessian eigenmap LLE method, requires that K > D * (1 + (D + 1) / 2

        'modified' : modified LLE method

        'ltsa': local tangent space alignment LLE method

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    pipeline : string, optional
       An extant Pipeline to use for model creation. If None then one will be created

    Returns
    =======

    model : :class:`LocalLinearEmbedder`
        LLE model object

    Examples
    ========

    Create a LLE model for a given dataset

    >>> sm = SliceMatrix(api_key)
    >>> lle = sm.LocalLinearEmbedder(dataset = dataframe, D = 2)
        
    """
    def __init__(self, dataset = None, name = None, pipeline = None, D = 2, K = 3, method = "standard", client = None):
        self.client  = client
        self.type     = "raw_lle"
        if dataset is not None:
            self.__full_init__(dataset, name, pipeline, D, K, method, client)
        else:
            self.__lazy_init__(name)        

    def __full_init__(self, dataset, name = None, pipeline = None, D = 2, k = 3, method = "standard", client = None):
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.pipeline = pipeline
        self.D        = D
        self.k        = k
        self.method   = method
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = LocalLinearEmbedderPipeline(pipeline_name, D, k, method, client)
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

    def embedding(self, nodes = True):
        """ 
        Get the D dimensional embedding of the training data

        I.e.

        1) Take input data in high dimensions
        2) Transform via LLE to D dimensions

        Parameters
        ==========

        nodes : boolean, optional
            Whether to return with node names. Default == True

        Returns
        =======

        embedding : pandas.DataFrame
            D dimensional embedding. shape = (n_rows, D)

        """
        nodes = self.nodes()
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "embedding",
                                          extra_params = {})
        try:
           return pd.DataFrame(response['embedding'], index = nodes)
        except:
           raise StandardError(response)

    def nodes(self):
        """ 
        Get the names of the data points / nodes that make of the training dataset

        Returns
        =======

        nodes : list
            Data point names / indices
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "nodes",
                                          extra_params = {})
        try:
           return response['nodes']
        except:
           raise StandardError(response)

    def recon_error(self):
        """ 
        Get the reconstruction error of the LLE model.

        Reconstruction error of the embedding

        Returns
        =======

        recon_error : float
            Reconstruction error for the model
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "recon_error",
                                          extra_params = {})
        try:
           return response['recon_err']
        except:
           raise StandardError(response)

    def meta(self):
        """ 
        Get the model metadata such as D, method, etc...

        Returns
        =======
        meta : dict
            Model metadata
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "meta",
                                          extra_params = {})
        try:
           return response['meta']
        except:
           raise StandardError(response)

    def feature_names(self):
        """ 
        Get the names of the features, if applicable

        Returns
        =======
        meta : dict
            Model feature names
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "feature_names",
                                          extra_params = {})
        try:
           return response['feature_names']
        except:
           raise StandardError(response)


#################################################################################################################################################################
class LaplacianEigenmapperPipeline(BasePipeline):
    """ 
    Create a Laplacian Eigenmapper Pipeline for creating :class:`.LaplacianEigenmapper` models from input
    training datasets

    Parameters
    ==========

    name : string
        The desired name of the Pipeline.

    D : int, optional
        The desired embedding dimension. Defaults to 2-D

    affinity : string ["knn" | "rbf"], optional
        How should we construct the affinity matrix?

        "knn" : use k nearest neighbors graph

        "rbf" : use radial basis function kernel

    K : integer greater than 1, optional
        The K to use if affinity is "knn".

    gamma : float, optional
        Kernel coefficient for affinity "rbf"

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========

    Create a Pipeline for processing multiple datasets into :class:`.LaplacianEigenmapper` models

    >>> io = ConnectIO(api_key)
    >>> spectral_pipe = LaplacianEigenmapperPipeline(D = 5, client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = spectral_pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())
    

    """
    def __init__(self, name, D = 2, affinity = "knn", K = 5, gamma = 1.0, client = None):
        params = {"D": D,
                  "K": K,
                  "affinity": affinity,
                  "gamma": gamma}
        BasePipeline.__init__(self, name, "raw_laplacian_eigenmap", client, params)

    def run(self, dataset, model):
        """ 
        Run the Pipeline and create a new :class:`.LaplacianEigenmapper` model

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

class LaplacianEigenmapper():
    """ 
    Train / Reload a Laplacian Eigenmapper model 

    Parameters
    ==========

    dataset : pandas.DataFrame
        Input DataFrame. shape = (n_rows, n_features) where each row is a data point and the columns are numeric features

    D : int, optional
        The desired embedding dimension. Defaults to 2-D

    affinity : string ["knn" | "rbf"], optional
        How should we construct the affinity matrix?

        "knn" : use k nearest neighbors graph

        "rbf" : use radial basis function kernel

    K : integer greater than 1, optional
        The K to use if affinity is "knn".

    gamma : float, optional
        Kernel coefficient for affinity "rbf"

    name : string, optional
        The desired name of the model. If None then a random name will be generated

    pipeline : string, optional
       An extant Pipeline to use for model creation. If None then one will be created

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    model : :class:`.LaplacianEigenmapper`

    Examples
    ========

    Create a model for a given dataset

    >>> sm = SliceMatrix(api_key)
    >>> spectral = sm.KernelPCA(dataset = dataframe, D = 3)

    Get the embedding

    >>> spectral.embedding()

    """
    def __init__(self, dataset = None, name = None, pipeline = None, D = 2, affinity = "knn", K = 5, gamma = 1.0, client = None):
        self.client  = client
        self.type     = "raw_laplacian_eigenmap"
        if dataset is not None:
            self.__full_init__(dataset, name, pipeline, D, affinity, K, gamma, client)
        else:
            self.__lazy_init__(name)        

    def __full_init__(self, dataset, name = None, pipeline = None, D = 2, affinity = "knn", K = 5, gamma = 1.0, client = None):
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.pipeline = pipeline
        self.D        = D
        self.K        = K
        self.affinity = affinity
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = LaplacianEigenmapperPipeline(pipeline_name, D, affinity, K, gamma, client)
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

    def embedding(self, nodes = True):
        """ 
        Get the D dimensional embedding of the training data

        I.e.

        1) Take input data in high dimensions
        2) Transform via Laplacian Eigenmapper to D dimensions

        Parameters
        ==========

        nodes : boolean, optional
            Whether to return with node names. Default == True

        Returns
        =======

        embedding : pandas.DataFrame
            D dimensional embedding. shape = (n_rows, D)

        """
        nodes = self.nodes()
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "embedding",
                                          extra_params = {})
        try:
           return pd.DataFrame(response['embedding'], index = nodes)
        except:
           raise StandardError(response)

    def nodes(self):
        """ 
        Get the names of the data points / nodes that make of the training dataset

        Returns
        =======

        nodes : list
            Data point names / indices
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "nodes",
                                          extra_params = {})
        try:
           return response['nodes']
        except:
           raise StandardError(response)

    def meta(self):
        """ 
        Get the model metadata such as D, affinity, etc...

        Returns
        =======
        meta : dict
            Model metadata
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "meta",
                                          extra_params = {})
        try:
           return response['meta']
        except:
           raise StandardError(response)

    def feature_names(self):
        """ 
        Get the names of the features, if applicable

        Returns
        =======
        meta : dict
            Model feature names
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "feature_names",
                                          extra_params = {})
        try:
           return response['feature_names']
        except:
           raise StandardError(response)

    def affinity_matrix(self):
        """ 
        Get the affinity matrix used to perform the embedding

        Returns
        =======
        affinity_matrix : matrix-like
            Model affinity matrix shape = (n_rows, n_rows)
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "affinity_matrix",
                                          extra_params = {})
        try:
           return response['affinity_matrix']
        except:
           raise StandardError(response)

#################################################################################################################################################################
class IsomapPipeline(BasePipeline):
    """ 
    Create a Pipeline for training :class:`.Isomap` models

    Parameters
    ==========

    name : string
        The desired name of the Pipeline.

    D : int, optional
        The desired embedding dimension. Defaults to 2-D

    K : integer greater than 1, optional, ignored if geodesic == False
        The number of neighbors to use in building the geodesic distance matrix. Geodesic distance is constructed by computing the
        K Nearest Neighbors graph for the input dataset, then constructing all pairwise distances using the geodesic distance, i.e.
        the number of edges in a shortest path between two points on the graph.

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========

    Create a Isomap Pipeline for processing multiple datasets

    >>> io = ConnectIO(api_key)
    >>> iso_pipe = KernelPCAPipeline(D = 3, K = 4, client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = iso_pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())
    
    """
    def __init__(self, name, D = 2, K = 3, client = None):
        params = {"D": D,
                  "K": K}
        BasePipeline.__init__(self, name, "raw_isomap", client, params)

    def run(self, dataset, model):
        """ 
        Run the Pipeline and create a new :class:`.Isomap` model

        Parameters
        ==========

        dataset : pandas.DataFrame
            The dataset to pass into the Pipeline which will train an :class:`.Isomap` model using the parameters
            defined upon Pipeline creation. Pipelines are reusable sets of instructions to train a machine
            learning model.

        Returns
        =======

        response : dict
            success or failure response to model creation request

        """
        return BasePipeline.run(self, dataset = dataset, model = model)

class Isomap():
    """ 
    Train / Reload an Isomap model

    Parameters
    ==========

    name : string, optional
        The desired name of the model. If None then a random name will be generated.
        If dataset == None, then the name will be used to lazy load the model from the SliceMatrix-IO
        cloud.

    dataset : pandas.DataFrame
        Input DataFrame. shape = (n_rows, n_features) where each row is a data point and the columns are numeric features

    D : int, optional
        The desired embedding dimension. Defaults to 2-D

    K : integer greater than 1, optional, ignored if geodesic == False
        The number of neighbors to use in building the geodesic distance matrix. Geodesic distance is constructed by computing the
        K Nearest Neighbors graph for the input dataset, then constructing all pairwise distances using the geodesic distance, i.e.
        the number of edges in a shortest path between two points on the graph.

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    pipeline : string, optional
       An extant Pipeline to use for model creation. If None then one will be created

    Returns
    =======

    model : :class:`.Isomap`
        Isomap model object

    Examples
    ========

    Create a model for a given dataset

    >>> sm = SliceMatrix(api_key)
    >>> iso = sm.Isomap(dataset = dataframe, D = 3, K = 10)

    Get the embedding

    >>> iso.embedding()

    """
    def __init__(self, dataset, name = None, pipeline = None, D = 2, K = 3, client = None):
        self.client  = client
        self.type     = "raw_isomap"
        if dataset is not None:
            self.__full_init__(dataset.T, name, pipeline, D, K, client)
        else:
            self.__lazy_init__(name)

    def __full_init__(self, dataset, name = None, pipeline = None, D = 2, K = 3, client = None):
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.pipeline = pipeline
        self.D        = D
        self.K        = K
        self.type     = "raw_isomap"
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = IsomapPipeline(pipeline_name, D, K, client)
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

    def embedding(self, nodes = True):
        """ 
        Get the D dimensional embedding of the training data

        I.e.

        1) Take input data in high dimensions
        2) Transform via Isomap to D dimensions

        Parameters
        ==========

        nodes : boolean, optional
            Whether to return with node names. Default == True

        Returns
        =======

        embedding : pandas.DataFrame
            D dimensional embedding. shape = (n_rows, D)

        """
        nodes = self.nodes()
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "embedding",
                                          extra_params = {})
        try:
           return pd.DataFrame(response['embedding'], index = nodes)
        except:
           raise StandardError(response)

    def nodes(self):
        """ 
        Get the names of the data points / nodes that make of the training dataset

        Returns
        =======

        nodes : list
            Data point names / indices
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "nodes",
                                          extra_params = {})
        try:
           return response['nodes']
        except:
           raise StandardError(response)

    def recon_error(self):
        """ 
        Get the reconstruction error of the model.

        Reconstruction error of the embedding

        Returns
        =======

        recon_error : float
            Reconstruction error for the model
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "recon_error",
                                          extra_params = {})
        try:
           return response['recon_error']
        except:
           raise StandardError(response)

    def rankLinks(self):
        """  
        Rank the links by geodesic distance

        Returns
        =======

        links : dict
            dictionary of links with associated geodesic distances
            
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "rankLinks",
                                          extra_params = {})
        try:
           return response['rankLinks']
        except:
           raise StandardError(response)

    def edges(self):
        """ 
        Get a list of all the edges in the KNN graph used to created the Isomap model

        Returns
        =======

        edges : list
            list of all edge / link tuples. Source is edge[0] Target is edge[1]
        """
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "edges",
                                          extra_params = {})
        try:
           return response['edges']
        except:
           raise StandardError(response)

    def rankNodes(self, statistic = "closeness_centrality"):
        """ 
        Rank the model's nodes by the given network graph statistic / factor

        Parameters
        ==========

        statistic : string ['degree_centrality' | 'eigen_centrality' | 'closeness_centrality' | 'betweenness_centrality' | 'is_connected' |
                            'curr_flow_centrality' | 'pagerank' | 'hits' | 'communicability' | 'clustering' | 'square_clustering' |
                            'greedy_colors' | 'eccentricity' | 'clique_numbers' | 'number_of_cliques' | 'estrada_index' | 'assortivity' |
                            'transitivity' | 'avg_clustering' | 'maximal_matching' | 'max_weight_matching' | 'dispersion']

            The desired graph statistic

        Returns
        =======

        stats : array-like
            Depending on the statistic this will be an array or a single float value

        """
        extra_params = {"statistic": statistic}
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "rankNodes",
                                          extra_params = extra_params)
        try:
           return pd.DataFrame(response['rankNodes'], index = [statistic]).T.sort(columns = statistic)
        except:
           raise StandardError(response)

    def neighborhood(self, node):
        """ 
        Get the nearest neighbors of the given node

        Parameters
        ==========

        node : string
            The name of the target node we want to find the nearest neighbors for

        Returns
        =======

        neighbors : dict
            Dictionary of nearest neighbors with distances to target node

        """
        extra_params = {"node": node}
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "neighborhood",
                                          extra_params = extra_params)
        try:
           return response['neighborhood']
        except:
           raise StandardError(response)

    def search(self, point):
        extra_params = {"point": point}
        response = self.client.call_model(model  = self.name,
                                          type   = self.type,
                                          method = "search",
                                          extra_params = extra_params)
        try:
           return response['search']
        except:
           raise StandardError(response)





