# -*- coding: utf-8 -*-
from __future__ import print_function
from concurrent.futures._base import TimeoutError
from functools import partial
from os import path
import imp
import logging
import sys
import netifaces
import pyshark
from configparser import SafeConfigParser
from player import Player


def load_conf():
    conf = SafeConfigParser(delimiters=';', comment_prefixes='#',
                            inline_comment_prefixes=None, allow_no_value=True)
    conf_file = "~/.dj_as/dj.conf"
    full_conf = path.expanduser(conf_file)
    if path.exists(full_conf):
        conf.read(full_conf)
        return conf

def get_assets_dir(conf):
    instrument_paths = conf.get('general', 'assets').split(',')
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


def get_timeout(conf):
    timeout = conf.getint('general', 'timeout')
    if timeout > 0:
        return float('inf')
    return timeout


def get_ifaces():
    ifaces = netifaces.interfaces()
    iface_pairs = {}
    for iface in ifaces:
        try:
            info = netifaces.ifaddresses(iface)[netifaces.AF_INET][0]
            iface_pairs[iface] = info["addr"]
        except KeyError, IndexError:
            continue
    return iface_pairs

def select_iface():
    interfaces = get_ifaces()
    iface_list = [iface for iface in interfaces.keys()]
    while 1:
        for index, iface in enumerate(iface_list):
            print("[{}]: {} ({})".format(index, iface, interfaces[iface]))
        try:
            selection = int(input("Select an interface: "))
            return iface_list[selection]
        except IndexError, TypeError:
            print("Invalid selection")

def get_interface(conf):
    interface = conf.get('general', 'default_interface')
    if interface == 'auto':
        interface = netifaces.gateways()['default'][netifaces.AF_INET][1]
    elif interface == "select":
        interface = select_iface()
    return interface



def main():
    logging.getLogger("trollius").addHandler(logging.NullHandler())
    conf = load_conf()
    instrument_path = get_assets_dir(conf)
    Callbacks = get_callbacks_class(conf)
    timeout = get_timeout(conf)
    interface = get_interface(conf)
    print(interface)

    sounds = Player(instrument_path)
    sounds.load()
    callback_funcs = Callbacks(sounds)
    live_callbacks = []

    for callback_name in conf.options('arrangements'):
        live_callbacks.append(callback_funcs.__getattribute__(callback_name))

    try:
        capture = pyshark.LiveCapture(interface=interface)
        for packet in capture.sniff_continuously(packet_count=timeout):
            for cb in live_callbacks:
                callback_funcs._call(cb, packet)
    except (TimeoutError, KeyboardInterrupt, RuntimeError):
		# TimeoutError will be raied when the capture timeout elapses
		# KeyboardInterrupt catches a user terminating early with ctrl-c
		# RuntimError pyshark exception if interrupted (ex. ctrl-c)
        pass

if __name__ == "__main__":
    main()
