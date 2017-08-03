from os import path
import numpy as np

PATH = path.abspath(path.dirname(__file__))

def smallGaussian():
    """
        Relaxed 10 body, gaussian distribution initial conditions.

        `G = 1.0`

        `mass_unit = 1.0`

        Returns:
            np.ndarray: contains points properties.
    """
    return np.genfromtxt(path.join(PATH, "small_size_gaussian2d.dat"))

def mediumGaussian():
    """
        Relaxed 100 body, gaussian distribution initial conditions.

        `G = 1.0`

        `mass_unit = 1.0`

        Returns:
            np.ndarray: contains points properties.
    """
    return np.genfromtxt(path.join(PATH, "medium_size_gaussian2d.dat"))

def largeGaussian():
    return np.genfromtxt(path.join(PATH, "large_size_gaussian2d.dat"))

def twosmallGaussians():
    return np.genfromtxt(path.join(PATH, "two_small_size_gaussian2d.dat"))

def twomediumGaussians():
    return np.genfromtxt(path.join(PATH, "two_medium_size_gaussian2d.dat"))

def twolargeGaussians():
    return np.genfromtxt(path.join(PATH, "two_large_size_gaussian2d.dat"))
