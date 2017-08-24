import pandas as pd
import numpy as np

#the base data creator function
def base_data_creator(Month = 'March', Year = 2016, No_of_Years = 3):
    """
    Function that outpus the required format for model prediction
    
    Parameters
    ----------
    Month: The number or name of the month
        e.g. 2 or February
        Default: 3
    
    Year: The year
            Default: 2016
    
    No_of_Years: The number of years required in the model prediction
            Default: 3
    
    Note that this function assumes that the required number of Tenure bands is 31. 
    This can be changed within the source code.
    This function is independent of the intended model.
    
    Returns
    -------
    DataFrame of dummy variables used to in model prediction
     
    """
    #Defining Variables Required
    tenures = np.arange(1, 32, 1)
    years = np.arange(2012, 2021, 1)
    months = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), 
              (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')]
    
    if str(Month) in [months[i][1] for i in range(len(months))]:
        Month = [months[j][1] for j in range(len(months))].index(str(Month)) + 1
    else:
        Month = int(Month)
        
    
    #The Function
    temp = pd.DataFrame({ 'Month': Month, 'Tenure': tenures, 'Year': Year })
    temp2 = pd.get_dummies(temp, columns = ['Month', 'Tenure', 'Year'])
    if Month < 10:
        temp2 = temp2.rename(columns = { 'Month_' + str(Month): 'Month_0' + str(Month), 
                                        'Tenure_1': 'Tenure_01', 'Tenure_2': 'Tenure_02', 'Tenure_3': 'Tenure_03', 
                                        'Tenure_4': 'Tenure_04', 'Tenure_5': 'Tenure_05', 'Tenure_6': 'Tenure_06', 
                                        'Tenure_7': 'Tenure_07', 'Tenure_8': 'Tenure_08', 'Tenure_9': 'Tenure_09'})
    else:
        temp2 = temp2.rename(columns = {'Tenure_1': 'Tenure_01', 'Tenure_2': 'Tenure_02', 'Tenure_3': 'Tenure_03', 
                                        'Tenure_4': 'Tenure_04', 'Tenure_5': 'Tenure_05', 'Tenure_6': 'Tenure_06', 
                                        'Tenure_7': 'Tenure_07', 'Tenure_8': 'Tenure_08', 'Tenure_9': 'Tenure_09'})
    
    temp3 = pd.DataFrame(pd.DataFrame([[0]*31 for i in range(0, len(months)-1)]).transpose(), columns = 
                         [['Month_0' + str(i) for i in [ 
                             months[i][0] for i in range(len(months)) if months[i][0] != Month and float(months[i][0]) < 10.0]] 
                          + 
                          ['Month_' + str(i) for i in [
                              months[i][0] for i in range(len(months)) if months[i][0] != Month and float(months[i][0]) >= 10.0]]
                         ]).fillna(0).astype(int)
    
    temp4 = pd.DataFrame(pd.DataFrame([[0]*31 for i in range(len(years)-1)]).transpose(), columns = 
                         ['Year_' + str(years[i]) for i in range(len(years)) if years[i] != Year]).fillna(0).astype(int)
    
    temp5 = pd.concat([temp2, temp3, temp4], axis = 1)
    
    return temp5.reindex_axis(sorted(temp5.columns), axis = 1)
   
 