"""low level SliceMatrix-IO API client"""

API_STAGE = "beta"

import pandas as pd
import numpy as np
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import json
import boto3
from StringIO import StringIO
import datetime as dt
import tempfile

region_api_map    = {"us-east-1":      "ud7p0wre43",
                     "us-west-1":      "4u0pr4ljei",
                     "eu-central-1":   "pozdfzsgae",
                     "ap-southeast-1": "gbq29whx4l"}

class ConnectIO():
  """ 
  Low Level Connection to SliceMatrix-IO

  Implements basic interface

  Parameters
  ----------
  api_key : string
      Valid SliceMatrix-IO API Key

  region : string ['us-east-1', 'us-west-1', 'eu-central-1', 'ap-southeast-1']
      Data center of choice. API Key must be valid for that specific data center.
      Latency will be lowest if client is closest to data center.

      'us-east-1': US East Coast Data Center

      'us-west-1': US West Coast Data Center

      'eu-central-1': Continental Europe Data Center

      'ap-southeast-1': South-East Asian Data Center

  Attributes
  ----------
  uploader : object
      Convienence class for uploading data to SliceMatrix-IO

  region : string

  Examples
  --------
  >>> from slicematrixIO.connect import ConnectIO
  >>> io = ConnectIO(api_key)
  >>> io.create_pipeline(...)
  >>> io.run_pipeline(...)
  >>> io.call_model(...)
      
  """
  def __init__(self, api_key, region = "us-east-1"):
    self.api_key  = api_key
    self.region   = region
    self.api      = region_api_map[region]
    self.uploader = Uploader(api_key, self.region, self.api)

  def put_df(self, name, dataframe):
    """ 
    Upload the DataFrame with desired name and get response (success | failure)

    Parameters
    ----------
    name : string
        The desired name of the DataFrame

    dataframe: pandas.DataFrame
        The DataFrame for uploading to the SliceMatrix-IO backend

    Returns
    -------
    response : dict
    """
    self.uploader.put_df(name, dataframe)

  def list_files(self):
    """ 
    Get a list of the files previously uploaded

    Returns
    -------
    file_list : list
    """
    return self.uploader.list_files()  

  def create_pipeline(self, name, type, params = {}):
    """ 
    Create a new Analytical Pipeline for distributed computation

    Parameters
    ----------
    name : string
        The desired name of the new Pipeline

    type : string [ 'raw_isomap' | 'raw_mst' | 'raw_lle' | 'raw_cfg' | 'raw_kde' | 'raw_knn_net' | 'raw_knn_classifier' | 'raw_knn_regressor' | 'raw_kpca' | 'raw_krr' | 'raw_rfr' | 'raw_laplacian' | 'raw_pnn' | 'matrix_mst' | 'matrix_kpca' | 'matrix_agg' | 'kalman_ols' | 'basic_a2d' | 'isolation_forest' | 'dist_matrix']
        The type of the Pipeline

    params: dict
        Any type specific parameters to the Pipeline in the key/val dictionary

    Returns
    -------
    response: dict

    Notes
    -----
    The basic structure of computation in SliceMatrix-IO starts with the Pipeline.
    
    Pipelines can be thought of as analytical assembly lines, running code which
    transforms a dataset from raw input data into a meaningful machine learning
    model. Each pipeline can be reused to process multiple datasets. Pipelines can
    also be run in parallel.  
    """
    url = 'https://' + self.api + '.execute-api.' + self.region + '.amazonaws.com/' + API_STAGE + '/pipelines/create'
    headers = {'x-api-key': self.api_key, 'Content-Type': 'application/json'}
    body    = {'name': name, 'type': type, 'params': params}
    r = requests.post(url, verify = False, headers = headers, data=json.dumps(body))
    return json.loads(r.text)
  
  def run_pipeline(self, name, model, type = None, dataset = None, matrix_name = None, matrix_type = None, X = None, Y = None, extra_params = {}, memory = "large"):
    """ 
    Run a Pipeline with the given dataset

    Parameters
    ----------
    name : string
        The name of the target Pipeline

    model : string
        The desired name of the model

    type : string [ 'raw_isomap' | 'raw_mst' | 'raw_lle' | 'raw_cfg' | 'raw_kde' |
                    'raw_knn_net' | 'raw_knn_classifier' | 'raw_knn_regressor' |
                    'raw_kpca' | 'raw_krr' | 'raw_rfr' | 'raw_laplacian' |
                    'raw_pnn' | 'matrix_mst' | 'matrix_kpca' | 'matrix_agg' |
                    'kalman_ols' | 'basic_a2d' | 'isolation_forest' | 'dist_matrix']
        The type of the Pipeline

    dataset : string 
        The name of the dataset to run through the Pipeline
    
    matrix_name : string
        The name of the matrix model to run through the Pipeline (for Matrix Models)

    matrix_type : string [ 'dist_matrix' | 'matrix_agg' ]  
        The type of matrix

    X : string
        The name of the X input (for multi-output regression models)

    Y : string
        The name of the Y input (for multi-output regression models)

    extra_params : dict
        Any extra parameters to pass as key / values to the Pipeline

    memory: string [ 'large']
        The size of the container (always set to large for beta)

    Returns
    -------
    response : dict

    Notes
    -----
    This is a very flexible function for running any Pipeline in the SliceMatrix-IO platform. 

    Most Pipelines will take a single dataset name as input (such as raw_isomap and raw_knn_classifier),
    whereas others will have more complex inputs. Matrix Models will take matrix_name and matrix_type
    parameters and regression models will require the names of input (X) and output (Y) training sets.

    """
    url = 'https://' + self.api + '.execute-api.' + self.region + '.amazonaws.com/' + API_STAGE + '/pipelines/run'
    headers = {'x-api-key': self.api_key, 'Content-Type': 'application/json'}
    body = {'name': name, 'model': model, 'memory': memory, 'type': type}
    if dataset != None:
        body['dataset']     = dataset
    else:
        body['dataset']     = ""
    if matrix_name != None and matrix_type != None:
        body['matrix_name'] = matrix_name
        body['matrix_type'] = matrix_type
    if X != None and Y != None:
        body['X'] = X
        body['Y'] = Y
    for param_key in extra_params.keys():
      body[param_key] = extra_params[param_key]
    #print body
    r = requests.post(url, verify = False, headers = headers, data=json.dumps(body))
    return json.loads(r.text)

  def call_model(self, model, type, method, extra_params = {}, memory = "large"):
    """ 
    Remotely call a method in a machine learning model

    Parameters
    ----------
    model : string
        The name of the model 

    type : string
        The type of the model

    method: string
        The name of the model method to call remotely. Acceptable inputs vary by Pipeline type. See Pipeline docs for more information

    extra_params : dict
        Any extra parameters to pass as key / values to the Pipeline

    memory: string [ 'large']
        The size of the container (always set to large for beta)

    Returns
    -------
    model_output: dict
    
    Notes
    -----
       

    """
    url = 'https://' + self.api + '.execute-api.' + self.region + '.amazonaws.com/' + API_STAGE + '/models/call'
    headers = {'x-api-key': self.api_key, 'Content-Type': 'application/json'}
    body    = {'model': model, 'type': type, 'function': method, 'extra_params': extra_params, 'memory': memory}
    r = requests.post(url, verify = False, headers = headers, data=json.dumps(body))
    #print r.text
    return json.loads(r.text)#[method]

  
