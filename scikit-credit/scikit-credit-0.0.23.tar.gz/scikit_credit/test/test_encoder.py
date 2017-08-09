# -*- coding:utf-8 -*-
import collections
import math
from utils import common

__author__ = 'jiyue'
import requests
import json
import pandas as pd
import numpy as np
from scikit_credit import encoder

'''
zm_score_list = [584, 652, 671, 690, 715, 854]
age_list = [18, 24, 27, 30, 33, 51]
income_amount_list = [3275, 5000, 7200, 12375, 240000]
billmonthamt_list = [941, 1463, 1996, 2729, 35053]

data = dict()
data['version'] = 'v1'
data['data'] = list()
data['data'].append(dict())
# data['data'][0]['zm_score'] = 710
# data['data'][0]['age'] = 35

for zm_score in zm_score_list:
    data['data'][0]['zm_score'] = zm_score
    for age in age_list:
        data['data'][0]['age'] = age
        for income_amount in income_amount_list:
            data['data'][0]['income_amount'] = income_amount
            for billmonthamt in billmonthamt_list:
                data['data'][0]['billmonthamt'] = billmonthamt
                res = requests.post('http://localhost:8098/fc/lqaddinfo', data=json.dumps(data))
                if res.status_code == 200:
                    res_json = json.loads(res.text)
                    print "zm_score:" + str(zm_score) + " " + "age:" + str(age) + " " + "income_amount:" + str(
                        income_amount) + " " + "billmonthamt:" + str(billmonthamt) + "     " + "score:" + str(
                        res_json['data'][0]['score'])
'''
'''
common.cal_weight('/home/jiyue/Desktop/output_encoding')

df = pd.read_csv(u'/home/jiyue/qddata/银行收入和运营商.csv', sep=',')
df_good_users = df[df['label'] == 0].sample(6000)
df_bad_users = df[df['label'] == 1]

frames = [df_good_users, df_bad_users]
df = pd.concat(frames)

y_src = df['label']
X_src = df.drop(['label', 'gender', 'ss_bank_expense_income_diff_all'], axis=1)

# 去掉一个最大值,一个最小值
woe_encoder = encoder.WoeEncoder(binning_mode='ef', bin_width=5)
woe_encoder.fit_transform(X_src.values, y_src.values)
print woe_encoder._features_iv
for item in woe_encoder._binned_range:
    print item
    print '\n'
'''

df = pd.read_csv('/home/jiyue/git/myproject/deeplearning/seven_online/risk_control/fuck.csv', sep=',')
with open('output_score', 'w') as f:
    f.write("ss_bank_avg_income_6m ss_operatorbasic_extendjointdt operatorbills_"
            "billmonthamt_avg_6m operatorvoices_total_time_avg_everyday_6m ss_fund_avg_income_6m "
            "ss_fund_repayment_avg_repaymentamount_6m "
            "id_age id_province_id zm_score tdscore zm_antifraud_score label zengxin_score\n")
    for index, item in df.iterrows():
        params = collections.OrderedDict()
        params['ss_bank_avg_income_6m'] = item['ss_bank_avg_income_6m']
        params['ss_operatorbasic_extendjointdt'] = item['ss_operatorbasic_extendjointdt']
        params['operatorbills_billmonthamt_avg_6m'] = item['operatorbills_billmonthamt_avg_6m']
        params['operatorvoices_total_time_avg_everyday_6m'] = item['operatorvoices_total_time_avg_everyday_6m']
        params['ss_fund_avg_income_6m'] = item['ss_fund_avg_income_6m']
        params['ss_fund_repayment_avg_repaymentamount_6m'] = item['ss_fund_repayment_avg_repaymentamount_6m']
        params['id_age'] = item['id_age']
        params['id_province_id'] = item['id_province_id']
        params['zm_score'] = item['zm_score']
        params['tdscore'] = item['tdscore']
        params['zm_antifraud_score'] = item['zm_antifraud_score']
        params['label'] = item['label']

        common.cal_user_query_score('/home/jiyue/Desktop/output_encoding', f, params)


def cal_qd_score_credit_pass(a_score, zm_score, b_score, td_score, ivs_score):
    p = 15
    q = 15
    d = 25
    c = 20
    b = 50

    theta = 10
    alpha = 5

    if math.isnan(zm_score) or zm_score == 0:
        return 0.0

    if math.isnan(a_score) or a_score == 0:
        a_score = 639.0

    if math.isnan(b_score) or b_score == 0:
        b_score = 596.0

    if math.isnan(td_score):
        td_score = 30.0

    if math.isnan(ivs_score):
        ivs_score = 70.0

    if td_score > 100:
        td_score = 100.0

    if ivs_score == 0:
        ivs_score = 70.0

    e = p * (td_score / 100) + q * (100 - ivs_score) / 100
    N_A = 1.0 * (a_score - 350) / (928 - 350)
    N_B = 1.0 * (b_score - (-59)) / (858 - (-59))
    N_Z = 1.0 * (zm_score - 350) / (928 - 350)
    N_R = 0.7
    return str(N_A) + ',' + str(N_B) + ',' + str(N_Z) + ',' + str(N_R) + ',' + str(e) + ',' + str((int)(
        theta * (alpha * N_R + b * N_A + c * N_Z + d * N_B - e)))


def cal_qd_score_credit_reject_600plus(a_score, zm_score, b_score, td_score, ivs_score):
    p = 20
    q = 20
    d = 35
    c = 20
    b = 40

    theta = 8
    alpha = 5

    if math.isnan(zm_score) or zm_score == 0:
        return 0
    if math.isnan(a_score) or a_score == 0:
        a_score = 639.0
    if math.isnan(b_score) or b_score == 0:
        b_score = 596.0

    if math.isnan(td_score):
        td_score = 30.0
    if math.isnan(ivs_score):
        ivs_score = 70.0

    if td_score > 100:
        td_score = 100.0
    if ivs_score == 0:
        ivs_score = 70.0

    e = p * (td_score / 100) + q * (100 - ivs_score) / 100
    N_A = 1.0 * (a_score - 350) / (928 - 350)
    N_B = 1.0 * (b_score - (-59)) / (858 - (-59))
    N_Z = 1.0 * (zm_score - 350) / (928 - 350)
    N_R = 0.5
    return str(N_A) + ',' + str(N_B) + ',' + str(N_Z) + ',' + str(N_R) + ',' + str(e) + ',' + str((int)(
        theta * (alpha * N_R + b * N_A + c * N_Z + d * N_B - e)))


'''
df = pd.read_csv('/home/jiyue/qddata/dm_tmp_qd_src_score_credit_600plus.csv', sep='\t')
print 'a_score,zm_score,b_score,tdscore,ivs_score,N_A,N_B,N_Z,N_R,e,qd_score'
for index, row in df.iterrows():
    if math.isnan(row['tdscore']) or math.isnan(row['zm_antifraud_score']):
        continue

    print str(row['aplus_score']) + ',' + str(row['zm_score']) + ',' + str(row['b_score']) + ',' + str(
        row['tdscore']) + ',' + str(row['zm_antifraud_score']) + ',' + str(
        cal_qd_score_credit_reject_600plus(row['aplus_score'], row['zm_score'], row['b_score'], row['tdscore'],
                                           row['zm_antifraud_score']))
'''
