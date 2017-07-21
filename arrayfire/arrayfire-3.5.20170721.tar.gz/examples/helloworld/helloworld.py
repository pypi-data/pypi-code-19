#!/usr/bin/python

#######################################################
# Copyright (c) 2015, ArrayFire
# All rights reserved.
#
# This file is distributed under 3-clause BSD license.
# The complete license agreement can be obtained at:
# http://arrayfire.com/licenses/BSD-3-Clause
########################################################
import arrayfire as af

inp=af.constant(0.0,1,1,1,1,dtype=af.Dtype.f64)

filtr=af.constant(0.0,3,3,3,dtype=af.Dtype.f64)

filtr[0,1,1] = 1
filtr[2,1,1] = 1

filtr[1,0,1] = 1
filtr[1,2,1] = 1

filtr[1,1,0] = 1
filtr[1,1,2] = 1

for l in range (2,100,2):
    print(l)
    inp=af.randu(l,l,l,3,dtype=af.Dtype.f64)
    t=af.timer.time()
    conv=af.convolve(inp,filtr, conv_mode=af.CONV_MODE.DEFAULT, conv_domain=af.CONV_DOMAIN.SPATIAL)
    af.sync()
    time_single=af.timer.time() - t
    print("single conv [s] :", time_single)
    loops=100
    t2=af.timer.time()
    for i in range(loops):
        conv=af.convolve(inp,filtr, conv_mode=af.CONV_MODE.DEFAULT, conv_domain=af.CONV_DOMAIN.SPATIAL)
        inp=af.randu(l,l,l,3,dtype=af.Dtype.f64)
    af.sync()
    time_loops=af.timer.time() -t2
    print(loops, "loops mean [s]:",(time_loops/loops))
