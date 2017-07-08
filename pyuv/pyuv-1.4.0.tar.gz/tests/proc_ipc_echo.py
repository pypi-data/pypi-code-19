#!/usr/bin/env python

import sys
sys.path.insert(0, '../')

import pyuv


def on_write(handle, error):
    global channel, recv_handle
    recv_handle.close()
    channel.close()

def on_channel_read(handle, data, error):
    global channel, loop, recv_handle
    pending = channel.pending_handle_type()
    assert pending in (pyuv.UV_NAMED_PIPE, pyuv.UV_UDP, pyuv.UV_TCP), "wrong handle type"
    if pending == pyuv.UV_NAMED_PIPE:
        recv_handle = pyuv.Pipe(loop)
    elif pending == pyuv.UV_TCP:
        recv_handle = pyuv.TCP(loop)
    elif pending == pyuv.UV_UDP:
        recv_handle = pyuv.UDP(loop)
    channel.accept(recv_handle)
    channel.write(b".", on_write, recv_handle)


loop = pyuv.Loop.default_loop()

recv_handle = None

channel = pyuv.Pipe(loop, True)
channel.open(sys.stdin.fileno())
channel.start_read(on_channel_read)

loop.run()

