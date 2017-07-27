# -*- coding:utf-8 -*-
import os
import sys
from datetime import datetime

project_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = os.path.dirname(project_dir)
sys.path.append(project_dir)
print 'project_dir', project_dir

from time_slice import TimeSliceUtils

def test_merge1():
    t1 = {
        "start_time": "2016-11-01",
        "end_time": "2016-12-01"
    }
    
    t2 = {
        "start_time": "2016-11-10",
        "end_time": "2016-12-03"
    }

    print TimeSliceUtils.merge([t1, t2])

def test_merge2():
    t1 = {
        "start_time": "2016-11-01",
        "end_time": "2016-12-01"
    }
    
    t2 = {
        "start_time": "2017-11-10",
        "end_time": "2017-12-03"
    }

    print TimeSliceUtils.merge([t1, t2])

def test_merge3():
    t1 = {
        "start_time": "2016-11-01",
        "end_time": "2016-12-01"
    }
    
    t2 = {
        "start_time": "2016-12-01",
        "end_time": "2017-12-03"
    }

    print TimeSliceUtils.merge([t1, t2])


def test_minus():
    t1 = {
        "start_time": datetime(2016, 11, 1), 
        "end_time": datetime(2016, 12, 1),
    }

    t2 = {
        "start_time": datetime(2016, 11, 11), 
        "end_time": datetime(2016, 11, 14),
    }

    # minus    
    print TimeSliceUtils.minus([t1], [t2])

    t3 = {
        "start_time": datetime(2016, 10, 11), 
        "end_time": datetime(2016, 12, 14),
    }

    print TimeSliceUtils.minus([t3], [t1, t2])

if __name__ == '__main__':
    test_merge3()