class Uploader():
  """ 
  Object to handle uploads to SliceMatrix-IO backend

  Parameters
  ----------
  api_key : string
     Valid SliceMatrix-IO API Key

  region : string ['us-east-1', 'us-west-1', 'eu-central-1', 'ap-southeast-1']
      Data center of choice. API Key must be valid for that specific data center.
      Latency will be lowest if client is closest to data center.

      'us-east-1': US East Coast Data Center

      'us-west-1': US West Coast Data Center

      'eu-central-1': Continental Europe Data Center

      'ap-southeast-1': South-East Asian Data Center

  api : string 
      API ID

  Examples
  --------
  >>> uploader = Uploader(api_key)
  >>> uploader.put_df("my_dataframe", df)   

  """
  def __init__(self, api_key, region, api):
    self.api_key = api_key
    self.region  = region
    self.api     = api
	
  def get_upload_url(self, file_name):
    url = 'https://' + self.api + '.execute-api.' + self.region + '.amazonaws.com/' + API_STAGE + '/datasets/authorize'
    headers = {'x-api-key': self.api_key, 'Content-Type': 'application/json'}
    r = requests.post(url, verify = False, headers = headers, data = json.dumps({'name':file_name}))
    return json.loads(r.text)

  def put_df(self, name, df):
    """ 
    Upload the DataFrame with desired name and get response (success | failure)

    Parameters
    ----------
    name : string
        The desired name of the DataFrame

    df: pandas.DataFrame
        The DataFrame for uploading to the SliceMatrix-IO backend

    Returns
    -------
    response : dict
    """
    post = self.get_upload_url(name)
    files = {"file": df.to_csv()}
    response = requests.post(post["url"], data=post["fields"], files=files)
    return response
	
  def list_files(self): 
    """ 
    Get a list of the files previously uploaded

    Returns
    -------
    file_list : list
    """
    url = 'https://' + self.api + '.execute-api.' + self.region + '.amazonaws.com/' + API_STAGE + '/datasets'
    headers = {'x-api-key': self.api_key}
    r = requests.get(url, verify = False, headers = headers)
    return json.loads(r.text)

