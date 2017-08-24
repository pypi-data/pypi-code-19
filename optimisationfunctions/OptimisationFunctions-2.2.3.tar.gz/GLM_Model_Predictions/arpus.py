import numpy as np

def ARPU_numbers_matrix(model, Month = 'March', Year = 2016, No_of_Years = 3, coefficients = None):
    """
    Function that outputs the predicted ARPU Numbers for each month per year for each Tenure band. Each row contains the ARPU
    numbers for 31 Tenure bands for a given month and year.
    
    Parameters:
    -----------
    
    Month: The month of the base case either as the number of the month or the name in quotes
            Default = 'March' or 3
    
    Year: The year of the base case and an integer
            Default = 2016
    
    No_of_Years: The number of years prediction is required
            Default = 3
            
    model: The model object used for prediction
            It is recommended to use the function 'GLM_Model_Build.GLM()'
            
    coefficients: The matrix of coefficients to be used in the prediction
            Default is None
            If Default, the function automatically calculates the model coefficients based on the other parameters
    
    Returns:
    --------
    
    NumPy array (matrix) with the predicted ARPU Numbers
    
    """
    
    months = [(1, 'January'), (2, 'February'), (3, 'March'), (4, 'April'), (5, 'May'), (6, 'June'), (7, 'July'), (8, 'August'), 
              (9, 'September'), (10, 'October'), (11, 'November'), (12, 'December')]
    
    years = np.arange(2012, Year + No_of_Years + 1, 1)
    
    arpus = np.array([[0]*31])
    
    if str(Month) in [months[i][1] for i in range(len(months))]:
        Month = [months[j][1] for j in range(len(months))].index(str(Month)) + 1
    else:
        Month = int(Month)
    
    if coefficients is None:
        coeffs = model_coefficients(model, Year, No_of_Years)
        for year in range(No_of_Years):
            for i in range(len(months)-Month):
                base = base_data_creator(months[Month+i][0], Year + year, No_of_Years)
                arpus = np.concatenate((arpus, [model.predict(coeffs, exog = base)]), axis = 0)
                
            for j in range(Month):
                base = base_data_creator(months[j][0], Year + year + 1, No_of_Years)
                arpus = np.concatenate((arpus, [model.predict(coeffs, exog = base)]), axis = 0)
    else:
        for year in range(No_of_Years):
            for i in range(len(months)-Month):
                base = base_data_creator(months[Month+i][0], Year + year, No_of_Years)
                arpus = np.concatenate((arpus, [model.predict(coefficients, exog = base)]), axis = 0)
                
            for j in range(Month):
                base = base_data_creator(months[j][0], Year + year + 1, No_of_Years)
                arpus = np.concatenate((arpus, [model.predict(coefficients, exog = base)]), axis = 0)
                
    return arpus

def ARPU_numbers(base_arpus, arpu_matrix, Month = 'March', Year = 2016, No_of_Years = 3):
    """
    Function that takes in a matrix of ARPU numbers and outputs a DataFrame with the ARPU numbers 
    for the specified number of years
    
    Parameters:
    -----------
    
    arpu_matrix: The matrix containing the ARPU numbers for the given number of years
    
    Month: The month of the base as either the month name or month number
            Default = 'March'
            
    Year: The year of the base
            Default = 2016
            
    No_of_Years: The number of years from base that predictions are required
            Default = 3
            
    Returns:
    --------
    
    Pandas DataFrame containing the ARPU numbers for given number of years from the base
    
    """
    arpus_df = np.array([base_arpus])
    
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
        
    for i in range(len(arpu_matrix)-2):
        arpus_df = np.vstack([arpus_df, arpu_matrix[i+1]])
        
    for j in range(len(arpus_df)):
        for k in range(j):
            if k < 30:
                arpus_df[j][k] = 0
            
    return pd.DataFrame(np.transpose(arpus_df))#, columns = columns)