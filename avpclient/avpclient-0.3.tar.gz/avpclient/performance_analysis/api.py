import json

import pandas as pd
import requests

import constants as const


def calc_periodic_index_return_df(df_exposure, return_type='simple'):
    res = requests.post(const.base_url + const.to_periodic_index_return, json=df_exposure.to_json()
                        , headers=const.api_key_header
                        , params={'returnType': return_type})

    return pd.read_json(res.content)


def calc_periodic_volatility_df(df_return, nperiods=30):
    res = requests.post(const.base_url + const.to_periodic_volatility, json=df_return.to_json()
                        , headers=const.api_key_header
                        , params={'nperiods': nperiods})

    return pd.read_json(res.content)


def calc_rolling_correlation_df(df_return, nperiods=30):
    res = requests.post(const.base_url + const.to_rolling_correlation, json=df_return.to_json()
                        , headers=const.api_key_header
                        , params={'nperiods': nperiods})

    return pd.read_json(res.content)


def calc_periodic_mtd_return_df(df_return):
    res = requests.post(const.base_url + const.to_periodic_MTD_return, json=df_return.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_qtd_return_df(df_return):
    res = requests.post(const.base_url + const.to_periodic_QTD_return, json=df_return.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_ytd_return_df(df_return):
    res = requests.post(const.base_url + const.to_periodic_YTD_return, json=df_return.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_ltm_return_df(df_return):
    res = requests.post(const.base_url + const.to_periodic_LTM_return, json=df_return.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_ltd_return_df(df_return):
    res = requests.post(const.base_url + const.to_periodic_LTD_return, json=df_return.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_itd_annualized_return_df(df_return):
    res = requests.post(const.base_url + const.to_periodic_ITD_annualized_return, json=df_return.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_3_year_annualized_returns_df(df_return):
    res = requests.post(const.base_url + const.to_periodic_3_year_annualized_returns, json=df_return.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_5_year_annualized_returns_df(df_return):
    res = requests.post(const.base_url + const.to_periodic_5_year_annualized_returns, json=df_return.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_rebase_df(df):
    res = requests.post(const.base_url + const.to_rebase, json=df.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_drawdown_df(df):
    res = requests.post(const.base_url + const.to_drawdown_series, json=df.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_sortino_ratio(df_return, rf=0, nperiods=30):
    res = requests.post(const.base_url + const.calc_sortino_ratio, json=df_return.to_json()
                        , headers=const.api_key_header
                        , params={'nperiods': nperiods, 'rf': rf})

    return pd.read_json(res.content, typ='series')


def calc_calmar_ratio(df):
    res = requests.post(const.base_url + const.calc_calmar_ratio, json=df.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content, typ='series')


def calc_sharpe_ratio(df_return, rf=0, nperiods=30, annualize=True):
    res = requests.post(const.base_url + const.calc_sharpe_ratios, json=df_return.to_json()
                        , headers=const.api_key_header
                        , params={'rf': rf, 'nperiods': nperiods, 'annualize': annualize})

    return pd.read_json(res.content, typ='series')


def calc_information_ratio(bp):
    res = requests.post(const.base_url + const.calc_information_ratio, json=bp.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content, typ='series')


def calc_max_drawdown(df):
    res = requests.post(const.base_url + const.calc_max_drawdown, json=df.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content, typ='series')


def calc_risk_return_ratio(df):
    res = requests.post(const.base_url + const.calc_risk_return_ratio, json=df.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content, typ='series')


def calc_stats_df(df):
    res = requests.post(const.base_url + const.calc_stats, json=df.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_ulcer_index(df):
    res = requests.post(const.base_url + const.calc_ulcer_index, json=df.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content, typ='series')


def calc_ulcer_performance_index(df, rf=0, nperiods=30):
    res = requests.post(const.base_url + const.calc_ulcer_performance_index, json=df.to_json()
                        , headers=const.api_key_header
                        , params={'rf': rf, 'nperiods': nperiods})

    return pd.read_json(res.content, typ='series')


def calc_periodic_xnpv_df(mv, cf, rate=0.1):
    content = {}
    content['MV'] = mv.to_json()
    content['CF'] = cf.to_json()
    content['rate'] = rate

    res = requests.post(const.base_url + const.calc_xnpv, json=json.dumps(content)
                        , headers=const.api_key_header)

    return pd.read_json(res.content).set_index('Date')


def calc_periodic_xirr_df(mv, cf):
    content = dict(MV=mv.to_json(), CF=cf.to_json())

    res = requests.post(const.base_url + const.calc_xirr, json=json.dumps(content)
                        , headers=const.api_key_header)

    return pd.read_json(res.content).set_index('Date')


def calc_periodic_multiple_of_money_df(content):
    res = requests.post(const.base_url + const.to_periodic_multiple_of_money, json=content.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_multiple_of_money_net_of_carry_df(content):
    res = requests.post(const.base_url + const.to_periodic_multiple_of_money_net_of_carry, json=content.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_realized_multiple_of_money_df(content):
    res = requests.post(const.base_url + const.to_periodic_realized_multiple_of_money, json=content.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_gross_multiple_df(content):
    res = requests.post(const.base_url + const.to_periodic_gross_multiple, json=content.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_net_multiple_df(content):
    res = requests.post(const.base_url + const.to_periodic_net_multiple, json=content.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_net_net_multiple_df(content):
    res = requests.post(const.base_url + const.to_periodic_net_net_multiple, json=content.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_distributed_capital_to_paid_in_capital_df(content):
    res = requests.post(const.base_url + const.to_periodic_distributed_capital_to_paid_in_capital,
                        json=content.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)


def calc_periodic_residual_value_to_paid_in_capital_df(content):
    res = requests.post(const.base_url + const.to_periodic_residual_value_to_paid_in_capital, json=content.to_json()
                        , headers=const.api_key_header)

    return pd.read_json(res.content)
