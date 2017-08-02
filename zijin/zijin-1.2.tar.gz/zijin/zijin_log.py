#!/usr/bin/env python
# encoding: utf-8
import os
import csv

from zijin_config import ORDER_HEADER


def zijin_log(path, content):
    with open(path, 'a') as f:
        f.write(content)


def zijin_order(path, order):
    if os.path.exists(path):
        first_write = False
    else:
        first_write = True
    with open(path, 'a') as f:
        csv_writer = csv.writer(f)
        if first_write:
            csv_writer.writerow(ORDER_HEADER)
        csv_writer.writerow([order.datetime, order.type, order.price, order.volume])


def zijin_predict(path, predict):
    if os.path.exists(path):
        first_write = False
    else:
        first_write = True
    with open(path, 'a') as f:
        predict_value_list = []
        predict_value_list.append(predict['datetime'])
        keys = predict.keys()
        keys.remove('datetime')
        keys = sorted(keys)
        csv_writer = csv.writer(f)
        if first_write:
            csv_writer.writerow(['datetime'] + sorted(keys))
        for key in keys:
            predict_value_list.append(predict[key])
        csv_writer.writerow(predict_value_list)
