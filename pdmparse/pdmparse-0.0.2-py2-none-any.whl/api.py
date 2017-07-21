# encoding: utf-8

'''
Created on 2014-7-19
@author: hshl.ltd
'''

from __future__ import unicode_literals

import os

from jinja2 import Environment, FileSystemLoader

from pdmparse.parsers import read

CODEC = 'UTF-8'


class PdmParse(object):

    def __init__(self, template_dir, filters=None):
        filters = filters or {}
        loader = FileSystemLoader(template_dir)
        env = Environment(loader=loader)
        env.filters.update(filters.copy())
        self.env = env

    def get_template(self, template_name):
        template = self.env.get_template(template_name)
        return template

    def gen_template_file(self, out_dir, pdm_path, template_name, tables,
                          file_prefix=None, file_suffix=None,
                          out_file_rename_func=None, **kwargs):

        if not os.path.exists(pdm_path) or not os.path.isfile(pdm_path):
            raise IOError('pdm文件路径:%s,路径不存在,或者不是文件' % pdm_path)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        t = self.get_template(template_name)

        pdm_tables = read(pdm_path)
        for pdm_table in pdm_tables:
            if '*' in tables or pdm_table.code in tables:
                d = {'table': pdm_table}
                d.update(**kwargs)
                if out_file_rename_func:
                    out_file_name = out_file_rename_func(pdm_table)
                else:
                    out_file_name = '%s%s%s' % (
                        file_prefix, pdm_table.code, file_suffix)

                out_file = os.path.join(out_dir, out_file_name)
                with open(out_file, 'w') as f:
                    f.write(t.render(d).encode(CODEC))
                print out_file

    def gen_singtemplate_file(self, out_dir, pdm_path, template_name, out_file_name, tables, **kwargs):
        if not os.path.exists(pdm_path) or not os.path.isfile(pdm_path):
            raise IOError('pdm文件路径:%s,路径不存在,或者不是文件' % pdm_path)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        t = self.get_template(template_name)

        pdm_tables = read(pdm_path)
        if len(tables) > 0 and tables != '*':
            pdm_tables = [
                pdm_table for pdm_table in pdm_tables if pdm_table.code in tables]

        d = {'tables': pdm_tables}
        d.update(**kwargs)

        out_file = os.path.join(out_dir, out_file_name)
        with open(out_file, 'w') as f:
            f.write(t.render(d).encode(CODEC))
        print out_file
