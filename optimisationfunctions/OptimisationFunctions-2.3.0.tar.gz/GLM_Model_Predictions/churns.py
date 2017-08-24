import pandas as pd
import numpy as np

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

def model_coefficients(model, Year = 2016, No_of_Years = 3):
    """
    Output the model coefficients for a GLM model object
    
    Parameters
    ----------    
    model: The model to be used
    
    Year: The year of the base case
        Default: 2016
    
    No_of_Years: The number of years coefficients are needed for
        Default: 3
    
    Returns
    -------
    NumPy array containing either the ARPU or churn coefficients
    
    Note that the starting year and number of years must be same as that contained in the base data when predicting
    
    """
    years = np.arange(2012, Year + No_of_Years + 2, 1)
    
    temp = pd.DataFrame(model.fit().params, columns = ['Coefficient'])
    ind = ['Year_' + str(i) for i in years[4:]]
    ind = ind + ['Tenure_01', 'Tenure_31']
    temp2 = pd.DataFrame([0]*len(ind), columns = ['Coefficient'], index = ind)
    temp3 = pd.concat([temp, temp2], axis = 0)
    temp3 = temp3.reindex_axis(sorted(temp3.index), axis = 0)
    
    return np.array(temp3['Coefficient']) 


#function to get the churn percentages
def churn_percentage_matrix(model, Month = 'March', Year = 2016, No_of_Years = 3):
    """
    Note that this function works on a 31 Tenure band base. 
    The source code can be changed to accommodate other requirements
    
    Parameters
    ----------
    
    Month: The number of the base month e.g. 4 or 'April'
            Default = 'March'
    
    Year: The base year
            Default = 2016
    
    No_of_Years: The number of years required for prediction
                    Default = 3
    
    model: The model used to predict churn percentages
    
    Returns:
    -------
    
    NumPy array with the churn percentages per month in row format
    
    """
    #Defining the required variables
    months = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), 
              (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')]
    
    years = np.arange(2012, Year + No_of_Years + 1, 1)
    
    temp_func = lambda x: 1-x
    coefficients = model_coefficients(churn_model, Year = Year, No_of_Years = No_of_Years)
    
    percentage_matrix = np.array([[0]*31])
    
    if str(Month) in [months[i][1] for i in range(len(months))]:
        Month = [months[j][1] for j in range(len(months))].index(str(Month)) + 1
    else:
        Month = int(Month)
    
    for year in range(No_of_Years):
        for i in range(len(months)-Month):
            base = base_data_creator(months[Month+i][0], Year + year, No_of_Years)
            percentage_matrix = np.concatenate((percentage_matrix, [model.predict(coefficients, exog = base)]), axis = 0)
            
        for j in range(Month):
            base = base_data_creator(months[j][0], Year + year + 1, No_of_Years)
            percentage_matrix = np.concatenate((percentage_matrix, [model.predict(coefficients, exog = base)]), axis = 0)
            
    return temp_func(percentage_matrix)

def customers_on_base(base_customers, percentage_matrix, Month = 'March', Year = 2016, No_of_years = 3):
    """
    Function that outputs the number of customers on base after churn for the specified number of years
        Note that this function works on the basis of 31 tenure banda
        
    Parameters:
    -----------
    
    base_customers: List containing the number of customers on base
    
    Month: The number of the month for the base
            Default = 'March'
    
    Year: The base year
            Default = 2016
    
    No_of_Years: The number of years to predict. This needs to be the same as in the matrix
            Default = 3
    
    percentage_matrix: Matrix containing the churn percentages 
    
    Returns:
    --------
    
    Pandas DataFrame containing the number of customers after churns for the specified number of years from the base
    
    """
    years = np.arange(Year, Year + No_of_Years, 1)

    months = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), 
              (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')]
    
    if str(Month) in [months[i][1] for i in range(len(months))]:
        Month = [months[j][1] for j in range(len(months))].index(str(Month)) + 1
    else:
        Month = int(Month)
    
    columns = []
    
    for y in years:
        columns = columns + [str(months[i][1]) + '_' + str(y) for i in range(Month-1, len(months))]
        columns = columns + [str(months[j][1]) + '_' + str(y+1) for j in range(Month-1)]
        
    temp = np.array([base_customers])
    new_row = [0]*31
    
    for i in range(len(percentage_matrix)-2):
        temp = np.vstack([temp, new_row])
        
    for j in range(len(temp)-1):
        for k in range(30):
            if k+1 == 30:
                temp[j+1][k+1] = temp[j][k+1] * percentage_matrix[j+1][k+1] + temp[j][k] * churn_matrix[j+1][k]
            else:
                temp[j+1][k+1] = temp[j][k] * percentage_matrix[j+1][k+1]
                
    return pd.DataFrame(np.transpose(temp), columns = [columns])