import pandas as pd
import numpy as np


def sayhello():
    print('hello')


def randDataFrame(m, n):
    return pd.DataFrame(np.random.randn(m, n))
