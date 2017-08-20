 # *********************************************************************
 # Author: James Whiteley IV
 # Creation Date: 2017-07-13
 # Description: This program includes functions that are quite handy when 
 # writing investment programs with pandas. 
 # Copyright 2017 James Whiteley IV
 # *******************************************************************
import pandas as pd
import pandas_datareader.data as web
import numpy as np
import datetime as dt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
import math

def print_all(df):
    '''
    prints all rows of a dataframe
    Params:
        df: dataframe to print
    '''
    pd.set_option('display.max_rows', len(df))
    print(df)
    pd.reset_option('display.max_rows')


def mean_list(l):
    '''
    Returns:
        average of all values in a list
    Params:
        l: list of floats to be averaged
    '''
    numerator = 0
    denomenator = len(l)
    for x in l:
        numerator += x
    return numerator / denomenator


def date_curr_first(date):
    '''
    Returns:
        changes a date to the first day of the CURRENT month
    example:
        date passed is dt.date(2010, 5, 14), it will return dt.date(2010, 5, 1)
        since its the last usable date's key.
    '''
    year = date.year
    month = date.month
    day = 1 
   
    return dt.date(year, month, day)


def date_next_first(date):
    '''
    Returns:
        changes a date to the first day of the  NEXT month
    example:
        date passed is dt.date(2010, 5, 14), it will return dt.date(2010, 6, 1)
    '''
    year = date.year
    month = date.month
    day = 1 

    if month == 12:
        month = 1
        year = year + 1
    else:
        month = month + 1
   
    return dt.date(year, month, day)


def risk_free_rate():
    '''
    Returns:
        current 3mo treasury yield
    '''
    end = dt.date.today()
    start = end - relativedelta(months=1)
    f = web.DataReader("DTB3", "fred", start, end)
    rate = f.ix[-1, 0]
    return rate



def stock_data(ticker, start=False, end=dt.date.today(), selection=False):
    '''
    Returns:
        *uses Google Finance.
        Series/df of prices for specified ticker.
    Params:
        ticker: in string format:  "AAPL" 
        start(optional): start date of series in datetime format.
        end(optional): end date of series in datetime format.   
        automatically set end to current date and start to one year before.
        selection(optional): pass in "Open", "High", "Low", "Close", or "Volume"
            to select a specific column and return that series.
    '''
    params = ['Open', 'High', 'Low', 'Close', 'Volume']

    if not start:
        start = end - relativedelta(years=1)

    f  = web.DataReader(ticker, "google", start, end)

    if selection in params:
        f = f.ix[:, selection]

    return f


def cagr(ser):
    '''
    Returns:
        Compound annual growth rate of a series in float format: 4.012311.
    Params:
        ser: series to calculate cagr for.
    '''
    f = ser.copy()
    days = len(f)
    annualized_days = days / 252.00  #252 trading days per year
    base = f.ix[-1] / f.ix[0]
    exp = 1.00 / annualized_days
    cagr = (base**exp - 1.00) * 100

    return cagr


def total_return(ser):
    '''
    Returns:
        Total percent change of a series in float format: 11.23351.
    Params:
        ser: series of prices to calculate total return.
    '''
    f = ser.copy()
    ret = (f.ix[-1] / f.ix[0] - 1) * 100.0

    return ret


def max_dd(ser, lookback=False):
    '''
    Returns:
        Maximum drawdown in percentage of series in float format: -12.013801.
    Params: 
        ser: Pandas series of prices  
        lookback(optional): number of rows to lookback starting from bottom (most recent date)
        must be less than length of series.  If left blank, calculated drawdown
        on entire series.
    '''
    f = ser.copy()
    if lookback:
        f = f.iloc[-lookback:]
    rolling_max = f.expanding(min_periods=1).max()
    dd = (f / rolling_max - 1) * 100.0
    dd = dd.min()

    return dd


def max_dd_date(ser, lookback=False):
    '''
    Returns:
        Date of maximum drawdown of a series of prices.
    Params: 
        ser: Pandas series of floats  
        lookback(optional): number of rows to lookback starting from bottom
        must be less than length of series.  If left blank, calculated drawdown
        on entire series.
    '''
    f = ser.copy()
    if lookback:
        f = f.iloc[-lookback:]

    rolling_max = f.expanding(min_periods=1).max()
    dd = (f / rolling_max - 1) * 100.0
    date = dd.idxmin()
    date = date[0]

    return date


