# -*- coding: utf-8 -*-
"""
Time Domain Fit
===============

Equations to fit the frequency shift transient in the time domain
are developed here.
"""
from __future__ import division, print_function
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import h5py
import sklearn
from scipy import linalg, signal, optimize
import lockin  # Switch to kpfm module at some point
import phasekick2 as pk2 # Switch to kpfm module at some point
import phasekick as pk
import tqdm
import sigutils
import munch

def avg_xt(tr, xr):
    tr_cent = (tr - tr.mean()) * 1e6 # Use µs units here
    A = np.c_[tr_cent ** 2, tr_cent, np.ones_like(tr_cent)]
    val, err, __, ___ = linalg.lstsq(A, xr)
    return val[-1], np.sqrt(err / (xr.size - 3)) / np.sqrt(xr.size)


def record_fit(f, xdata, ydata, p0=None, bounds=(-np.inf, np.inf), name=''):
    fit_data = munch.Munch()
    fit_data.p0 = p0
    fit_data.popt, fit_data.pcov = optimize.curve_fit(f, xdata, ydata, p0=p0, bounds=bounds)
    fit_data.x = f(xdata, *fit_data.popt)
    fit_data.resid = ydata - fit_data.x
    fit_data.name = name
    return fit_data

def _remove_harmonics(b, popt, x_har, N_harmonics=5):
    b.t_zeroed = b.t_ms - b.t_ms[0]
    b.A = harN(b.t_zeroed, popt[2], N_harmonics, np.exp(-b.t_zeroed * popt[3]))
    b.x_no_overtones = b.x - np.dot(b.A, x_har)
    b.resid = b.x_no_overtones - damped_sine(b.t_zeroed, *popt)

def remove_harmonics(b, bdamp):
    _remove_harmonics(b, bdamp.fit.popt, bdamp.x_har, bdamp.N_harmonics)

# def avg_trig_xt(tr, xr):
#     tr_cent = (tr - tr.mean()) * 1e6 # Use µs units here
#     A = np.c_[np.cos(0.062*2*np.pi*tr_cent),
#               np.sin(0.062*2*np.pi*tr_cent),
#               np.ones_like(tr_cent)]
#     val, err, __, ___ = linalg.lstsq(A, xr)
#     return (val[0] + val[-1]), np.sqrt(err / (xr.size - 3)) / np.sqrt(xr.size)

def damped_sine(t, X, Y, f, k, x0):
    """Sine wave with variable phase (X, Y), frequency f,
    damping rate k, and DC offset x0."""
    return np.exp(-k * t) *  (X * np.cos(2*np.pi*f*t) + Y * np.sin(2*np.pi*f*t)) + x0

def _damped_sine_exp_A(t, X, Y, f, k, x0, df, k_tau, k1):
    return np.where(t > 0,
        np.exp(-k1 * t),
        np.exp(-k * t))

def _damped_sine_exp_phi(t, X, Y, f, k, x0, df, k_tau, k1):
    return np.where(t > 0,
        2*np.pi*(f - df * np.expm1(-k_tau*t)) * t,
        2*np.pi*f*t
            )

def damped_sine_exp(t, X, Y, f, k, x0, df, k_tau, k1):
    phi = _damped_sine_exp_phi(t, X, Y, f, k, x0, df, k_tau, k1)
    A = _damped_sine_exp_A(t, X, Y, f, k, x0, df, k_tau, k1)
    return A * (X * np.cos(phi) + Y*np.sin(phi)) + x0

def harN(t, f, N, A=1):
    """Generate harmonics of a given frequency for least squares fitting."""
    cols = []
    for i in xrange(2, N+1):
        cols.extend([A*np.cos(t*2*np.pi*f*i), A*np.sin(t*2*np.pi*f*i)])
    return np.c_[cols].T

def harNphi(phi, N, A=1):
    """Generate harmonics of a given frequency for least squares fitting."""
    cols = []
    for i in xrange(2, N+1):
        cols.extend([A*np.cos(phi*i), A*np.sin(phi*i)])
    return np.c_[cols].T


