""" 
Useful utility functions
"""
from uuid import uuid4
import numpy as np

def rando_name(type = "short"):
    """ 
    Generate a random name string

    Longer name decreases chance of overwrite collision

    Parameters
    ==========

    type : string ["short" | "long"]
        Whether to create a long or short name

    Returns
    =======

    name : string
        Random name
    """
    name = str(uuid4())
    if type == "short":
        return name.split("-")[-1]
    else:
        return name.replace("-", "")


def r_squared(Y_hat, Y):
    """ 
    Get the coefficient of determination, or r-squared, for a given prediction versus its ground truths

    Parameters
    ==========

    Y_hat : pandas.DataFrame
        The predicted values DataFrame

    Y : pandas.DataFrame
        The actual values DataFrame

    Returns
    =======

    r_2 : float
        The r-squared value
    """
    res = np.sum(np.square(np.subtract(Y.values, Y_hat.values))) #np.sum(np.square(Y.values - Y_hat.values))
    tot = np.sum(np.square(np.subtract(Y.values, np.mean(Y.values))))
    #print res, tot
    return 1. - ( res / tot )
