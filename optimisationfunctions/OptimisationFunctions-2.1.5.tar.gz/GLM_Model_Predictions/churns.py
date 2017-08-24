import pandas as pd
import numpy as np

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
    
    percentage_matrix = np.array([[0]*31])
    
    coefficients = model_coefficients(model, Year, No_of_Years)
    
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