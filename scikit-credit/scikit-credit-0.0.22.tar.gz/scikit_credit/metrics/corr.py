__author__ = 'jiyue'
import numpy as np

# 相关性分析
def compute_corr(df, corr_value):
    cor = df.corr()
    cor.loc[:, :] = np.tril(cor, k=-1)  # below main lower triangle of an array
    cor = cor.stack()
    print cor[(cor > corr_value) | (cor < -corr_value)]
