""" 
Classes for creating network graph models
"""
from core import BasePipeline
from utils import rando_name
from uuid import uuid4
import pandas as pd

#################################################################################################################################################################
class MinimumSpanningTreePipeline(BasePipeline):
    """ 
    Create a Pipeline for training :class:`.MinimumSpanningTree` models.

    Parameters
    ==========

    name : string
        The desired name of the Pipeline.

    corr_method : string ["pearson" | "spearman" | "kendall" ]
        Which method should we use for computing the correlation matrix?
 
       "pearson" : use the Pearson correlation coefficient

       "spearman" : use Spearman's rho

       "kendall" : use Kendall's tau

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========

    Create a Pipeline for training multiple :class:`.MinimumSpanningTree` models

    >>> io = ConnectIO(api_key)
    >>> pipe = MinimumSpanningTreePipeline(client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())

    """
    def __init__(self, name, corr_method = "pearson", client = None):
        params = {"corr_method": corr_method}
        BasePipeline.__init__(self, name, "raw_mst", client, params)

    def run(self, dataset, model):
        return BasePipeline.run(self, dataset = dataset, model = model)

class MinimumSpanningTree():
    def __init__(self, dataset = None, name = None, pipeline = None, corr_method = "pearson", client = None):
        self.client  = client
        self.type     = "raw_mst"
        if dataset is not None:
            self.__full_init__(dataset, name, pipeline, corr_method, client)
        else:
            self.__lazy_init__(name)

    def __full_init__(self, dataset, name = None, pipeline = None, corr_method = "pearson", client = None):
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.pipeline = pipeline
        self.corr_method = corr_method
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = MinimumSpanningTreePipeline(pipeline_name, corr_method, client)
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

    def rankLinks(self):
        """ 
        Rank the links by weight, if applicable

        Returns
        =======

        links : dict
            dictionary of links with associated weight, if applicable

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
        Get a list of all the edges in the graph model

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
            The name of the target node we want to find the neighbors (shared edges)

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


#################################################################################################################################################################
class CorrelationFilteredGraphPipeline(BasePipeline):
    """ 
    Create a Pipeline for training :class:`.CorrelationFilteredGraph` models.

    CFG's are similar to MST's, in that both graph's begin with a distance matrix, but whereas
    MST's are limited to constructing a tree, CFG's draw links between a node and its closests K
    neighbors based on correlation distance. CFG's are like KNN networks, but optimized for
    using correlation distance.

    Parameters
    ==========

    name : string
        The desired name of the Pipeline.

    K : integer greater than 1, optional
        The number of nearest neighbors to use for constructing the CFG

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========

    Create a Pipeline for training multiple :class:`.CorrelationFilteredGraph` models

    >>> io = ConnectIO(api_key)
    >>> pipe = CorrelationFilteredGraphPipeline(client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())
    """
    def __init__(self, name, K = 3, client = None):
        params = {"K": K}
        BasePipeline.__init__(self, name, "raw_cfg", client, params)

    def run(self, dataset, model):
        return BasePipeline.run(self, dataset = dataset, model = model)

class CorrelationFilteredGraph():
    def __init__(self, dataset = None, name = None, pipeline = None, K = 3, client = None):
        self.client  = client
        self.type     = "raw_cfg"
        if dataset is not None:
            self.__full_init__(dataset, name, pipeline, K, client)
        else:
            self.__lazy_init__(name)

    def __full_init__(self, dataset, name = None, pipeline = None, K = 3, client = None):
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.pipeline = pipeline
        self.K        = K
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = CorrelationFilteredGraphPipeline(pipeline_name, K, client)
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

    def rankLinks(self):
        """ 
        Rank the links by weight, if applicable

        Returns
        =======

        links : dict
            dictionary of links with associated weight, if applicable

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
        Get a list of all the edges in the graph model

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
            The name of the target node we want to find the neighbors (shared edges)

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

#################################################################################################################################################################
class NeighborNetworkGraphPipeline(BasePipeline):
    """ 
    Create a Pipeline for training :class:`.NeighborNetworkGraph` models.

    Parameters
    ==========

    name : string
        The desired name of the Pipeline.

    K : integer greater than 1, optional
        The number of nearest neighbors to use for constructing the CFG

    kernel : string, optional
        The distance kernel / metric to use in constructing the distance matrix. Default is euclidean.

    client : :class:`slicematrixIO.connect.ConnectIO`
        Low level client for dispatching requests to SliceMatrix-IO

    Returns
    =======

    response : dict
        success or failure response to Pipeline creation request

    Examples
    ========

    Create a Pipeline for training multiple :class:`.NeighborNetworkGraph` models

    >>> io = ConnectIO(api_key)
    >>> pipe = NeighborNetworkGraphPipeline(K = 5, client = io)
    >>> for dataframe in dataframes:
    >>>     current_model = pipe.run(dataset = dataframe, name = slicematrixIO.utils.rando_name())

    """
    def __init__(self, name, K = 3, kernel = "euclidean", client = None):
        params = {"K": K, 
                  "kernel": kernel}
        BasePipeline.__init__(self, name, "raw_knn_net", client, params)

    def run(self, dataset, model):
        return BasePipeline.run(self, dataset = dataset, model = model)

class NeighborNetworkGraph():
    def __init__(self, dataset = None, name = None, pipeline = None, K = 3, kernel = "euclidean", client = None):
        self.client  = client
        self.type     = "raw_knn_net"
        if dataset is not None:
            self.__full_init__(dataset, name, pipeline, K, kernel, client)
        else:
            self.__lazy_init__(name)

    def __full_init__(self, dataset, name = None, pipeline = None, K = 3, kernel = "euclidean", client = None):
        if name == None:
            name = rando_name()
        self.name     = name
        self.dataset  = dataset
        self.pipeline = pipeline
        self.K        = K
        if self.pipeline == None:
            pipeline_name = rando_name()
            self.pipeline = NeighborNetworkGraphPipeline(pipeline_name, K, kernel, client)
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

    def rankLinks(self):
        """ 
        Rank the links by weight, if applicable

        Returns
        =======

        links : dict
            dictionary of links with associated weight, if applicable

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
        Get a list of all the edges in the graph model

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
            The name of the target node we want to find the neighbors (shared edges)

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


