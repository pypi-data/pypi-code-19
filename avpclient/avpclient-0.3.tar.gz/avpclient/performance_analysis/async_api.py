from avpclient.performance_analysis import engine
import itertools
import asyncio
import pandas as pd
import numpy as np
import constants as const
import uvloop

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def construct_data_frame_dict(data, url, parameters, bucket_size=1):
    data = data.set_index('Date').sort_index().T
    items = np.array_split(data, len(data) / bucket_size)

    data_frame_dict = {ind: pd.DataFrame for ind, item in enumerate(items)}

    for key in data_frame_dict.keys():
        data_frame_dict[key] = {
            'data': items[key].T.reset_index(),
            'url': url,
            'parameters': parameters
        }

    return data_frame_dict


def calc_periodic_index_return_df(df_exposure, return_type='simple', bucket_size=10):

    data_frame_dict = construct_data_frame_dict(data=df_exposure,
                                                url=const.to_periodic_index_return,
                                                parameters={'returnType': return_type},
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_periodic_volatility_df(df_return, nperiods=30, bucket_size=10):

    data_frame_dict = construct_data_frame_dict(data=df_return,
                                                url=const.to_periodic_volatility,
                                                parameters={'nperiods': nperiods},
                                                bucket_size=bucket_size)

    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_rolling_correlation_df(df_return, nperiods=30):
    df_return = df_return.set_index('Date').sort_index()

    col_names = df_return.columns[df_return.columns != 'Date']
    col_pairs = [list(x) for x in list(itertools.combinations(col_names, 2))]

    data_frame_dict = {ind: pd.DataFrame for ind, item in enumerate(col_pairs)}

    for key, columns in zip(data_frame_dict.keys(), col_pairs):
        data_frame_dict[key] = {
                                'data': df_return[columns].reset_index(),
                                'url': const.to_rolling_correlation,
                                'parameters': {'nperiods': str(nperiods)}
                              }

    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(col_pairs), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_periodic_mtd_return_df(df_return, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_return,
                                                url=const.to_periodic_MTD_return,
                                                parameters=None,
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_periodic_qtd_return_df(df_return, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_return,
                                                url=const.to_periodic_QTD_return,
                                                parameters=None,
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_periodic_ytd_return_df(df_return, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_return,
                                                url=const.to_periodic_YTD_return,
                                                parameters=None,
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_periodic_ltm_return_df(df_return, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_return,
                                                url=const.to_periodic_LTM_return,
                                                parameters=None,
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_periodic_ltd_return_df(df_return, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_return,
                                                url=const.to_periodic_LTD_return,
                                                parameters=None,
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_periodic_itd_annualized_return_df(df_return, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_return,
                                                url=const.to_periodic_ITD_annualized_return,
                                                parameters=None,
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T

def calc_periodic_3_year_annualized_returns_df(df_return, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_return,
                                                url=const.to_periodic_3_year_annualized_returns,
                                                parameters=None,
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_periodic_5_year_annualized_returns_df(df_return, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_return,
                                                url=const.to_periodic_5_year_annualized_returns,
                                                parameters=None,
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_periodic_rebase_df(df_exposure, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_exposure,
                                                url=const.to_rebase,
                                                parameters=None,
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_periodic_drawdown_df(df_exposure, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_exposure,
                                                url=const.to_drawdown_series,
                                                parameters=None,
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_sortino_ratio(df_return, rf=0, nperiods=30, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_return,
                                                url=const.calc_sortino_ratio,
                                                parameters={'nperiods': nperiods, 'rf': rf},
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_calmar_ratio(df_exposure, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_exposure,
                                                url=const.calc_calmar_ratio,
                                                parameters=None,
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_sharpe_ratio(df_return, rf=0, nperiods=30, annualize=True, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_return,
                                                url=const.calc_sharpe_ratios,
                                                parameters={'rf': rf, 'nperiods': nperiods, 'annualize': annualize},
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


def calc_stats_df(df_exposure, bucket_size=10):
    data_frame_dict = construct_data_frame_dict(data=df_exposure,
                                                url=const.calc_stats,
                                                parameters=None,
                                                bucket_size=bucket_size)
    loop = asyncio.get_event_loop()
    res = loop.run_until_complete(engine.run(loop, len(data_frame_dict), data_frame_dict))

    res = [pd.DataFrame.from_dict(x).T for x in res]
    return pd.concat(res).T