def fit_damped_sine_eliminate_harmonics(t, x, p0, N_harmonics=5):
    b = munch.Munch()
    # Copy input parameters
    b.t = t
    b.t_zeroed = b.t - b.t[0]
    b.x = x
    b.N_harmonics = N_harmonics

    b.fit0 = record_fit(damped_sine, b.t_zeroed, x, p0=p0, name='initial fit')

    b.A = harN(b.t_zeroed, b.fit0.popt[2], N_harmonics, A=np.exp(-t * b.fit0.popt[3]))

    b.Afit = linalg.lstsq(b.A, b.fit0.resid)
    b.x_har = b.Afit[0]

    b.x_no_overtones = b.x - np.dot(b.A, b.x_har)
    b.fit = record_fit(damped_sine, b.t_zeroed, b.x_no_overtones, p0=p0, name='final fit')

    return b

def signal_average_list(gr_list, ti, tf):
    """Utility function to signal average a group from an HDF5 file."""
    b = munch.Munch()
    xs = []
    ts = []
    for ds in tqdm.tqdm(gr_list):
        t = pk.gr2t(ds)
        t1 = ds.attrs['Abrupt BNC565 CantClk.t1 [s]']
        t0 = -t1 - ds["half periods [s]"][0]
        m = (t > ti) & (t < tf)
        ts.append(t[m])
        x = ds['cantilever-nm'][:]
        xs.append(x[m])

    ts = np.array(ts)
    b.t = np.mean(ts, axis=0)
    x_array = np.array(xs)
    b.x = np.mean(x_array, axis=0)
    m2 = b.t < 0.0
    b.x = b.x - b.x[m2].mean()
    b.t_ms = b.t * 1e3
    b.t_us = b.t * 1e6
    b.t5 = b.t[500:]
    b.x5 = b.x[500:]
    b.t5ms = b.t5*1e3
    b.t5us = b.t5*1e6
    
    try:
        b.li = lockin.LockIn(b.t, b.x, 1e6)
        b.li.lock2()
        b.li.phase(tf=0)
        b.li.name='data'
    except TypeError:
        print("TypeError")
    
    return b


def signal_average_gr(gr, ti, tf):
    """Utility function to signal average a group from an HDF5 file."""
    b = munch.Munch()
    xs = []
    ts = []
    for ds in tqdm.tqdm(gr.values()):
        t = pk.gr2t(ds)
        t1 = ds.attrs['Abrupt BNC565 CantClk.t1 [s]']
        t0 = -t1 - ds["half periods [s]"][0]
        m = (t > ti) & (t < tf)
        ts.append(t[m])
        x = ds['cantilever-nm'][:]
        xs.append(x[m])

    ts = np.array(ts)
    b.t = np.mean(ts, axis=0)
    x_array = np.array(xs)
    b.x = np.mean(x_array, axis=0)
    m2 = b.t < 0.0
    b.x = b.x - b.x[m2].mean()
    b.t_ms = b.t * 1e3
    b.t_us = b.t * 1e6
    b.t5 = b.t[500:]
    b.x5 = b.x[500:]
    b.t5ms = b.t5*1e3
    b.t5us = b.t5*1e6
    
    try:
        b.li = lockin.LockIn(b.t, b.x, 1e6)
        b.li.lock2()
        b.li.phase(tf=0)
        b.li.name='data'
    except TypeError:
        print("TypeError")
    
    return b


def signal_average_parab_list(gr_list, ti, tf, invert=True, align_voltage=False):
    """Utility function to signal average a group from an HDF5 file."""
    b = munch.Munch()
    xs = []
    ts = []
    if invert:
        scale = -1
    else:
        scale = 1
    for ds in tqdm.tqdm(gr_list):
        # Move the zero in time to the initial voltage pulse
        x = ds['cantilever-nm'][:]
        dt = ds['dt [s]'].value

        if align_voltage:
            t1 = ds.attrs['Abrupt BNC565 CantClk.t1 [s]']
            t0 = -t1 - ds["half periods [s]"][0]
            t = np.arange(x.size)*dt + t0
        else:
            t = pk.gr2t(ds)

        m = (t > ti) & (t < tf)
        ts.append(t[m])
        x = ds['cantilever-nm'][:]
        xs.append(scale * x[m])

    ts = np.array(ts)
    b.t = np.mean(ts, axis=0)
    xs = np.array(xs)
    
    # Do proper signal averaging, fitting data to a parabola at each point
    x_err = np.zeros(xs.shape[1])
    x_bf = np.zeros(xs.shape[1])
    for i, (tr, xr) in tqdm.tqdm(enumerate(zip(ts.T, xs.T))):
        x, err = avg_xt(tr, xr)
        x_err[i] = err
        x_bf[i] = x

    b.x = x_bf
    b.x_err = x_err
    m2 = b.t < 0.0
    b.x0neg = b.x[m2].mean()
    b.x = b.x - b.x0neg
    b.t_ms = b.t * 1e3
    b.t_us = b.t * 1e6
    b.t5 = b.t[500:]
    b.x5 = b.x[500:]
    b.t5ms = b.t5*1e3
    b.t5us = b.t5*1e6
    
    try:
        b.li = lockin.LockIn(b.t, b.x, 1e6)
        b.li.lock2()
        b.li.phase(tf=0)
        b.li.name='data'
    except TypeError:
        print("TypeError")
    
    return b