def std_dev(ser, period=False, neg=False):
    '''
    Returns:
        Standard deviation of daily returns in format: 1.23 as in 1.23%.
    Params:
        ser: series of prices to calculate standard deviation on.
        period(optional): # of days to lookback for std calculation. default is 63 days (3 months)
        neg(optional): True if you want to calculate standard deviation only on negative returns.
    '''
    if period:
        f = ser.ix[-period:].pct_change()
    else:
        f = ser.pct_change()

    if neg:
        f = f[f < 0]

    return f.std() * 100.0


def annualized_sortino(ser):
    '''
    Returns:
        Annualized sortino ratio for the series of prices passed.
    Params:
        ser: series to calculate ratio on.
    '''
    dev = std_dev(ser, neg=True) 
    dev = math.sqrt(252) * dev  # annualize the standard deviation
    sortino = (cagr(ser) - (4 * risk_free_rate())) / dev # 4 * 3mo risk free gets annual return

    return sortino


def annualized_sharpe(ser):
    '''
    Returns:
        Annualized sharpe ratio for the series of prices passed.
    Params:
        ser: series to calculate ratio on.
    '''
    dev = std_dev(ser) 
    dev = math.sqrt(252) * dev  # annualize the standard deviation
    sharpe = (cagr(ser) - (4 * risk_free_rate())) / dev # 4 * 3mo risk free gets annual return

    return sharpe


def stats(ser, ser2=[]):
    '''
    Returns:
        a string that includes max dd, cagr, sortino, sharpe, and total return.
    Params:
        ser: series of prices to perform data calculations on.
        ser2(optional): adds benchmark stats. 
    '''
    dd = "max dd: " + str(round(max_dd(ser), 2)) + "% "
    cagr1 = "cagr: " + str(round(cagr(ser), 2)) + "% "
    tot_ret = "Port: " + str(round(total_return(ser), 2)) + "% "
    sortino = "Sortino: " + str(round(annualized_sortino(ser), 2)) + " "
    sharpe = "Sharpe: " + str(round(annualized_sharpe(ser), 2)) + " "
    title = tot_ret + cagr1 + sortino + sharpe + dd 
    if len(ser2) > 0:
        tot_ret2 = "Bench: " + str(round(total_return(ser2), 2)) + "% "
        cagr2 = "cagr: " + str(round(cagr(ser2), 2)) + "% "
        dd2 = "max dd: " + str(round(max_dd(ser2), 2)) + "% "
        sortino2 = "Sortino: " + str(round(annualized_sortino(ser2), 2)) + " "
        sharpe2 = "Sharpe: " + str(round(annualized_sharpe(ser2), 2)) + " "
        title = title + "\n" + tot_ret2 + cagr2 + sortino2 + sharpe2 +  dd2

    return title


def rel_strength(ticker1, ticker2, start, end):
    '''
    Returns:
        A Pandas series comparing two tickers' relative strength using 'Close' price.
        If series is increasing, ticker1's relative strength is increasing
        vs. ticker2.   

    Params:
        ticker1: first ticker
        ticker2: second ticker
        start: start date of series
        end: end date of series
    '''
    f = stock_data(ticker1, start, end, 'Close')
    f = f.rename(columns={'Close':ticker1})

    f2 = stock_data(ticker2, start, end, 'Close')
    f2 = f2.rename(columns={'Close':ticker2})

    f = pd.concat([f, f2], axis=1)
    f = f.pct_change()
    f['diff'] = 1 + (f[ticker1] - f[ticker2])
    f['RS'] = 100
    f.loc[1:, 'RS'] = f['diff'][1:].cumprod() * 100
    rs = f['RS']

    return rs 


def rsi(ser, days=14):
    '''
    Returns: 
        series of RSI values for a series of prices.
    Params:
        ser: series to calculate RSI on.
        days(optional): number of days to use for RSI calculation.
    '''
    up  = ser.copy().pct_change()
    up[up < 0] = 0
    down = ser.copy().pct_change()
    down[down > 0] = 0
    avgUp = up.rolling(min_periods=1, window=days).mean()
    avgDown = down.rolling(min_periods=1, window=days).mean().abs()

    rs = avgUp / avgDown
    rsi = 100.0 - (100.0 / (1.0 + rs))

    return rsi 


