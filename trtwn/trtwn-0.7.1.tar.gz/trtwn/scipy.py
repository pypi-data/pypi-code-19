import numpy as np
from scipy.optimize import curve_fit
from trtwn.math import gauss

def fit_gauss(x, y):

    # Find starting parameters
    _sum = np.sum(y)
    peak = np.max(y)
    mean = np.sum(x * y)/_sum
    sigma = np.sqrt(sum(y*(x-mean)**2)/_sum)
    offset = y[0]

    # Fit gaussian curve to y
    return curve_fit(gauss, x, y, p0=[peak,mean,sigma,offset])