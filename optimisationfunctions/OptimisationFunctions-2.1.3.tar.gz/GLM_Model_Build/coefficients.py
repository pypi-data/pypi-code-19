#function to get the model coefficients
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
