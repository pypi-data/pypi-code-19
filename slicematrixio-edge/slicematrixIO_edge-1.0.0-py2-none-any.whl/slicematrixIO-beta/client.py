"""High Level Python Client for the SliceMatrix-IO Machine Learning PaaS"""
from connect import ConnectIO, Uploader

from bayesian_filters import KalmanOLS                                                     # lazy loading enabled
from distributions import KernelDensityEstimator, BasicA2D, IsolationForest                # lazy loading enabled                
from classifiers import KNNClassifier, PNNClassifier                                       # lazy loading enabled
from graphs import MinimumSpanningTree, CorrelationFilteredGraph, NeighborNetworkGraph     # lazy loading enabled 
from matrices import DistanceMatrix, LazyMatrix                                            # lazy loading enabled
from matrix_models import MatrixMinimumSpanningTree, MatrixKernelPCA, MatrixAgglomerator   # lazy loading enabled
from manifolds import KernelPCA, LocalLinearEmbedder, LaplacianEigenmapper, Isomap         # lazy loading enabled
from regressors import KNNRegressor, RFRegressor, KernelRidgeRegressor                     # lazy loading enabled
from stress_tests import PortfolioStressTest                                               # lazy loading enabled

class SliceMatrix():
    """ 
    Main business object for slicematrixIO-python

    Builds upon low level api (ConnectIO) to create high level objects for each model type.

    The models are meant to be created by the client, as opposed to instantiated directly.

    Parameters
    ==========
    api_key: string
        A Valid SliceMatrix-IO API Key

    region : string ['us-east-1', 'us-west-1', 'eu-central-1', 'ap-southeast-1']
        Data center of choice. API Key must be valid for that specific data center.
        Latency will be lowest if client is closest to data center.

        'us-east-1': US East Coast Data Center

        'us-west-1': US West Coast Data Center

        'eu-central-1': Continental Europe Data Center

        'ap-southeast-1': South-East Asian Data Center

    Attributes
    ==========
    client : ConnectIO
        Low level SliceMatrix-IO Python client      

    Examples
    ========

    Create a Kernel Density Estimator model that lives in the cloud

    >>> kde = sm.KernelDensityEstimator(dataset=df) 

    Score a new data point

    >>> kde.score(10325632)

    Simulate 1000 new data points

    >>> kde.simulate(1000) 

    Manifold Learning:

    >>> iso = sm.Isomap(dataset=prices)

    Get statistics / factors related to internal graph structure of each node

    >>> iso.rankNodes("pagerank")

    Find low dimensional embedding of input data

    >>> iso.embedding() 

    See www.slicematrix.com/use-cases for more in-depth examples

    """
    def __init__(self, api_key, region = "us-east-1"):
        self.api_key = api_key
        self.client  = ConnectIO(self.api_key, region = region)

    # bayesian filters ##########################################################################################################################################################
    # need to test this
    def KalmanOLS(self, dataset = None, init_alpha = None, init_beta = None, trans_cov = None, obs_cov = None, init_cov = None, optimizations = [], name = None, pipeline = None):
        """ 
        Create slicematrixIO.bayesian_filters.KalmanOLS object with current client

        The KalmanOLS model 

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

        pipeline : BasePipeline, optional
            Pipeline to use. Defaults to None. If None then a pipeline will be created for use in creating the model

        Returns
        =======

        model : :class:`slicematrixIO.bayesian_filters.KalmanOLS`

        """
        return KalmanOLS(dataset = dataset,
                         init_alpha = init_alpha,
                         init_beta  = init_beta,
                         trans_cov  = trans_cov,
                         obs_cov  = obs_cov,
                         init_cov = init_cov,
                         optimizations = optimizations,
                         name     = name,
                         pipeline = pipeline,
                         client   = self.client)

    # classifiers ###############################################################################################################################################################
    def KNNClassifier(self, dataset = None, class_column = None, name = None, pipeline = None, K = 5, kernel = "euclidean", algo = "auto", weights = "uniform", kernel_params = {}):
        """ 
        Create K Nearest Neighbors Classifier model

        Parameters
        ==========

        dataset : pandas.DataFrame
            Input DataFrame. shape = (n_rows, n_features + 1) where each row is a data point and the columns are numeric features and a 
            column with the class labels

        class_column : string
            The name of the column in the input dataset which describes the class labels

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

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

        Returns
        =======

        model : :class:`slicematrixIO.classifiers.KNNClassifier`
        
        """
        return KNNClassifier(dataset  = dataset, 
                             class_column = class_column,
                             name     = name, 
                             pipeline = pipeline, 
                             K        = K,
                             kernel   = kernel, 
                             algo     = algo, 
                             weights  = weights, 
                             kernel_params = kernel_params, 
                             client   = self.client)

    def PNNClassifier(self, dataset = None, class_column = None, name = None, pipeline = None, sigma = 0.1):
        """ 
        Create a Probabilistic Neural Network Classifier model

        Parameters
        ==========

        dataset : pandas.DataFrame
            Input DataFrame. shape = (n_rows, n_features + 1) where each row is a data point and the columns are numeric features and a
            column with the class labels

        class_column : string
            The name of the column in the input dataset which describes the class labels

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        sigma : float in (0., 1.), optional
            The desired smoothing parameter for the PNN model. Default is 0.1

        Returns
        =======

        model : :class:`slicematrixIO.classifiers.PNNClassifier`
        """
        return PNNClassifier(dataset  = dataset,
                             class_column = class_column,
                             name     = name,
                             pipeline = pipeline,
                             sigma    = sigma,
                             client   = self.client)

    
    # distributions #############################################################################################################################################################
    def KernelDensityEstimator(self, dataset = None, bandwith = "scott", kernel_params = {}, name = None, pipeline = None):
        """ 
        Train a Kernel Density Estimator model 

        Parameters
        ==========        

        dataset : pandas.DataFrame
            Input DataFrame. shape = (n_rows, n_features + 1) where each row is a data point and the columns are numeric features and a
            column with the class labels

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        bandwidth : str ['scott' | 'silverman'], optional
            The method for bandwidth selection in the KDE model

        kernel_params : dict, optional
            Any parameters specific to the chosen kernel

        Returns
        =======
        model : :class:`slicematrixIO.distributions.KernelDensityEstimator`
 
        """
        return KernelDensityEstimator(dataset  = dataset,
                                      bandwidth = bandwith,
                                      name     = name,
                                      pipeline = pipeline,
                                      client   = self.client)

    def BasicA2D(self, dataset = None, retrain = True, name = None, pipeline = None):
        """ 
        Create a BasicA2D model (basic automatic anomaly detection)

        Parameters
        ==========

        dataset : pandas.DataFrame
            Input DataFrame. shape = (n_rows, n_features + 1) where each row is a data point and the columns are numeric features and a
            column with the class labels

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        retrain : boolean, optional
            Whether to automatically retrain the model upon a remote call to the update method. The BasicA2D is a window detector which
            can be retrained in an online fashion where new data is used to update the model's understanding of the world and influence
            future anomaly scoring. 

        Returns
        =======
        model : :class:`slicematrixIO.distributions.BasicA2D`
        
        """
        return BasicA2D(dataset  = dataset,
                        retrain  = retrain,
                        name     = name,
                        pipeline = pipeline,
                        client   = self.client)

    def IsolationForest(self, dataset = None, rate = 0.1, n_trees = 100, name = None, pipeline = None):
        """ 
        Create an Isolation Forest model for automatic anomaly detection

        Parameters
        ==========

        dataset : pandas.DataFrame
            Input DataFrame. shape = (n_rows, n_features + 1) where each row is a data point and the columns are numeric features and a
            column with the class labels

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        rate : float in (0., 0.5), optional
            The desired rate of anomaly detection in training data. Default is 0.1 i.e. 10%

        n_trees : integer greater than 1, optional
            The number of trees to use in construction of the Isolation Forest model. Default is 100 trees

         Returns
        =======
        model : :class:`slicematrixIO.distributions.IsolationForest`

        """
        return IsolationForest(dataset  = dataset,
                               rate  = rate,
                               n_trees = n_trees,
                               name     = name,
                               pipeline = pipeline,
                               client   = self.client)

    # regressors ################################################################################################################################################################
    def KNNRegressor(self, X = None, Y = None, K = 5, kernel = "euclidean", algo = "auto", weights = "uniform", kernel_params = {}, name = None, pipeline = None):
        """ 
        Create a K Nearest Neighbors Regressor model

        Multi-output regression finds function from input space Y to lower dimension output space

        Parameters
        ==========

        X : pandas.DataFrame
            Input DataFrame. shape = (n_rows, input_features) where each row is a data point and the columns are numeric features

        Y : pandas.DataFrame
            Output DataFrame. shape = (n_rows, output_features) where output_features < input_features and each row is a data point
            and the columns are numeric features

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

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
        
      
        Returns
        =======
        model : :class:`slicematrixIO.regressors.KNNRegressor`

        """
        return KNNRegressor(X = X,
                            Y = Y,
                            name     = name,
                            pipeline = pipeline,
                            K        = K,
                            kernel   = kernel,
                            algo     = algo,
                            weights  = weights,
                            kernel_params = kernel_params,
                            client   = self.client)


    def RFRegressor(self, X = None, Y = None, n_trees = 8, name = None, pipeline = None):
        """ 
        Create a Random Forest Regressor model

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

        Returns
        =======
        model : :class:`slicematrixIO.regressors.RFRegressor`
        """
        return RFRegressor(X = X, 
                           Y = Y, 
                           n_trees = n_trees, 
                           name = name,
                           pipeline = pipeline,
                           client = self.client)

    def KernelRidgeRegressor(self, X = None, Y = None, kernel = "linear", alpha = 1.0, kernel_params = {}, name = None, pipeline = None):
        """ 
        Create a Kernel Ridge Regressor model

        Parameters
        ==========

        X : pandas.DataFrame
            Input DataFrame. shape = (n_rows, input_features) where each row is a data point and the columns are numeric features

        Y : pandas.DataFrame
            Output DataFrame. shape = (n_rows, output_features) where output_features < input_features and each row is a data point
            and the columns are numeric features

        alpha : float, optional
            Kernel Ridge Regressor model alpha value. Default 1.0
 
        kernel : string ['linear', 'rbf', 'poly']
            Kernel to use in regression. Linear is default. For nonlinear datasets, consider rbf or poly
        
            'linear' : linear kernel 

            'rbf' : radial basis function kernel

            'poly' : polynomial kernel

        kernel_params : dict
            Kernel specific parameters

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        Returns
        =======
        model : :class:`slicematrixIO.regressors.KernelRidgeRegressor`

        """
        return KernelRidgeRegressor(X = X,
                                    Y = Y,
                                    kernel = kernel, 
                                    alpha  = alpha,
                                    kernel_params = kernel_params,
                                    name = name,
                                    pipeline = pipeline,
                                    client = self.client)
         
    # matrices #################################################################################################################################################################
    def DistanceMatrix(self, dataset = None, K = 5, kernel = "euclidean", kernel_params = {}, geodesic = False, name = None, pipeline = None):
        """ 
        Create a Distance Matrix model  

        Parameters
        ==========

        dataset : pandas.DataFrame
            Input DataFrame. shape = (n_rows, n_features + 1) where each row is a data point and the columns are numeric features and a
            column with the class labels

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

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

        Returns
        =======

        model : :class:`slicematrixIO.matrices.DistanceMatrix`

        """
        return DistanceMatrix(dataset = dataset,
                              K       = K,
                              kernel  = kernel,
                              kernel_params = kernel_params,
                              geodesic = geodesic,
                              name = name,
                              pipeline = pipeline,
                              client   = self.client)

    def LazyMatrix(self, dataset = None, kernel = "euclidean", kernel_params = {}, name = None, pipeline = None):
        return LazyMatrix(dataset = dataset,
                              kernel  = kernel,
                              kernel_params = kernel_params,
                              name = name,
                              pipeline = pipeline,
                              client   = self.client)

							  
    # matrix models ############################################################################################################################################################
    def MatrixMinimumSpanningTree(self, matrix = None, matrix_name = None, matrix_type = None, name = None, pipeline = None):
        """ 
        Create a Minimum Spanning Tree model from a Distance Matrix model

        This is an example of a Matrix Model, which creates a machine learning model using another already trained model as
        its input. You can think of this as model chaining. 

        In this case, this function takes a previously created Distance Matrix model and uses it to construct a network graph
        model called a Minimum Spanning Tree.

        Parameters
        ==========

        matrix : object
            Matrix model object; i.e. a class from slicematrixIO.matrices

        matrix_name : string, optional
            The name of the existing matrix model. Optional if matrix is not None

        matrix_type :
            The type of the matrix model. Optional if matrix is not None. Required if using matrix_name

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        Returns
        =======

        model : :class:`slicematrixIO.matrix_models.MatrixMinimumSpanningTree`

        """
        return MatrixMinimumSpanningTree(matrix = matrix,
                                         matrix_name = matrix_name,
                                         matrix_type = matrix_type,
                                         name = name,
                                         pipeline = pipeline,
                                         client   = self.client)

    def MatrixKernelPCA(self, D = 2, matrix = None, matrix_name = None, matrix_type = None, name = None, pipeline = None):
        """ 
        Decompose the input matrix and embed the input into a lower dimension space

        Parameters
        ==========

        D : int, optional
            The desired embedding dimension. Defaults to 2-D

        matrix : object
            Matrix model object; i.e. a class from slicematrixIO.matrices

        matrix_name : string, optional
            The name of the existing matrix model. Optional if matrix is not None

        matrix_type :
            The type of the matrix model. Optional if matrix is not None. Required if using matrix_name

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        Returns
        =======

        model : :class:`slicematrixIO.matrix_models.MatrixKernelPCA`

        """
        return MatrixKernelPCA(D = D, 
                               matrix = matrix,
                               matrix_name = matrix_name,
                               matrix_type = matrix_type,
                               name = name,
                               pipeline = pipeline,
                               client   = self.client)

    def MatrixAgglomerator(self, label_dataset = None, alpha = 0.1, matrix = None, matrix_name = None, matrix_type = None, name = None, pipeline = None):
        """ 
        Create a Matrix Agglomerator model. Essential for supervised manifold learning, this model takes a previously created matrix model as input and
        applies class label information to the similarity matrix. In a nutshell, this model pulls data points of the same class closer together, increasing
        the separability of the dataset. 

        Parameters
        ==========

        label_dataset : pandas.DataFrame
            The class label information. shape = (n_rows, 1). n_rows should be same dimension as input matrix

        alpha : float in (0., 1.)
            The agglomeration factor, i.e. how much does class label effect input distances. An alpha of 0 will
            have no effect, while 1.0 will pull data points of the same class completely together. The higher
            the value of alpha, the more information will be transfered to the distance matrix from the class
            labels. Higher alphas increase the in-sample performance but also increase the chance of over-fitting

        matrix : object
            Matrix model object; i.e. a class from :mod:`slicematrixIO.matrices`

        matrix_name : string, optional
            The name of the existing matrix model. Optional if matrix is not None

        matrix_type :
            The type of the matrix model. Optional if matrix is not None. Required if using matrix_name

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created
        
        Returns
        =======

        model : :class:`slicematrixIO.matrix_models.MatrixAgglomerator`
        """
        return MatrixAgglomerator(alpha = alpha, 
                                  label_dataset = label_dataset,
                                  matrix = matrix,
                                  matrix_name = matrix_name,
                                  matrix_type = matrix_type,
                                  name = name,
                                  pipeline = pipeline,
                                  client   = self.client)

    # manifolds ################################################################################################################################################################
    def KernelPCA(self, dataset = None, D = 2, kernel = "linear", alpha = 1.0, invert = False, kernel_params = {}, name = None, pipeline = None):
        """ 
        Create a Kernel Principal Components Analysis model for non-linear dimensionality reduction. Applies the kernel trick to PCA

        Parameters
        ==========

        dataset : pandas.DataFrame
            Input DataFrame. shape = (n_rows, n_features) where each row is a data point and the columns are numeric features

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

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        Returns
        =======

        model : :class:`slicematrixIO.manifolds.KernelPCA`
        
        """
        return KernelPCA(dataset = dataset,
                         D = D,
                         kernel  = kernel,
                         kernel_params = kernel_params,
                         alpha = alpha,
                         invert = invert,
                         name = name,
                         pipeline = pipeline,
                         client   = self.client)

    def LocalLinearEmbedder(self, dataset = None, D = 2, K = 3, method = "standard", name = None, pipeline = None):
        """ 
        Create a Local Linear Embedder model for non-linear dimensonality reduction

        Parameters
        ==========

        dataset : pandas.DataFrame
            Input DataFrame. shape = (n_rows, n_features) where each row is a data point and the columns are numeric features

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

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        Returns
        =======

        model : :class:`slicematrixIO.manifolds.LocalLinearEmbedder`

        """                               

        return LocalLinearEmbedder(dataset = dataset,
                                   D = D,
                                   K = K,
                                   method = method, 
                                   name = name, 
                                   pipeline = pipeline,
                                   client   = self.client)

    def LaplacianEigenmapper(self, dataset = None, D = 2, affinity = "knn", K = 5, gamma = 1.0, name = None, pipeline = None):
        """ 
        Create Laplacian Eiegenmapper model aka spectral embedder for non-linear dimensonality reduction

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

        Returns
        =======

        model : :class:`slicematrixIO.manifolds.LaplacianEigenmapper`

        """
        return LaplacianEigenmapper(dataset = dataset,
                                    D = D,
                                    K = K,
                                    gamma = gamma,
                                    name = name,
                                    pipeline = pipeline,
                                    client   = self.client)

    def Isomap(self, dataset = None, D = 2, K = 3, name = None, pipeline = None):
        """ 
        Create Isomap model for non-linear dimensonality reduction

        Parameters
        ==========

        dataset : pandas.DataFrame
            Input DataFrame. shape = (n_rows, n_features) where each row is a data point and the columns are numeric features

        D : int, optional
            The desired embedding dimension. Defaults to 2-D

        K : integer greater than 1, optional, ignored if geodesic == False
            The number of neighbors to use in building the geodesic distance matrix. Geodesic distance is constructed by computing the
            K Nearest Neighbors graph for the input dataset, then constructing all pairwise distances using the geodesic distance, i.e.
            the number of edges in a shortest path between two points on the graph.

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        Returns
        =======

        model : :class:`slicematrixIO.manifolds.Isomap`

        """
        return Isomap(dataset = dataset,
                      D = D,
                      K = K,
                      name = name,
                      pipeline = pipeline,
                      client   = self.client)

    # graphs ##################################################################################################################################################################
    def MinimumSpanningTree(self, dataset = None, corr_method = "pearson", name = None, pipeline = None):
        """ 
        Create a Minimum Spanning Tree graph model

        MST models transform the input dataset into a distance matrix then construct a graph with the shortest possible total
        distance which visits all nodes without cycling (i.e. it creates a tree)

        In particular, this model constructs the graph using the correlation matrix. For more flexible options in creating a 
        MST graph, use slicematrixIO.matrix_models.MatrixMinimumSpanningTree in combination with a distance matrix

        Parameters
        ==========

        dataset : pandas.DataFrame
            Input DataFrame. shape = (n_rows, n_features) where each row is a data point and the columns are numeric features

        corr_method : string ["pearson" | "spearman" | "kendall" ]
            Which method should we use for computing the correlation matrix?

            "pearson" : use the Pearson correlation coefficient

            "spearman" : use Spearman's rho

            "kendall" : use Kendall's tau

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        Returns
        =======

        model : :class:`slicematrixIO.graphs.MinimumSpanningTree`

        """
        return MinimumSpanningTree(dataset = dataset,
                                   corr_method = corr_method, 
                                   name = name,
                                   pipeline = pipeline,
                                   client   = self.client)
    
    def CorrelationFilteredGraph(self, dataset = None, K = 3, name = None, pipeline = None):
        """ 
        Create a Correlation Filtered Graph

        CFG are similar to MST's, in that both graph's begin with a distance matrix, but whereas 
        MST's are limited to constructing a tree, CFG's draw links between a node and its closests K
        neighbors based on correlation distance. CFG's are like KNN networks, but optimized for 
        using correlation distance. 

        Parameters
        ==========

        dataset : pandas.DataFrame
            Input DataFrame. shape = (n_rows, n_features) where each row is a data point and the columns are numeric features

        K : integer greater than 1, optional
            The number of nearest neighbors to use for constructing the CFG

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        Returns
        =======

        model : :class:`slicematrixIO.graphs.CorrelationFilteredGraph`

        """
        return CorrelationFilteredGraph(dataset = dataset,
                                        K = K,
                                        name = name,
                                        pipeline = pipeline,
                                        client   = self.client)

    def NeighborNetworkGraph(self, dataset = None, K = 3, kernel = "euclidean", name = None, pipeline = None):
        """ 
        Create a K Nearest Neighbor Graph for the given dataset

        Parameters
        ==========

        dataset : pandas.DataFrame
            Input DataFrame. shape = (n_rows, n_features) where each row is a data point and the columns are numeric features

        K : integer greater than 1, optional
            The number of nearest neighbors to use for constructing the CFG

        kernel : string, optional
            The distance kernel / metric to use in constructing the distance matrix. Default is euclidean.

        name : string, optional
            The desired name of the model. If None then a random name will be generated

        pipeline : string, optional
            An extant Pipeline to use for model creation. If None then one will be created

        Returns
        =======

        model : :class:`slicematrixIO.graphs.NeighborNetworkGraph`

        """
        return NeighborNetworkGraph(dataset = dataset,
                                    K = K,
                                    kernel = kernel,
                                    name = name,
                                    pipeline = pipeline,
                                    client   = self.client)

################################################################################
# stress tests
#
################################################################################

    def PortfolioStressTest(self, dataset = None, target_col = None, name = None):
        """ 
        Perform a stress test simulation on the dataset, conditional on a movement in the target_col

        Parameters
        ==========

        target_col : string
            Which column will be "given", i.e. which column conditions the movement of the rest of the dataset?

        Returns
        =======

        model : :class:`slicematrixIO.stres_tests.PortfolioStressTest`

        """
        return PortfolioStressTest(dataset = dataset,
                                   target_col = target_col,
                                   name = name,
                                   client   = self.client)


