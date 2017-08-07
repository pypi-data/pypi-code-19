#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2017-3-17

@author: laok@laok.studio.com
@email:  1306743659@qq.com
@copyright: Apache License,Version 2.0
'''
import sys,types,re,time,traceback,codecs
from collections import OrderedDict
#===============================================================================
# 交互式测试 _lktest
#===============================================================================

#从文件提取 _lktest名字,主要是用于排序
RE_PAT = re.compile(r"^def\s*(.*_lktest)\(\):.*")
def _find_file_lktests(filename):
    with codecs.open(filename ,encoding='utf8') as f:
        for line in f:
            res = RE_PAT.search(line)
            if res:
                yield res.group(1)

#调用函数, 并打印, 捕获异常,
def _timeit_trig_func(func , catch_except=True):
    try:
        print( '%s==begin' % func.__name__ )
        t0 = time.time()
        func()
    except Exception:
        if catch_except:
            raise 
        print ( 'exception in call function---->\n%s' % traceback.format_exc() )
    finally:        
        elapse = time.time() - t0
        print ( '%s==end(time:%fs)\n' % (func.__name__, elapse) )
    
#找到所有主模块的 _lktest
def _find_main_lktest():
    _main = sys.modules['__main__']
    lktest_dict = { 
                   k:v
                   for k,v in  
                   _main.__dict__.items()
                   if k.endswith('_lktest') and isinstance(v, types.FunctionType )
                   }
    #按照代码物理行对 _lktest 进行排序
    lktest_ordered_dict = OrderedDict()
    for name in _find_file_lktests(_main.__file__):
        lktest_ordered_dict[name] = lktest_dict[name]
    return lktest_ordered_dict


#从列表里选择对应的索引
#默认 default = len(listvals)-1
def _console_select_int(select_vals, prompt='Please select:' , default=None):
    for i, value in enumerate(select_vals):
        print("<%-02d>==%s" % (i , value) )
    
    defVal = default if default else len(select_vals) - 1

    i = input(prompt)
    try:
        i = int(i)
        if i > len(select_vals) - 1:
            i = defVal
    except:
        i = defVal 
    return i

'''
run_last 执行最后一个用例
run_all 执行所有
run_first 执行第一个
run_select 执行选择式
run_select_once 执行一次选择                
'''
def run(run_option='run_last' , catch_except=True ,**kargs):
    lktest_ordered_dict = _find_main_lktest()
    if not lktest_ordered_dict:
        print('there is no xxx_lktest here')
        return
    
    lktest_names = list(lktest_ordered_dict.keys())
    
    #执行选项
    if run_option == 'run_first':
        test_name = lktest_names[0]
        _timeit_trig_func( lktest_ordered_dict[test_name] , catch_except)
        return
    elif run_option == 'run_last':
        test_name = lktest_names[-1]
        _timeit_trig_func(lktest_ordered_dict[test_name] , catch_except)
        return
    elif run_option == 'run_all':
        for func in lktest_ordered_dict.values():
            _timeit_trig_func(func , catch_except)
        return
    #执行 'run_select'模式
    while True:
        index = _console_select_int(lktest_names ,
                                   'which test do you want to run , -1=quit , -2=run-all , -3=exit:')
        if index == -3:
            raise SystemExit 
        elif index == -2:
            for func in lktest_ordered_dict.values():
                _timeit_trig_func(func , catch_except)
            return
        elif index == -1:
            return 
        else:
            test_name = lktest_names[index]
            _timeit_trig_func(lktest_ordered_dict[test_name]  , catch_except)
            
        if run_option == 'run_select_once':
            return
    
