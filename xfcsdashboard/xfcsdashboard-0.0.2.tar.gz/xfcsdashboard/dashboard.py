"""
Main script for xfcsdashboard.

plot_data -> entry point for xfcs metadata
plot_csv -> cli entry point

"""

import os

import pandas as pd
import plotly.graph_objs as go
from plotly.offline import plot

from xfcsdashboard import csv_data
# ------------------------------------------------------------------------------
def add_range_slider():
    """Creates adjustable time series slider.

    Returns:
        xslider: config dict for plotly layout

    """

    xslider = dict(
        rangeselector=dict(
            buttons=[
                dict(count=7,label='1w',step='day',stepmode='backward'),
                dict(count=1,label='1m',step='month',stepmode='backward'),
                dict(count=6,label='6m',step='month',stepmode='backward'),
                dict(count=1,label='YTD',step='year',stepmode='todate'),
                dict(count=1,label='1y',step='year',stepmode='backward'),
                dict(step='all')
                ]
            ),
        rangeslider=dict(),
        type='date'
        )
    return xslider


def make_data_traces(df, data_keys):
    """Creates plotly Scatter traces of selected numeric keywords (and optional mean values).
    Index of data or mean data is tracked for use in opacity controls.

    Args:
        df: dataframe of numeric metadata
        data_keys: iterable of (data key, data mean key | '')

    Returns:
        data: list of plotly Scatter instances
        data_ix: iterable of 0|1 with values of 1 relative to data key in data
        mean_ix: iterable of 0|1 with values of 1 relative to data mean key in data
    """

    data, data_ix, mean_ix = [], [], []

    for param, param_mean in data_keys:
        trace_data = go.Scatter(
            x=df.index, y=df[param], mode='lines', legendgroup=param,
            line=dict(width=1.5),
            name=param
        )

        data.append(trace_data)
        data_ix.append(1)
        mean_ix.append(0)

        if param_mean:
            trace_mean = go.Scatter(
                x=df.index, y=df[param_mean], mode='lines', legendgroup=param,
                line=dict(color='red', width=1),
                name=param_mean
            )

            data.append(trace_mean)
            data_ix.append(0)
            mean_ix.append(1)

    return data, data_ix, mean_ix


def opacity_button(data_ix, mean_ix):
    """Configures opacity drop down menu.

    Args:
        data_ix: iterable with data index at 1 and mean index at 0.
        mean_ix: iterable with data index at 0 and mean index at 1.

    Returns:
        opacity_menu: config dict for layout
    """

    reset_opac = [1] * len(data_ix)
    data_reduce = [a+b for a,b in zip([.5*x for x in data_ix], mean_ix)]
    mean_reduce = [a+b for a,b in zip([.5*x for x in mean_ix], data_ix)]

    opacity_menu = list([
        dict(
            font=dict(family='monospace', size=12),
            showactive = True,
            xanchor = 'auto',
            direction = 'down',
            x = 0,
            y = 1,
            active=0,
            buttons=list([
            dict(label = 'Reset opacity',
                 method = 'update',
                 args = [{'opacity': reset_opac}]),
            dict(label = 'Data opacity 0%',
                 method = 'update',
                 args = [{'opacity': mean_ix}]),
            dict(label = 'Data opacity 50%',
                 method = 'update',
                 args = [{'opacity': data_reduce}]),
            dict(label = 'Mean opacity 0%',
                 method = 'update',
                 args = [{'opacity': data_ix}]),
            dict(label = 'Mean opacity 50%',
                 method = 'update',
                 args = [{'opacity': mean_reduce}])
            ])
        )
    ])
    return opacity_menu


def generate_plot(df, data_keys, fn):
    """Collects all layout, data and instantiates plot.

    Args:
        df: dataframe of numeric metadata
        data_keys: iterable of (data key, data mean key | '')
        fn: file name for outgoing html plot

    Returns:
        file name of html plot
    """

    data, data_ix, mean_ix = make_data_traces(df, data_keys)

    layout = dict(
        font=dict(family='monospace', size=15, color='#000000'),
        title=fn,
        xaxis=dict(showgrid=True, showline=True, gridcolor='#a0a080'))

    layout['xaxis'].update(add_range_slider())
    layout['yaxis'] = dict(showgrid=True, showline=True)
    layout['updatemenus'] = opacity_button(data_ix, mean_ix)

    fig = dict(data=data, layout=layout)
    return plot(fig, filename='{}.html'.format(fn), auto_open=False, show_link=False)


def organize_columns(columns):
    """Locates data column keys and their respective mean data keys.

    Args:
        columns: iterable of dataframe column names

    Returns:
        keywords: iterable of tuples containing (data key, data mean key | '')
    """

    located = []
    keywords = []
    for kw in sorted(columns):
        if kw in located:
            continue
        mean_keys = [mkey for mkey in columns if mkey.startswith(kw+'_MEAN')]
        if not mean_keys:
            keywords.append((kw, ''))
            continue
        for mean_key in mean_keys:
            keywords.append((kw, mean_key))
            located.append(mean_key)

    return keywords


def make_plot(df, filepath):
    data_keys = organize_columns(df.select_dtypes(exclude=['object']).columns)

    if not data_keys:
        print('>>> Cannot locate useable data in:', filepath)
    else:
        html = generate_plot(df, data_keys, fn=filepath.rsplit('.', 1)[0])
        print('\n>>> FCS metadata dashboard generated:', html)


def plot_csv(files):
    for filepath in files:
        df = csv_data.load(filepath)
        make_plot(df, filepath)
    print()


def plot_data(fcs_objs, meta_keys):
    all_data = {key: [fcs.param(key) for fcs in fcs_objs] for key in meta_keys}
    df = pd.DataFrame(all_data)
    if df.columns.contains('$DATE'):
        df.index = pd.to_datetime(df['$DATE'])
        
    filepath = os.path.basename(os.getcwd())
    make_plot(df, filepath)


# ------------------------------------------------------------------------------
