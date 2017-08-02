#!/usr/bin/env python
# encoding: utf-8

import os
import shutil
from datetime import datetime, date

from zijin_functions import StrategyManager
from zijin_config import ORDER_DIR, LOG_DIR, PREDICT_DIR, START_DATE, END_DATE


def strategy_run(work_dir, script_path, script_mode, predict_format, start=START_DATE, end=END_DATE):
    """
    :param work_dir: 工作目录，脚本和模型文件所在目录
    :param script_path: 脚本名称
    :param script_mode: 脚本类型， predict or trade
    :param predict_format: 如果是预测脚本，预测的格式，如果是交易脚本，None
    :param start: 回测开始时间（选填）
    :param end: 回测结束时间（选填）
    :return: 
    """
    os.chdir(work_dir)
    if os.path.exists(LOG_DIR):
        shutil.rmtree(LOG_DIR)
    os.makedirs(LOG_DIR)
    if os.path.exists(PREDICT_DIR):
        shutil.rmtree(PREDICT_DIR)
    if os.path.exists(ORDER_DIR):
        shutil.rmtree(ORDER_DIR)
    if script_mode == 'predict':
        if isinstance(predict_format, list):
            for arg in predict_format:
                if not isinstance(arg, dict):
                    raise Exception('exception: single predict format should be dict')
        else:
            raise Exception('exception: predict format should be list')
        os.makedirs(PREDICT_DIR)
    else:
        os.makedirs(ORDER_DIR)
    strategy_manager = StrategyManager()
    if isinstance(start, datetime):
        start = start.date()
    if isinstance(end, datetime):
        end = end.date()
    if not isinstance(start, date):
        raise Exception('start should be datetime or date')
    if not isinstance(end, date):
        raise Exception('end should be datetime or date')
    strategy_manager.run_strategy(script_path[:-3], script_mode, predict_format, start, end)