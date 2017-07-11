#!/usr/bin/env python3

import sounddevice as sd

blocksize = 0
device = 'system'

old_in = 0
old_out = 0
old_current = 0


def callback(indata, outdata, frames, time, status):
    global old_in, old_out, old_current
    print(frames,
          time.inputBufferAdcTime - old_in,
          time.outputBufferDacTime - old_out,
          time.currentTime - old_current,
          sep='\t')
    old_in = time.inputBufferAdcTime
    old_out = time.outputBufferDacTime
    old_current = time.currentTime
    outdata.fill(0)


with sd.Stream(device=device, blocksize=blocksize, callback=callback):
    input()