def to_pkl(ser, path='./temp.pkl'):
    '''
    Creates a .pkl file from a series.
    Params: 
        ser: series to create .pkl file from.
        path(optional): path and filename of .pkl file to create
    '''
    ser.to_pickle(path=path)

def get_pkl(path):
    '''
    Returns:
        series created from .pkl file.
    Params:
        path: ./temp.pkl would be current directory pickle file.
    '''
    return pd.read_pickle(path)


def invest_passive(ser):
    '''
    Returns:
        A series as if you were to invest $100k in a buy and hold strategy of the passed series.
    Params:
        ser: series of prices
    '''
    f = ser.copy()
    f = f.pct_change() + 1
    f.ix[0] = 100000
    f.ix[1:] = f.ix[1:].cumprod() * 100000

    return f
      

def plotter(ser, pdfName, second_ser=[], title="", yLabel="", annotate=[], grn_vline=[], red_vline=[], secondary_y=False, sec_yLabel=""):
    '''
    Plots a series in current directory
    * Full example after function:

    Params:
        ser: series to plot
        pdfName: string
        second_ser (optional): plot a second series
        title (optional): plot title 
        yLabel (optional): y label of plot
        annotate (optional): pass a list of lists of annotations for the plot
            uses arrows, list of lists should be in [[datetime, annotation], [datetime, annotation]] format
        grn_vline (optional): pass a list of dates for vertical shading.  Should be in format
            [date, date, date]
        red_vline (optional): plot red vertical line at specified dates 

    '''
    pp = PdfPages('./{}.pdf'.format(pdfName))
    ax = ser.plot.line(legend=False, linewidth=0.5)

    if len(grn_vline) > 0:
        for dates in grn_vline:
            plt.axvspan(dates, dates+relativedelta(days=1), color='g', alpha=0.2, lw=2)

    if len(red_vline) > 0:
        for dates in red_vline:
            plt.axvspan(dates, dates+relativedelta(days=1), color='r', alpha=0.2, lw=2)

    if len(annotate) > 0:
        y = -15 
        x = -15 
        for a,b in annotate:
            idx = ser.index.get_loc(a, method='nearest')
            ax.annotate(b,
                    (ser.index[idx], ser.ix[idx]), #x, y locations
                    xytext=(x,y),
                    fontsize=7,
                    textcoords='offset points',
                    arrowprops=dict(arrowstyle='-|>'))
    plt.title(title, fontsize=10)
    plt.ylabel(yLabel)

    if len(second_ser) > 0:
        second_ser.plot.line(color='crimson', legend=False, linewidth=0.5, secondary_y=secondary_y)
    
    if len(sec_yLabel) > 0:
        ax.right_ax.set_ylabel(sec_yLabel)

    x_axis = ax.axes.get_xaxis()
    x_axis.set_label_text('') #remove 'Date'

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  ncol=5, fancybox=True, shadow=True)

    plt.savefig(pp, format='pdf')
    plt.tight_layout()
    plt.close()
    pp.close()


'''
# EXAMPLE OF PLOTTER FUNCTION
anAnnotation = [[dt.date(2010,1,1), "Bought here"], [dt.date(2010,5,12), "Sold here"]]
buy_dates = [dt.date(2010,1,1)]
sell_dates = [dt.date(2010,5,12)]
ser = stock_data('AAPL', start=dt.date(2009,5,1), end=dt.date(2011,1,1), selection='Close')
secser = stock_data('AAPL', start=dt.date(2009,5,1), end=dt.date(2011,1,1), selection='Volume')

plotter(
    ser=ser, 
    pdfName="pdfHere", 
    second_ser = secser,
    title="Buy dates of AAPL",
    yLabel="prices",
    annotate=anAnnotation, 
    grn_vline=buy_dates,
    red_vline=sell_dates,
    )
'''


def plot_rsi(ticker, months_lookback=12):
    '''
    Plots line graph of ticker's closing price vs 14-day RSI.
    months_lookback is how many months before the current date to start the graph.
    '''
    print "Plotting {} vs. RSI...".format(ticker)

    end = dt.date.today()
    start = end - relativedelta(months=months_lookback)

    price = stock_data(ticker=ticker, start=start, end=end, selection='Close')
    rsi_frame  = rsi(price)
    cur_rsi = round(rsi_frame.ix[-1], 2)

    frame =  pd.DataFrame({'rsi': rsi_frame, 'price': price},
                        index=price.index,
            )

    pdfName = ticker + " vs. RSI"
    title = pdfName + "\nCurrent RSI: {}".format(cur_rsi) 

    plotter(ser=frame.price, pdfName=pdfName, second_ser=frame.rsi, title=title, yLabel="Price", secondary_y=True, sec_yLabel="RSI")


