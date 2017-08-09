"""
常用小工具集
"""
from functools import wraps
from datetime import datetime
from time import time


def log_this(func):
    """
    函数日志装饰器
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if func.__name__.startswith('_'):
            print('-----------')
            print('Func On:\t{func}'.format(func=func.__name__))
            s = time()
            r = func(*args, **kwargs)
            e = time()
            print('Time This:\t{time:.3f}'.format(time=(e - s)))
            print('Func Off:\t{func}'.format(func=func.__name__))
            print('-----------')
        else:
            print('\n=======================')
            print('FUNC ON:\t{func}'.format(func=func.__name__))
            print('TIME NOW:\t{now}'.format(now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            s = time()
            r = func(*args, **kwargs)
            e = time()
            print('TIME THIS:\t{time:.3f}'.format(time=(e - s)))
            print('FUNC OFF:\t{func}'.format(func=func.__name__))
            print('=======================')
        return r
    return wrapper


def log_stack(stack: int = 0):
    """
    层叠式函数日志装饰器
    :param stack: 函数层级
    """
    def wrapper_maker(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            marks = ['=', '-', '.']
            print('{mark}'.format(mark=marks[stack] * 10 * (3 - stack)))
            print('FUNC ON:\t{func}'.format(func=func.__name__))
            print('TIME NOW:\t{now}'.format(now=datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            s = time()
            r = func(*args, **kwargs)
            e = time()
            print('TIME THIS:\t{time:.3f}'.format(time=(e - s)))
            print('FUNC OFF:\t{func}'.format(func=func.__name__))
            print('{mark}'.format(mark=marks[stack] * 10 * (3 - stack)))
            return r
        return wrapper
    return wrapper_maker
