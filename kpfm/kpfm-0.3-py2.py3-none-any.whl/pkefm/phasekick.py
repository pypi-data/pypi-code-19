# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function
import numpy as np
import pandas as pd
idx = pd.IndexSlice
from scipy import interpolate
from scipy import stats
from collections import OrderedDict
from kpfm.lockin import LockIn, FIRStateLockVarF, FIRStateLock


def masklh(x, l=None, r=None):
    if l is None:
        return (x < r)
    elif r is None:
        return (x >= l)
    else:
        return (x >= l) & (x < r)

def weight(tau, dt, N_sigma=5, N=None, style=stats.expon):
    scale = tau / dt
    
    if N is None:
        N = int(round(scale * N_sigma))

    i = np.arange(N)
    return style.pdf(i, scale=scale)

def get_plot_data(y, dt, t0, N_dec_plot, plot_fir, f0):
    fs = 1. / dt
    lockstate = FIRStateLock(plot_fir, N_dec_plot, f0, 0.0, t0=t0, fs=fs)
    lockstate.filt(y)
    lockstate.dphi = np.unwrap(np.angle(lockstate.z_out))
    df = np.gradient(lockstate.dphi) * (
            fs / (N_dec_plot * 2*np.pi))

    A = np.abs(lockstate.z_out)

    plot_data = dict(t0=lockstate.t0_dec,
                     dt=dt * N_dec_plot,
                     A=A,
                     f=df + f0
                     )

    return plot_data


def measure_dA_dphi(lock, li, tp, t_fit=2e-3,
                dphi_weight_before=None,
                dphi_weight_after=None):
    """Correct for impulsive phase shift at end of pulse time."""
    fs = li.fs
    if dphi_weight_before is None:
        N_b = int(round(fs*t_fit))
    else:
        N_b = len(dphi_weight_before)
        t_fit = N_b / fs

    if dphi_weight_after is None:
        N_a = int(round(fs*t_fit))
    else:
        N_a = len(dphi_weight_after)
        t_fit = N_a / fs

    i_tp = np.arange(lock.t.size)[lock.t < tp][-1]
    # Use 20 data points for interpolating; this is slightly over one
    # cycle of our oscillation
    m = np.arange(-10, 11) + i_tp
    # This interpolator worked reasonably for similar, low-frequency sine waves
    interp = interpolate.KroghInterpolator(lock.t[m], lock.x[m])
    x0 = interp(tp)[()]
    # We only need t0 approximately; the precise value of f0 doesn't matter very much.
    t0 = li.t[(li.t < tp)][-1]
    f0 = li.df[(li.t < tp)][-1] + li.f0(t0)
    v0 = interp.derivative(tp)[()]
    x2 = v0 / (2*np.pi*f0)

    phi0 = np.arctan2(-x2, x0)

    ml = masklh(li.t, tp-t_fit, tp)
    mr = masklh(li.t, tp, tp + t_fit)

    ml_phi = np.arange(li.t.size)[li.t <= tp][-N_b:]
    mr_phi = np.arange(li.t.size)[li.t > tp][:N_a]

    A = abs(li.z_out)
    phi = np.unwrap(np.angle(li.z_out))/(2*np.pi)

    mbAl = np.polyfit(li.t[ml], A[ml], 1)
    mbAr = np.polyfit(li.t[mr], A[mr], 1)

    mb_phi_l = np.polyfit(li.t[ml_phi], phi[ml_phi], 1, w=dphi_weight_before)
    mb_phi_r = np.polyfit(li.t[mr_phi], phi[mr_phi], 1, w=dphi_weight_after)

    dA = np.polyval(mbAr, tp) - np.polyval(mbAl, tp)
    dphi = np.polyval(mb_phi_r, tp) - np.polyval(mb_phi_l, tp)

    return phi0, dA, dphi



