from collections import Counter
from contextlib import contextmanager
import re

import data
from engine import *

def normalize(text):
    return re.sub( '[^\w]+', '_', text)

global_pre_script_definitions = {}

class State:
    def __init__(self, scope = None, block = None, old_state = None):
        self.scope = scope
        self.block = block
        self.subblock = None

        self.pre_script_definitions = {}
        if old_state:
            self.pre_script_definitions.update(old_state.pre_script_definitions)

        self.initialized_blocks = set()
        self.pre_block_definitions = {}

global_current_state = State()

def state():
    return global_current_state

@contextmanager
def scope(name, block = None):
    global global_current_state

    if name:
        name = normalize(name)

    old_state = global_current_state
    global_current_state = State(scope, block, old_state)

    current_resultfile_state = None

    try:
        current_resultfile_state = engine().scopeBegin(name)
        pre_script_code()
        yield
    finally:
        post_script_code()
        engine().scopeEnd()

        global global_pre_script_definitions
        global_pre_script_definitions.update(global_current_state.pre_script_definitions)

        global_current_state = old_state

@contextmanager
def subscope(block):
    state().subblock = block
    try:
        pre_block_code(block)
        yield
    finally:
        post_block_code(block)
        state().subblock = None

def pre_script_code():
    if state().block == 'config':
        print data.config_begin
        print data.overrides_function
    else:
        print data.data_source_function
        print data.jms_function
        print data.wtc_function
        print data.resources_begin

def post_script_code():
    if state().block == 'config':
        print data.config_end
    else:
        print data.resources_end

def pre_block_code(block):
    if block in state().initialized_blocks:
        return

    if block == 'wtc-export':
        print data.wtc_export_begin
    elif block.startswith('wtc-import'):
        name = state().pre_block_definitions['remote-access-point']
        networkAddress = state().pre_block_definitions['remote-network-address']
        print data.wtc_remote_access_point.format(remoteAccessPoint = {
           'name': name, 'networkAddress': networkAddress })
    elif block == 'messaging':
        print data.jms_begin

    state().initialized_blocks.add(block)

def post_block_code(block):
    state().pre_block_definitions.clear()

def add_pre_script_definition(variable, value):
    state().pre_script_definitions[variable] = value

def add_pre_block_definition(variable, value):
    state().pre_block_definitions[variable] = value

