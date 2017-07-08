# -*- coding: utf-8 -*-

'''
script for initialization.
'''
from torcms.script.script_init_tabels import run_init_tables
from .autocrud.base_crud import build_dir
from .script_gen_category import run_gen_category
from .script_crud import run_auto
from .script_fetch_fe2lib import run_f2elib
from .script_create_admin import run_create_admin
from .script_whoosh import run_whoosh

build_dir()


def run_init(*args):
    '''
    running init.
    :return:
    '''
    run_f2elib()
    run_init_tables()
    run_gen_category()
    run_create_admin()
    run_auto()
    run_whoosh()
