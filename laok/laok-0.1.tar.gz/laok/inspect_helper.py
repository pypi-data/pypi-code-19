#! /usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 2017-3-17

@author: laok@laok.studio.com
@email:  1306743659@qq.com
@copyright: Apache License,Version 2.0
'''
import inspect
#===============================================================================
# 使用inspect模块打印信息
#===============================================================================
def simple_description(obj):
    for i in dir(obj):
        if not i.startswith('_'):
            print('%s=%s' %(i,getattr(obj, i) ) )


def detail_description(obj):
    u'''实现比较详细的对象描述
    '''
    print('#%s,%s' %(obj, type(obj)) )
    attrs = inspect.getmembers( obj ,lambda x: not inspect.isroutine(x) )
    attrs = [(k,type(v),v) for k,v in attrs if not k.startswith('_')]
    
    for i,pairs in enumerate(attrs):
        if i == 0:
            print( '#attribute---->' )
        _name , _type , _val = pairs
        _val = '  '.join(str(_val).splitlines() )
        print( "    #%s[%s] [%s]" % (_name , _type , _val) )

    builts = inspect.getmembers( obj , inspect.isbuiltin )
    builts = [(k,type(v)) for k,v in builts if not k.startswith('_')]
    for i,pairs in enumerate(builts):
        if i == 0:
            print( '#builtin-method---->' )
        func_doc = getattr(obj, pairs[0]).__doc__
        if func_doc:
            func_doc = '  '.join(func_doc.splitlines() )
        print( "    #%s [%s] [%s]" % ( pairs[0] , pairs[1] , func_doc  ) )
    
    funcs = inspect.getmembers( obj , lambda x: not inspect.isbuiltin(x) and inspect.isroutine(x) )
    funcs = [(k,v) for k,v in funcs if (not k.startswith('_') or k == '__init__') ]
    for i,pairs in enumerate(funcs):
        if i == 0:
            print( '#funcs/method---->' )
        k,v = pairs
        if  v.__doc__:
            v_des = v.__doc__.splitlines()[0]
        else:
            v_des = ''
            
        try:
            arg_spec = inspect.getargspec(pairs[1])
            argv = inspect.formatargspec(arg_spec.args, arg_spec.varargs , arg_spec.keywords , arg_spec.defaults)
            if v_des:
                print( "    #%s%s [%s]" % (k,argv , v_des ) )
            else:
                print( "    #%s%s" % (k,argv) )
        except Exception as e:
            print("    #%s(...) ==>%s" % (k,v_des) )


