# encoding: utf-8

'''
Created on 2017-7-20
@author: CHINAFHP
'''

from __future__ import unicode_literals

from pdmparse.parsers import read

from pdmparse.api import PdmParse


def x2(value, c, c1):
    return value * c * c1

f = {
    'x2': x2
}


def gen_model():
    api = PdmParse('/Users/fhp/svn/test', f)
    api.gen_template_file('/Users/fhp/svn/test', r'/Users/fhp/svn/test/abc.pdm',
                          'abc.temp', '*', '_', '.cs')


def print_read():
    """测试read方法读取的XML解析到FnTable中的值，并输出到屏幕
    """
    fnTables = read(r'I:\Gitlab\短信通知.pdm')

    for t in fnTables:
        print u'table:%s' % t.name
        print t

        print u'columns:'
        for column in t.columns:
            print column

        print u'parentrefs:'
        for ref in t.parent_refs:
            print ref

        print u'childrefs:'
        for ref in t.child_refs:
            print ref
        print u'####################################################################\n'


def main():
#     print_read()
    gen_model()

if __name__ == "__main__":
    main()