def individual_phasekick2(y, dt, t0, t1, t2, tp, N_dec, lockin_fir,
                          weight_before, weight_after, plot_funcs=None, **kwargs):
    """
        x
        fs
        t1
        t2
        tp
        lockin_fir (chosen by fp, fc)
        N_dec (chosen by int(fs/fs_dec))
        weight_before (chosen by opt. filter)
        weight_after (chosen by opt. filter)

    """

    fs = 1. / dt
    t = np.arange(y.size) * dt + t0
    lock = LockIn(t, y, fs)
    lock.run(fir=lockin_fir)
    lock.phase(tf=-t2)
    fc0 = lock.f0corr
    
    N_b = weight_before.size
    N_a = weight_after.size

    # Find N_smooth points before begining of pulse
    # Flip filter coefficients for convolution
    # Could also fit phase to a line here
    df_before = np.polyfit(lock.t[lock.t < 0][-N_b:],
                           lock.df[lock.t < 0][-N_b:],
                           0,
                           w=weight_before[::-1])
    
    # Don't flip filter coefficients, this is 'anti-casual',
    # inferring f at tp from f at times t > tp
    df_after = np.polyfit(lock.t[lock.t > tp][:N_a],
                           lock.df[lock.t > tp][:N_a],
                           0,
                           w=weight_after)

    f1 = fc0 + df_before
    f2 = fc0 + df_after

    lock.phase(ti=-dt*N_b/5, tf=0)
    phi0 = -lock.phi[0]

    def f_var(t):
        return np.where(t > tp, f2,
                np.where(t > t0 + t1, f1, f2)
                    )

    lockstate = FIRStateLockVarF(lockin_fir, N_dec, f_var, phi0, t0=t0, fs=fs)
    lockstate.filt(y)
    lockstate.dphi = np.unwrap(np.angle(lockstate.z_out))
    lockstate.df = np.gradient(lockstate.dphi) * (
            fs / (N_dec * 2*np.pi))
    lockstate.t = td = lockstate.get_t()
    

    phi0_tp, dA, dphi_tp = measure_dA_dphi(lock, lockstate, tp, t_fit=None,
                dphi_weight_before=weight_before[::-1],
                dphi_weight_after=weight_after)

    mb_before = np.polyfit(td[td < 0][-N_b:],
                           lockstate.dphi[td < 0][-N_b:],
                           1,
                           w=weight_before[::-1])

    mb_after = np.polyfit(td[td > tp][:N_a] - tp,
                         lockstate.dphi[td > tp][:N_a],
                         1,
                         w=weight_after)


    phi0 = mb_before[1] + tp * mb_before[0]
    phi1 = mb_after[1]

    # Enforce conversion to float to get rid of annoying 1 element arrays
    # that will cause problems in the DataFrame later.
    outd = dict(
        mb_before=mb_before,
        mb_after=mb_after,
        dphi=float(phi1 - phi0),
        phi0_tp=float(phi0_tp),
        dA=float(dA),
        dphi_tp=float(dphi_tp),
        fc0=float(fc0),
        f1=float(f1),
        f2=float(f2)
        )

    return outd


def pk_dictionary_to_dataframe(d):
    _df = pd.DataFrame.from_dict(d, orient='index')
    named_index = pd.MultiIndex(levels=_df.index.levels,
                            labels=_df.index.labels,
                            names=['expt', 'ds'],)
    df = pd.DataFrame(_df, index=named_index)
    return df


def make_df_dict(d):
    """Reduce the keys in data, and turn them into the keys need for
    the pandas dataframe."""
    dout = {}
    for key, val in d.items():
        data = val['data']
        out = val['out']
        dout[key] = OrderedDict([
            ('tp', data['tp']),
            ('tp_ms', data['tp']*1e3),
            ('dphi [cyc]', out['dphi'] / 2*np.pi),
            ('dphi [mcyc]', out['dphi'] / 2*np.pi * 1e3),
            ('f0 [Hz]', out['fc0']),
            ('df_dV [Hz]', out['f1'] - out['fc0']),
            ('dA [nm]', out['dA']),
            ('dphi_tp_end [cyc]', out['dphi_tp'] / (2*np.pi)),
            ('phi_at_tp [rad]', out['phi0_tp']),
            ('relative time [s]', data['relative_time']),
            ('dphi_corrected [cyc]', out['dphi'] - out['dphi_tp']),
            ('dphi_corrected [mcyc]', (out['dphi'] - out['dphi_tp']) * 1e3)
            ]
                                )
    
    return dout