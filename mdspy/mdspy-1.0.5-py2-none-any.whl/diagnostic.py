#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu May 11 15:17:36 2017

@author: patrice
"""
import matplotlib.pylab as plt
import seaborn as sns
import statsmodels.graphics
import statsmodels.api as sm


def diagnostic(model_fit):

    """
    Diagnostic fonction for SARIMA family models
    
    In theory two assumptions are made when using a SARIMA model for predictions:
        
        1. Normality of the errors
            This can be verified by looking at the qq-plot of the residues
            and by comparing the histogram plus estimaed density graph.
                To be normal like, the KDE and the N(0,1) should be close to 
                each other.
    
        2. Autocorrelation between residues is null
            The Ljunb-Box statistic test when p-value < 0.05 allows us to
            reject the null hypothesis that the autocorrelation is null.
            When p-value > 0.05 for all lag, there is not enough evidence to
            reject the null hypothesis therefore it is possible to go forward.
            WARNING: The key point here is that there is not enough evidence
            therefore, it is not garanteed that the autocorrelation is null.
            
        More information:
            The Correlogram can be used to see what can be improved. If the
            null autocorrelation is not rejected,it should show a white noise
            correlogram (no significant peaks after the first one)
        
            The standardized residual plot should show no seasonality and be
            white noise like.
            
            The summary table shows relevant information also. The coef column
            shows the weight (i.e. importance) of each feature and how each one
            impacts the time series. The P>|z| column informs us of the 
            significance of each feature weight. Here, each weight has a 
            p-value lower or close to 0.05, so it is reasonable to retain all 
            of them in our model. (this paragraph from https://www.digitalocean.com/community/tutorials/a-guide-to-time-series-forecasting-with-arima-in-python-3 )
            
            
    Returns
    --------
    Graph of the Ljung-Box statistic test
    Residuals as a numpy.ndarray

    Parameters
    --------
    model_fit: a model fit from a SARIMAX model
        Example with the following parameters(AR =1, diff = 1, MA = 1) seasonal(AR = 2, diff = 1, MA = 2, period = 7):
            model = sm.tsa.SARIMAX(ts_train, order=(1,1,1),seasonal_order=(2,1,2,7))
            model_fit = model.fit()
    
    """
    #Importing whitegrid seaborn style
    sns.set_style('whitegrid')
    
    #Getting the residuals
    res = statsmodels.tsa.statespace.sarimax.SARIMAXResults.resid(model_fit)

    #Plotting the diagnostic from statsmodels
    model_fit.plot_diagnostics(figsize=(15, 12))
    plt.show()
    
    #Plotting the lunjg-box result
    lb = sm.stats.diagnostic.acorr_ljungbox(res, lags=None, boxpierce=False)
    #print(lb[1])fi
    plt.figure(figsize=(15,4))
    plt.title('p-value for Ljung-Box statistic')
    plt.xlabel('Lag')
    plt.ylabel('p-value')
    dstart = 0
    dend = len(lb[1])
    x = range(0, len(lb[1]))
    plt.scatter(x,lb[1])
    plt.axhline(y=0.05,linestyle = '--',color = 'k',hold=None)
    plt.xlim([dstart,dend])
    plt.ylim([-.1,1])
    plt.show()
    
    #Printing the coefficient table from the summary
    print(model_fit.summary().tables[1])

    
    return res
