import numpy as np

def gauss(x, A, mu, sigma, c):
    return A/(sigma * np.sqrt(2 * np.pi)) * np.exp(-(x - mu)**2 / (2 * sigma**2)) + c
