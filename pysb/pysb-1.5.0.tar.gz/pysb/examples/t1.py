#!/usr/bin/env python
"""Reproduce figures 4A and 4B from the EARM 1.0 publication (Albeck et
al. 2008)."""

from __future__ import print_function
from pysb.simulator import ScipyOdeSimulator
from numpy import *

from earm_1_0 import model


# saturating level of ligand (corresponding to ~1000 ng/ml SuperKiller TRAIL)
Lsat = 6E4; 

# relationship of ligand concentration in the model (in # molecules/cell) to actual TRAIL concentration (in ng/ml)
Lfactor = model.parameters['L_0'].value / 50;

L_0_baseline = model.parameters['L_0'].value


def fig_4a():
    print("Simulating model for figure 4A...")
    t = linspace(0, 20*3600, 20*60+1)  # 20 hours, in seconds, 1 min sampling
    dt = t[1] - t[0]

    Ls_exp = Lsat / array([1, 4, 20, 100, 500])
    Td_exp = [144.2, 178.7, 236,   362.5, 656.5]
    Td_std = [32.5,   32.2,  36.4,  78.6, 171.6]
    Ts_exp = [21.6,   23.8,  27.2,  22.0,  19.0]
    Ts_std = [9.5,     9.5,  12.9,   7.7,  10.5]

    CVenv = 0.2
    # num steps was originally 40, but 15 is plenty smooth enough for screen display
    Ls = floor(logspace(1,5,15)) 

    fs = empty_like(Ls)
    Ts = empty_like(Ls)
    Td = empty_like(Ls)

    sim = ScipyOdeSimulator(model, tspan=t)

    print("Scanning over %d values of L_0" % len(Ls))
    for i in range(len(Ls)):
        print("  L_0 = %g" % Ls[i])
        res = sim.run(param_values={'L_0': Ls[i]})
        x = res.all

        fs[i] = (x['PARP_unbound'][0] - x['PARP_unbound'][-1]) / x['PARP_unbound'][0]
        dP = 60 * (x['PARP_unbound'][:-1] - x['PARP_unbound'][1:]) / (dt * x['PARP_unbound'][0])  # in minutes
        ttn = argmax(dP)
        dPmax = dP[ttn]
        Ts[i] = 1 / dPmax  # minutes
        Td[i] = t[ttn] / 60  # minutes


fig_4a()