def plot_trend(ticker, months_lookback=12):
    '''
    Plots line graph of ticker's closing price vs trend line (line of best fit).
    Adds PDF to current directory.
    months_lookback is how many months before the current date to start the graph.
    '''
    print "Plotting {} vs. Trend Line...".format(ticker)

    end = dt.date.today()
    start = end - relativedelta(months=months_lookback)

    price = stock_data(ticker=ticker, start=start, end=end, selection='Close')
    x = np.arange(len(price))
    m, b = np.polyfit(x, price, 1)
    y = m * x + b

    frame = pd.DataFrame({'trend': y, 'price': price},
                        index=price.index,
            )

    cur_trend = round(frame.trend.ix[-1], 2)
    cur_price = round(frame.price.ix[-1], 2)

    pdfName = '{} vs Trend Line'.format(ticker)
    title = pdfName + '\nCurrent Price: {}  Current Trend: {}'.format(cur_price, cur_trend)

    plotter(ser=frame.price, pdfName=pdfName, second_ser=frame.trend, title=title, yLabel="Price", secondary_y=False)


def plot_ma(ticker, start, end, *moving_averages): 
    '''
    Plots line graph of ticker's closing price and N moving averages.  Adds PDF to current directory.
    '''
    print "Plotting {} vs. Moving Average...".format(ticker)

    price = stock_data(ticker=ticker, start=dt.date(1970, 1, 1), selection='Close') #set start date far back so moving average isn't cut off 
    f = price.ix[start:end]
    f = f.rename('price')
    ax = f.plot.line(legend=False, linewidth=0.5)
    
    for ma in moving_averages:
        ma_frame = price.rolling(window=ma).mean()
        ma_frame = ma_frame.ix[start:end]
        ma_frame = ma_frame.rename('{}'.format(ma))
        ma_frame.plot.line(legend=False, linewidth=0.5)

    pdfName = '{} vs Moving Average'.format(ticker)
    pp = PdfPages('./{}.pdf'.format(pdfName))

    plt.title(pdfName)
    plt.ylabel('Price')

    x_axis = ax.axes.get_xaxis()
    x_axis.set_label_text('') #remove 'Date'

    ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
                  ncol=5, fancybox=True, shadow=True)

    plt.savefig(pp, format='pdf')
    plt.tight_layout()
    plt.close()
    pp.close()


def plot_all(ticker):
    '''
    plots prev 12mo RSI
    plots prev 12mo trend line
    plots 20, 50, 100, 200 day MA for last 12mo
    '''
    end = dt.date.today()
    start = end - relativedelta(months=12) 
    plot_rsi(ticker)
    plot_trend(ticker)
    plot_ma(ticker, start, end, 20, 50, 100, 200)


def rsi_below(ticker, rsi_val):
    '''
    pass in a ticker and integer, returns true if current 14-day RSI is below the passed in value. 
    '''
    end = dt.date.today()
    start = end - relativedelta(months=12)

    price = stock_data(ticker=ticker, start=start, end=end, selection='Close')
    rsi_frame  = rsi(price)
    cur_rsi = rsi_frame.ix[-1]

    if cur_rsi < rsi_val:
        return True #current RSI is below passed in value

    return False


def rsi_above(ticker, rsi_val):
    '''
    pass in a ticker and integer, returns true if current 14-day RSI is below the passed in value. 
    '''
    end = dt.date.today()
    start = end - relativedelta(months=12)

    price = stock_data(ticker=ticker, start=start, end=end, selection='Close')
    rsi_frame  = rsi(price)
    cur_rsi = rsi_frame.ix[-1]

    if cur_rsi > rsi_val:
        return True #current RSI is above passed in value

    return False


def pos_trend(ticker, lookback=12):
    '''
    pass in a ticker and the months lookback for trend line, 
    returns true if slope is positive for trend line. 
    '''
    end = dt.date.today()
    start = end - relativedelta(months=lookback)

    price = stock_data(ticker=ticker, start=start, end=end, selection='Close')
    x = np.arange(len(price))
    m, b = np.polyfit(x, price, 1)

    if m > 0:
        return True #slope of trend line is positive

    return False
   