def signal_average_gr_parab(gr, ti, tf, invert=True, align_voltage=False):
    """Utility function to signal average a group from an HDF5 file."""
    return signal_average_parab_list(gr.values(), ti, tf, invert=invert, align_voltage=align_voltage)

def pk_phase(f_i, df, f_f, tau, t0, tp):
    return lambda t: 2 * np.pi * np.where(t <= t0, f_i * (t-t0),
                      np.where(t < tp, f_i*(t-t0)+ pk.phase_step(t-t0, tau, df),
                              f_i*(tp-t0)+ pk.phase_step(tp-t0, tau, df) + f_f*(t-tp)))

def pk_freq(f_i, df, f_f, tau, t0, tp):
    return lambda t: np.where(t <= t0, f_i,
                      np.where(t < tp, f_i - df *np.expm1(-(t-t0)/tau), f_f)
                            )

def osc(phi, amp, X0, Y0):
    return (X0 * np.cos(phi) + Y0 * np.sin(phi)) * amp

def osc_phase(t, phase, A, X0, Y0):
    return osc(phase(t), A(t), X0, Y0)

def osc_freq(t, freq, A, X0, Y0):
    dt = np.r_[0, np.diff(t)]
    phi = np.cumsum(freq(t) * dt)
    return osc(phi, A(t), X0, Y0)

def getA(ki, km, kf, ti, tf):
    def A(t):
        t_ = t - ti
        Af = np.exp(-km*(tf-ti))
        return np.where(t <= ti, np.exp(-ki * t_), np.where(t < tf,
                        np.exp(-km * t_), Af * np.exp(-(t-tf)*kf)))
    return A

def get_xDCt(phaset, ft, A, tau, xDC0, dx_light, t0, tp):
        delta = (ft(tp) / ft(t0))**2
        r = 1 - delta
        
        omega_tau = (2*np.pi*ft(t0)*tau)
        omega_tau2 = omega_tau**2
        omega_bar = (phaset(tp) - phaset(t0)) / (tp - t0)
        xeq = lambda t: np.where(t <= t0, xDC0, np.where(t < tp, xDC0-dx_light*np.expm1(-(t-t0)/tau),0))
        
        xresp = lambda t: np.where(t <= t0, xDC0, np.where(t < tp, r*(
                xDC0 + dx_light -
                dx_light * omega_tau2 / (1+omega_tau2) * np.exp(-(t-t0)/tau)
                ) + 
                delta*xDC0*np.cos(omega_bar*(t-t0)) -
                dx_light * r /(1+omega_tau2) * (
                    np.cos(omega_bar * (t-t0)) + omega_tau*np.sin(omega_bar * (t-t0))
                ),np.nan))

        xDC = lambda t: (xresp(t) - xeq(t)) * A(t)/A(t0) + xeq(t)
        return xDC

def fit(f, xdata, ydata, p0=None, bounds=(-np.inf, np.inf), tfit=None, name=''):
    fit_data = munch.Munch()
    fit_data.popt, fit_data.pcov = optimize.curve_fit(f, xdata, ydata, p0=p0, bounds=bounds)
    fit_data.x = f(xdata, *fit_data.popt)
    fit_data.resid = ydata - fit_data.x
    if tfit is None:
        tfit = xdata
    
    fs = 1.0/np.mean(np.diff(tfit))
    li = lockin.LockIn(tfit, fit_data.x, fs)
    li.lock2()
    li.phase(tf=0)
    fit_data.li = li
    fit_data.name = name
    fit_data.li.name = name
    return fit_data


