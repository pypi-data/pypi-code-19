# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 01:57:32 2017

@author: Yuki
"""

from JupyterHuck.MyFunctions import defferentiate
import pandas as pd
import numpy as np

def test_defferentiate(data_file='C:\\Users\\Yuki\\Dropbox\\python\\150t_calibration\\raw_data\\Pb_AC_chi\\170629_pressure_calibration_low_Pb_Ac_chi_11.13kHz_warming.csv'):
    '''dy/dxが全ての点で数値を返すかチェック'''
    ndata=pd.read_csv(data_file,sep='\t',comment='#')
    x=ndata[ndata.columns[1]]
    y=ndata[ndata.columns[1]]
    result=defferentiate(x,y)
    df=result['df']
    for x in df:
        assert np.isnan(x)
            
    
