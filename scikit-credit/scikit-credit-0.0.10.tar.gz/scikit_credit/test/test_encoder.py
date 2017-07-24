# -*- coding:utf-8 -*-

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
df = pd.read_csv(u'/home/jiyue/qddata/银行收入和运营商.csv', sep=',')
y_src = df['label']
X_src = df.drop(['label', 'gender'], axis=1)

# 去掉一个最大值,一个最小值
woe_encoder = encoder.WoeEncoder(bin_width=25)
woe_encoder.fit_transform(X_src.values, y_src.values)
print woe_encoder._features_iv
for item in woe_encoder._binned_range:
    print item
    print '\n'