def workup_signal_averaged_force_data(b, ti_phase=-0.02, tf_phase=-0.001, T = 0.005):

    fs = 1.0/np.mean(np.gradient(b.t))
    
    li = lockin.LockIn(b.t5, b.x5, fs=fs)
    li.f0_est = 65900
    li.lock2(fp=500, fc=2000)
    li.phase(ti=ti_phase, tf=tf_phase,adjust_f0=False)
    m = pk.masklh(li.t, ti_phase, tf_phase)
    mb = np.polyfit(li.t[m]-li.t[m][0], np.unwrap(li.phi[m]), 1)
    li.lock2(fp=500, fc=2000, f0=li.f0 + mb[0] / (2*np.pi))
    li.phase(ti=ti_phase/2, tf=tf_phase, adjust_f0=False)
    
    t = li('t')
    X = li('X')
    Y = li('Y')
    Npts = li.fir.size//8
    mask = pk.masklh(t, -T, T)
    mR = pk.masklh(t, 0, T)
    mL = pk.masklh(t, -T, 0)
    t_L = t[mL][:-Npts]
    X_L = X[mL][:-Npts]
    Y_L = Y[mL][:-Npts]

    t_R = t[mR][Npts:]
    X_R = X[mR][Npts:]
    Y_R = Y[mR][Npts:]



    X_mb_L = np.polyfit(t_L, X_L, 1)
    Y_mb_L = np.polyfit(t_L, Y_L, 1)

    X_mb_R = np.polyfit(t_R, X_R, 1)
    Y_mb_R = np.polyfit(t_R, Y_R, 1)

    dX = np.polyval(X_mb_R, 0) - np.polyval(X_mb_L, 0)
    dY = np.polyval(Y_mb_R, 0) - np.polyval(Y_mb_L, 0)
    dA = (dX**2 + dY**2)**0.5
    
    return dA


def make_col(f, t, div):
    t_div = t.reshape(-1, div)
    col = np.zeros((t.size, t_div.shape[0]))
    for i, tt in enumerate(t_div):
        col[i*div:(i*div+div), i] = f(tt)
    
    return col

def make_L(col, initial=1000.0):
    N = col.shape[1]
    L = np.zeros((N, N))
    for j in xrange(N):
        for k in xrange(N):
            if k == 0:
                L[j,k] = initial
            elif j >= k:
                L[j,k] = 1.0
    return L

class WorkupForceEFM(object):
    def __init__(self, fm, fc, Nm, Nc):
        self.fm = fm
        self.fc = fc
        self.Nm = Nm
        self.Nc = Nc

    def __repr__(self):
        return "WorkupForceEFM(fm={},fc={},Nm={},Nc={})".format(self.fm,
            self.fc, self.Nm, self.Nc)

    def __call__(self, t, x):
        fm = self.fm
        fc = self.fc
        Nm = self.Nm
        Nc = self.Nc
        Npts_per_column = [Nm, Nm, Nm, Nm, Nc, Nc, Nc]
        cols = [make_col(lambda t: np.cos(2*np.pi*fm*t), t, Nm),
        make_col(lambda t: np.sin(2*np.pi*fm*t), t, Nm),
        make_col(lambda t: np.cos(4*np.pi*fm*t), t, Nm),
        make_col(lambda t: np.sin(4*np.pi*fm*t), t, Nm),
        make_col(lambda t: np.cos(2*np.pi*fc*t), t, Nc),
        make_col(lambda t: np.sin(2*np.pi*fc*t), t, Nc),
        make_col(lambda t: np.ones_like(t), t, Nc),
       ]

        lengths = [col.shape[1] for col in cols]
        slices = np.r_[0, np.cumsum(lengths)]

        Afull = np.concatenate(cols, axis=1)
        fit = linalg.lstsq(Afull, x)
        all_params = fit[0]
        params = [all_params[slices[i]:slices[i+1]] for i in range(len(slices)-1)]
        ts = [t[::Npts] for Npts in Npts_per_column]
        resid = x - np.dot(Afull, all_params)

        return munch.Munch(t=t, x=x,
                        fit=fit,
                        all_params=all_params,
                        params=params,
                        t_mod=t[::Nm],
                        t_cant=t[::Nc],
                        ts=ts,
                        resid=resid)





