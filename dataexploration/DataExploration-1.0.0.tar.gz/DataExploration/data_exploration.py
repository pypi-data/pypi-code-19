
# coding: utf-8

# # Find columns with specfied percentage of missing values 
# 
# 1. It takes the dataframe and the percent value
# 2. It returns all the columns which missing values greater than or equal to particular percent
# 3. Those columns can be removed from analysis
# 4. You can use it to find columns with at least one missing value with the argument 1/data.shape[0]

# In[1]:

def percent_missing_value(data, percent):
    #columns = row.columns
    #notnullvalues = [1 for col in columns if(row[col].isnull()]:
    actual_percent = 100 - percent
    notnullcount = data.count()
    columns = data.columns
    null_columns = []
    total_values = data.shape[0]
    for col in columns:
        notnullratio = notnullcount[col] / data.shape[0]
        notnull_percent = notnullratio * 100
        if(notnull_percent <= actual_percent):
            null_columns.append(col)
    return null_columns
      


# # Find percent of missing values against each column in the dataframe
# 
# It returns the dataframe listing the column name and the correponding percent of missing values

# In[2]:

def percent_missing_columnwise(data):
    notnullcount = data.count()
    percent_values = [(1 - col/data.shape[0])*100 for col in notnullcount]
    return pd.DataFrame(percent_values, index=data.columns)


# # Find DataType of each column
# 
# 1. Return the datatype of each column in the list of columns passed

# In[3]:

def get_data_type(data, columns):
    dtypes = []
    for col in columns:
        dtypes.append(data[col].dtype)
        
    return pd.DataFrame(dtypes, index = columns)


# # Find the numeric and non numeric columns from the dataframe

# In[4]:

def find_numeric_columns(data, columns):
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    numeric_columns = []
    for col in columns:
        if(data[col].dtype in numerics):
            numeric_columns.append(col)
    return numeric_columns


# In[5]:

def find_non_numeric_columns(data, columns):
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    non_numeric_columns = []
    for col in columns:
        if(data[col].dtype not in numerics):
            non_numeric_columns.append(col)
    return non_numeric_columns


# # Check if column has missing value

# In[6]:

def check_missing_value_any(data, column):
    return data[column].isnull().any()


# # Check if column has all the missing values

# In[7]:

def check_missing_value_all(data, column):
    return data[column].isnull().all()


# # Check if the list of columns have missing value. If yes, return the list of columns

# In[8]:

def check_missing_value_columns(data, columns):
    missing_columns = []
    for col in columns:
        if(data[col].isnull().any()):
            missing_columns.append(col)
    return missing_columns


# # Fill the numeric missing values in columns
# 
# 1. Numeric missing values can be filled with the median values.
# 

# In[9]:

def fill_missing_value_numeric(data, numeric_columns):
    for col in numeric_columns:
        data[col]= data[col].fillna(data[col].median())
    return data


# In[10]:

# Fill non numeric missing values in columns


# In[11]:

# Fill the non numeric missing values in columns
def fill_missing_value_non_numeric(data, numeric_columns):
    for col in numeric_columns:
        data[col] = data[col].fillna(data[col].value_counts().idxmax())
    return data
    


# # Find the highly correlated features

# In[12]:

def find_highly_correlated_features(data, columns, threshold):
    corr_list = []
    correlation = data.corr()
    for index, row in correlation.iterrows():
        for col in columns:
            if((row[col] > threshold and row[col] <1) or (row[col] < -threshold and row[col] > -1)):
                corr_list.append([row[col],index,col])
    s_corr_list = sorted(corr_list,key=lambda x: -abs(x[0]))   
    return s_corr_list


# # Remove Skewness in the Data

# In[13]:

# Skew Correction
#log1p function applies log(1+x) to all elements of the column
import numpy as np
def remove_skewness(data, param):
    skew = data.skew()

    skewedfeatures = [[s, skew[s]] for s in skew.index if(skew[s] > param)]
    for skf in skewedfeatures:
        data[skf[0]] = np.log1p(data[skf[0]])
    return data


# # Non numeric data to numeric/One hot Encoding

# In[14]:

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
def cateogorical_to_numeric(data, labels, size):
    final_df = data
    columns = data.columns
    for i in range(0, size):
        label_encoder = LabelEncoder()
        label_encoder.fit(labels[i])
        feature = label_encoder.transform(data.iloc[:,i])
        feature = feature.reshape(data.shape[0], 1)
        #One hot encode
        onehot_encoder = OneHotEncoder(sparse=False,n_values=len(labels[i]))
        feature = onehot_encoder.fit_transform(feature)
        temp=pd.DataFrame(feature,columns=[columns[i] +"_"+str(j) for j in label_encoder.classes_])
        temp=temp.set_index(data.index.values)
    
        final_df=pd.concat([final_df,temp],axis=1)
    return final_df


# # Feature Scaling/Normalization/Min-Max Scaling and Standardization

# Some examples of algorithms where feature scaling matters are:
# 
# k-nearest neighbors with an Euclidean distance measure if want all features to contribute equally
# k-means (see k-nearest neighbors)
# logistic regression, SVMs, perceptrons, neural networks etc. if you are using gradient descent/ascent-based optimization, otherwise some weights will update much faster than others
# linear discriminant analysis, principal component analysis, kernel principal component analysis since you want to find directions of maximizing the variance (under the constraints that those directions/eigenvectors/principal components are orthogonal); you want to have features on the same scale since you’d emphasize variables on “larger measurement scales” more. There are many more cases than I can possibly list here … I always recommend you to think about the algorithm and what it’s doing, and then it typically becomes obvious whether we want to scale your features or not.

# # “Standardization or Min-Max scaling?
# 
# Standardization or Min-Max scaling?” - There is no obvious answer to this question: it really depends on the application.
# 
# For example, in clustering analyses, standardization may be especially crucial in order to compare similarities between features based on certain distance measures. Another prominent example is the Principal Component Analysis, where we usually prefer standardization over Min-Max scaling, since we are interested in the components that maximize the variance (depending on the question and if the PCA computes the components via the correlation matrix instead of the covariance matrix; but more about PCA in my previous article).
# 
# However, this doesn’t mean that Min-Max scaling is not useful at all! A popular application is image processing, where pixel intensities have to be normalized to fit within a certain range (i.e., 0 to 255 for the RGB color range). Also, typical neural network algorithm require data that on a 0-1 scale.

# In[15]:

# get_ipython().system('jupyter nbconvert --to script data_cleaning_processing.ipynb')


# In[ ]:



