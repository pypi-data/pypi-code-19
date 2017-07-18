# -*- coding: utf-8 -*-
from player import Player
import pyshark
import netifaces
from configparser import SafeConfigParser
from concurrent.futures._base import TimeoutError
from functools import partial
from os import path
import sys
import imp

def load_conf():
    conf = SafeConfigParser(delimiters=';', comment_prefixes='#',
                            inline_comment_prefixes=None)
    conf_files = ["~/.dj_as/dj.conf",
                  path.join(path.dirname(path.abspath(__file__)), 'dj.conf')]
    for conf_file in conf_files:
        full_conf = path.expanduser(conf_file)
        if path.exists(full_conf):
            conf.read(full_conf)
            return conf

def get_assets_dir(conf):
    instrument_paths = conf.get('general', 'assets').split(',')
    instrument_paths.append(
        path.join(path.dirname(path.abspath(__file__)), 'assets')
    )
    for inst_path in instrument_paths:
        full_inst_path = path.expanduser(inst_path)
        if path.exists(full_inst_path):
            return full_inst_path

def get_callbacks_class(conf):
    callback_paths = conf.get('general', 'callbacks').split(',')
    for cb_path in callback_paths:
        full_cb_path = path.expanduser(cb_path)
        if path.exists(full_cb_path):
            cb_dir = path.dirname(full_cb_path)
            sys.path.append(cb_dir)
            cb_module = path.splitext(path.basename(full_cb_path))[0]
            try:
                mod_info = imp.find_module(cb_module)
                mod = imp.load_module(cb_module, *mod_info)
                cls = mod.Callbacks
                return cls
            except ImportError:
                pass # could not load user callback file
            finally:
                cb_file_handle = mod_info[0]
                if cb_file_handle is not None:
                    cb_file_handle.close()
    if not callback_class:
        from callbacks import CallbackBase as Callbacks
    return Callbacks




def main():
    conf = load_conf()
    instrument_path = get_assets_dir(conf)
    Callbacks = get_callbacks_class(conf)
    interface = conf.get('general', 'default_interface')
    timeout = conf.getint('general', 'timeout')
    if interface == 'auto':
        interface = netifaces.gateways()['default'][netifaces.AF_INET][1]

    sounds = Player(instrument_path)
    sounds.load()
    callback_funcs = Callbacks(sounds)

    for bpf, callback_name in conf.items('arrangements'):
        capture = pyshark.LiveCapture(interface=interface, bpf_filter=bpf)
        cb_func = callback_funcs.__getattribute__(callback_name)
        cb = partial(callback_funcs._call, cb_func, bpf)
        try:
            capture.apply_on_packets(cb, timeout=60)
        except TimeoutError as e:
            # we expect this to be raised when the timeout ends
            pass

if __name__ == "__main__":
    main()
