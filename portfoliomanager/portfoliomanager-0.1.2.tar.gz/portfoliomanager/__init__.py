#*********************************************************************
 # File Name: portfolio_manager.py
 # Author: James Whiteley IV
 # Creation Date: 2016-12-14
 # Description: This program is used to track a portfolio against IVV
 #  no cash, no buying, no selling
 # Copyright 2017 James Whiteley IV
 # *******************************************************************
import pandas_datareader.data as web
import matplotlib.pyplot as plt 
import datetime as dt
import numpy as np 
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.dates as mdates
import pandas as pd
from dateutil.relativedelta import relativedelta
import investmentutility as inv

class Portfolio:

    def __init__(self, tickers, start, end, name, start_value=100000):
        '''
        Initialize Portfolio object
        name used for pdf name
        portfolio_start/end is datetime objects
        tickerss: list of strings
        start_value(optional): default to 100,000.  This is the start value of the investments.
        '''
        self.name = name
        self.portfolio_start = start
        self.portfolio_end = end
        self.tickers = tickers
        self.start_value = start_value

    def getChgFrame(self):
        '''
        Equally weights each investment and invests in each.  Returns the cumulative values as 
        a series.
        '''
        f = web.DataReader(self.tickers, "google", self.portfolio_start, self.portfolio_end)
        df = f.loc['Close']
        df = df.pct_change() + 1
        num_investments = len(df.columns)
        invest_in_each = self.start_value / num_investments
        df.ix[0,:] = invest_in_each
        df = df.fillna(1)
        df.ix[1:] = df.ix[1:].cumprod() * invest_in_each
        df['value'] = df.sum(axis=1)
        return df['value']

    def getBenchmark(self):
        '''
        Returns a series of how your starting value turned out if you invested buy and
        hold in IVV etf.
        '''
        f = web.DataReader("IVV", "google", self.portfolio_start, self.portfolio_end)
        df = f['Close']
        df = df.pct_change() + 1
        df.iloc[0] = self.start_value
        df.iloc[1:] = df.iloc[1:].cumprod() * self.start_value
        return df
    
    def pltPort(self):
        '''
        Uses the plotter utility function from pandas_util.
        Plots IVV vs. portfolio with statistics of each.
        '''
        print "Plotting", self.name, "vs IVV..."
        port = self.getChgFrame()
        bench = self.getBenchmark()
        title = inv.stats(port, bench)
        inv.plotter(port, self.name, bench, title, yLabel='Price')


