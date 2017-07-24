# -*- coding: utf-8 -*-
"""
======
lockin
======

This module contains classes and functions for performing digital lock-in
amplifier data analysis.
"""
from __future__ import division, absolute_import, print_function
import numpy as np
from scipy import signal, optimize
import matplotlib as mpl
import matplotlib.pyplot as plt
import h5py
import pandas as pd

import sigutils

from scipy.signal.signaltools import _centered

from kpfm.util import next_fast_len

class LockIn(object):
    """A basic digital lock-in amplifier. 

    Run an input signal x through a digital lock-in amplifier.
    A finite impulse response (FIR) lock-in filter can be provided by
    `lock` or `lock2`, or a custom FIR filter can be used by directly
    calling `run`. After generating the complex lock-in output, the lock-in
    can be phased by running `phase`, or `autophase`.
    After phasing, the lock-in output channels are X, the in-phase channel and
    Y, the out-of-phase channel.

    Parameters
    ----------
    t: array_like
        Time array
    x: array_like
        Input signal array
    fs: float
        Sampling rate


    Example
    -------

    >>> fs = 1000.0
    >>> t = np.arange(1000)/fs
    >>> A = 1 - 0.1 * t
    >>> f = 80 + 0.1 * t
    >>> x = A * np.sin(np.cumsum(f)*2*np.pi/fs)
    >>> li = LockIn(t, x, fs)

    We process the data with a 20 Hz bandwidth lock-in amplifier filter.

    >>> li.lock(bw=20.0)
    Response:
    f   mag       dB
     0.000 1.000    0.000
    10.000 0.996   -0.035
    20.000 0.500   -6.022
    40.025 0.000  -91.020
    80.051 0.000 -113.516
    500.000 0.000 -204.987

    The lock-in amplifier automatically infers the reference frequency.
    The printed response shows the lock-in amplifier gain at different
    frequencies. For the output to be valid the gain at the reference frequency
    must be very small (-60 dB or smaller).  

    We phase the lock-in amplifier output, and then have the lock-in variables
    available for use.

    >>> li.phase()
    >>> li('t') # Shortcut for accessing masked version of the signal.

    """
    def __init__(self, t, x, fs=None):
        self.t = t
        self.x = x

        if fs is not None:
            self.fs = fs
        else:
            self.fs = 1/np.mean(np.gradient(t))

        self.f0_est = freq_from_fft(self.x, self.fs)

    @classmethod
    def from_x(Cls, x, fs, t0=0):
        """Generate the time array internally."""
        t = t0 + np.arange(x.size) / fs
        return Cls(t, x, fs)

    def __call__(self, key):
        """Shorthand for validly masked section of any data array."""
        return getattr(self, key)[self.m]

    def __repr__(self):
        f0 = getattr(self, 'f0', self.f0_est)
        return "LockIn(f0={})".format(f0)

    def run(self, f0=None, fir=None):
        """Run the lock-in amplifier at reference frequency ``f0``,
        using the finite impulse response filter ``fir``.
        """
        if f0 is None:
            self.f0 = f0 = self.f0_est
        else:
            self.f0 = f0
        if fir is not None:
            self.fir = fir

        self.z = z = signal.fftconvolve(self.x * np.exp(-2j*np.pi*f0*self.t),
                                        2*self.fir,
                                        "same")

        n_fir = self.fir.size
        indices = np.arange(self.t.size)
        # Valid region mask
        # This is borrowed explicitly from scipy.signal.sigtools.fftconvolve
        self.m = m = np.zeros_like(self.t, dtype=bool)
        mask_indices = _centered(indices, self.t.size - n_fir + 1)
        if n_fir % 2 == 0:
            mask_indices += 1
        self.m[mask_indices] = True

        self.A = abs(self.z)
        self.phi = np.angle(self.z)


    def lock(self, bw=None, f0=None, bw_ratio=0.5, coeff_ratio=9., coeffs=None,
             window='blackman'):
        """Standard, windowed finite impulse response filter."""

        t = self.t
        fs = self.fs

        if f0 is None:
            self.f0 = f0 = self.f0_est
        else:
            self.f0 = f0

        if bw is None:
            if bw_ratio > 1:
                raise ValueError("Bandwidth ratio 'bw_ratio' must be < 1 (bw_ratio={}".format(bw_ratio))
            bw = bw_ratio * f0 / (self.fs/2)
        else:
            bw = bw / (self.fs/2)

        if coeffs is None:
            coeffs = round(coeff_ratio / bw, 0)
            if coeffs > self.x.size:
                raise ValueError(
"""No valid output when 'coeffs' > t.size (coeffs: {}, t.size: {}).
Reduce coeffs by increasing bw, bw_ratio, or decreasing coeff_ratio,
or provide more data.""".format(coeffs, t.size))

        self.fir = b = signal.firwin(coeffs, bw, window=window)

        w, rep = signal.freqz(b, worN=np.pi*np.array([0., bw/2, bw, f0/self.fs, f0/(self.fs/2.), 1.]))

        print("Response:")
        _print_magnitude_data(w, rep, fs)

        self.run(f0=f0)

    def lock2(self, f0=None, fp_ratio=0.1, fc_ratio=0.4, coeff_ratio=8,
              fp=None, fc=None, coeffs=None, window='blackman',
              print_response=True):
        t = self.t
        fs = self.fs

        if f0 is None:
            self.f0 = f0 = self.f0_est
        else:
            self.f0 = f0

        if fp is None:
            fp = fp_ratio * f0

        if fc is None:
            fc = fc_ratio * f0

        self.fir = b = lock2(f0, fp, fc, fs, coeff_ratio, coeffs, window,
                             print_response=print_response)

        if coeffs > self.x.size:
            raise ValueError(
    """No valid output when 'coeffs' > t.size (coeffs: {}, t.size: {}).
    Reduce coeffs by increasing bw, bw_ratio, decreasing coeff_ratio,
    or provide more data.""".format(coeffs, t.size))


        self.run(f0=f0)

    def lock_butter(self, N, f3dB, t_exclude=0, f0=None, print_response=True):
        """Butterworth filter the lock-in amplifier output"""
        t = self.t
        fs = self.fs
        nyq = fs / 2.
        f3dB = f3dB / nyq

        self.iir = ba = signal.iirfilter(N, f3dB, btype='low')

        if f0 is None:
            self.f0 = f0 = self.f0_est


        self.z = z = signal.lfilter(self.iir[0], self.iir[1], self.z)
        # TODO: Fix accounting on final / initial point
        m = self.m
        self.m = self.m & (t >= (t[m][0] + t_exclude)) & (t < (t[m][-1] - t_exclude))

        self.A = abs(self.z)
        self.phi = np.angle(self.z)

        if print_response:
            w, rep = signal.freqz(self.iir[0], self.iir[1],
                        worN=np.pi*np.array([0., f3dB/2, f3dB,
                                             0.5*f0/nyq, f0/nyq, 1.]))
            print("Response:")
            _print_magnitude_data(w, rep, fs)

    def _output_df_X_Y(self):
        """Helper function for outputting frequency shift
        and lock-in X, Y channels after phasing."""
        self.df = np.gradient(self.dphi) * self.fs / (2*np.pi)
        self.Z = np.exp(-1j*self.phi_fit) * self.z
        self.X = self.Z.real
        self.Y = self.Z.imag

    def manual_phase(self, phi0, f0corr=None):
        "Manually phase the lock-in output with phase phi0 (in radians)."
        self.phi0 = phi0
        
        if f0corr is not None:
            self.f0corr = f0corr
            delta_f0 = f0corr - self.f0
        else:
            self.f0corr = self.f0
            delta_f0 = 0.0

        self.phi_fit = self.t * delta_f0 * 2 * np.pi + self.phi0
        self.dphi = np.unwrap(((self.phi - self.phi_fit + np.pi) % (2*np.pi))
                              - np.pi)

        self._output_df_X_Y()


    def autophase(self, ti=None, tf=None, unwrap=False, x0=[0., 0.], adjust_f0=True):
        t = self.t
        m = self.m
        z = self.z


        if unwrap:
            phi = np.unwrap(self.phi)
        else:
            phi = self.phi

        if ti is None and tf is None:
            mask = m
        elif ti is not None and tf is None:
            mask = m & (t >= ti)
        elif ti is None and tf is not None:
            mask = m & (t < tf)
        else:
            mask = m & (t >= ti) & (t < tf)

        self.mb = mb = auto_phase(t[mask], phi[mask], x0, adjust_f0=adjust_f0)

        self.phi0 = mb[-1]

        self.phi_fit = np.polyval(mb, t)

        self.dphi = np.unwrap((
            (self.phi - self.phi_fit + np.pi) % (2*np.pi)) - np.pi)

        if adjust_f0:
            self.f0corr = self.f0 + mb[0] / (2*np.pi)
        else:
            self.f0corr = self.f0

        self._output_df_X_Y()


    def phase(self, ti=None, tf=None, weight=True, adjust_f0=True):
        t = self.t
        m = self.m
        z = self.z

        poly_order = int(adjust_f0)

        if ti is None and tf is None:
            mask = m
        elif ti is not None and tf is None:
            mask = m & (t >= ti)
        elif ti is None and tf is not None:
            mask = m & (t < tf)
        else:
            mask = m & (t >= ti) & (t < tf)

        phi = np.unwrap(self.phi[mask])
        std = np.std(self.phi[mask])
        phi_norm = phi / std

        try:
            if weight:
                A = abs(z[mask]) / np.std(abs(z[mask]))
                self.mb = mb = np.polyfit(t[mask], phi_norm, poly_order, w=A) * std
            else:
                self.mb = mb = np.polyfit(t[mask], phi_norm, poly_order) * std
        except TypeError:
            print(t)
            print(ti)
            print(tf)
            raise

        self.phi_fit = np.polyval(mb, t)

        self.dphi = np.unwrap(((self.phi - self.phi_fit + np.pi) % (2*np.pi))
                              - np.pi)

        self.phi0 = mb[-1]

        if adjust_f0:
            self.f0corr = self.f0 + mb[0] / (2*np.pi)
        else:
            self.f0corr = self.f0

        self._output_df_X_Y()

    def decimate(self, factor=None):
        if factor is None:
            factor = int(self.fs//self.f0)

        self.dec_t = self.t[self.m][::factor]
        self.dec_phi = self.dphi[self.m][::factor]
        self.dec_A = self.A[self.m][::factor]
        self.dec_df = self.df[self.m][::factor]
        self.dec_f0 = self.f0
        self.dec_fs = self.fs/factor
        self.dec_z = self.z[self.m][::factor]

    def phase_dec(self, ti=None, tf=None, weight=True):
        t = self.dec_t
        m = np.ones_like(self.dec_z, dtype=bool)
        z = self.dec_z

        if ti is None and tf is None:
            mask = m
        elif ti is not None and tf is None:
            mask = m & (t >= ti)
        elif ti is None and tf is not None:
            mask = m & (t < tf)
        else:
            mask = m & (t >= ti) & (t < tf)

        phi = np.unwrap(np.angle(z))
        std = np.std(phi[mask])
        phi_norm = phi / std
        try:
            if weight:
                A = abs(z[mask]) / np.std(abs(z[mask]))
                self.mb = mb = np.polyfit(t[mask], phi_norm[mask], 1, w=A) * std
            else:
                self.mb = mb = np.polyfit(t[mask], phi_norm[mask], 1) * std
        except TypeError:
            print(t)
            print(ti)
            print(tf)
            raise

        phi_fit = np.polyval(mb, t)

        dphi = np.unwrap(((phi - phi_fit + np.pi) % (2*np.pi)) - np.pi)

        df = np.gradient(dphi) * self.dec_fs / (2*np.pi)

        self.f0_dec_direct = self.f0 + mb[0] / (2*np.pi)

    def absolute_phase(self, mask, guess=0.0):
        """Perform a curve fit """
        phi = self.phi[mask] + self.t[mask]*2*np.pi*self.f0corr
        popt, pcov = curve_fit(lambda phi, phi0:
            self.A[mask]*np.cos(phi+phi0), phi, self.x[mask],
            [guess])

        self.phi0abs = popt[0]
        self.phiabs = self.phi + self.t*2*np.pi*self.f0corr + self.phi0abs
        return popt, pcov



class FIRStateLock(object):
    """
    Lock-in amplifier object which uses an FIR filter, decimates data, and 
    processes data in batches.

    Pass data in with the ``filt`` function.
    Lock-in amplifier output stored in ``z_out``.
    Time array accessible with the ``get_t`` function.

    Parameters
    ----------
    fir: array_like
        finite-impulse-response (FIR) filter coefficients
    dec: int
        Decimation factor (output sampling rate = input sampling rate /dec)
    f0: scalar
        Lock-in amplifier reference frequency.
    phi0: scalar
        Initial lock-in amplifier phase.
    t0: scalar, optional
        Inital time associated with the first incoming data point.
        Defaults to 0.
    fs: scalar, optional
        Input sampling rate. Defaults to 1.
    """
    def __init__(self, fir, dec, f0, phi0, t0=0, fs=1.):
        self.fir = fir
        self.nfir_mid = (len(fir) - 1)//2
        self.dec = dec
        self.f0 = f0
        self.w0 = f0/fs
        self.phi0 = self.phi_i = phi0 + 2*np.pi*self.w0
        self.t0 = t0
        self.fs = fs
        self.t0_dec = t0 + self.nfir_mid / self.fs
        self.z = np.array([], dtype=np.complex128)
        self.z_out = np.array([], dtype=np.complex128)

    def filt(self, data):
        n = self.fir.size
        phi = (-2*np.pi*self.w0*np.arange(1, data.size+1) + self.phi_i
               ) % (2*np.pi)
        self.phi_i = phi[-1]

        z = np.r_[self.z, data * np.exp(1j*phi)]
        y = signal.fftconvolve(z, 2*self.fir, mode="full")

        indices = np.arange(y.size)
        m = indices[n-1:-n+1]
        if len(m) == 0:
            self.z = z
        else:
            m_dec = m[::self.dec]
            self.z_out = np.r_[self.z_out, y[m_dec]]
            self.z = z[m_dec[-1] - (n-1) + self.dec:]

    def get_t(self):
        return self.t0_dec + np.arange(self.z_out.size)/self.fs * self.dec


class FIRStateLockVarF(object):
    """
    Variable frequency lock-in amplifier object which uses an FIR filter,
    decimates data, and processes data in batches.

    Pass data in with the ``filt`` function.
    Lock-in amplifier output stored in ``z_out``.
    Time array corresponding to the data in ``z_out`` accessible
    with the ``get_t`` function.

    Parameters
    ----------
    fir: array_like
        finite-impulse-response (FIR) filter coefficients
    dec: int
        Decimation factor (output sampling rate = input sampling rate /dec)
    f0: function
        Lock-in amplifier reference frequency as a function of time
    phi0: scalar
        Initial lock-in amplifier phase.
    t0: scalar, optional
        Inital time associated with the first incoming data point.
        Defaults to 0.
    fs: scalar, optional
        Input sampling rate. Defaults to 1.
    """
    def __init__(self, fir, dec, f0, phi0, t0=0, fs=1.):
        self.fir = fir
        self.nfir_mid = (len(fir) -1)//2
        self.dec = dec
        self.f0 = f0
        self.w0 = lambda t: f0(t) / fs
        self.phi0 = self.phi_i = phi0 + 2*np.pi*self.w0(t0)
        self.t0 = t0
        self._current_t = t0  # This field updates as incoming data arrives
        self.fs = fs
        self.t0_dec = t0 + self.nfir_mid / self.fs
        # Stores filtered, lock-in data waiting to be decimated
        self.z = np.array([], dtype=np.complex128)
        # Decimated output
        self.z_out = np.array([], dtype=np.complex128)

    def filt(self, data):
        n = self.fir.size
        m = data.size
        t = self._current_t + np.arange(m, dtype=np.float64) / self.fs
        w = self.w0(t)
        phi = (-2*np.pi*np.cumsum(w) + self.phi_i) % (2*np.pi)
        self.phi_i = phi[-1]
        self._current_t = t[-1]

        z = np.r_[self.z, data * np.exp(1j*phi)]
        y = signal.fftconvolve(z, 2*self.fir, mode="full")

        indices = np.arange(y.size)
        m = indices[n-1:-n+1]
        if len(m) == 0:
            self.z = z
        else:
            m_dec = m[::self.dec]
            self.z_out = np.r_[self.z_out, y[m_dec]]
            self.z = z[m_dec[-1] - (n-1) + self.dec:]

    def get_t(self):
        return self.t0_dec + np.arange(self.z_out.size)/self.fs * self.dec




def phase_err(t, phase, dphi_max, x):
    return abs(abs(phase - (x[0]*t + x[1])) - dphi_max) - dphi_max

def _fit_phase(t, phase, amp, phase_reversals=True):
    if phase_reversals:
        dphi_max = np.pi/2
    else:
        dphi_max = np.pi
    f = lambda x: np.sum(amp**2 * abs((abs(abs(phase - (x[0]*t + x[1])) - dphi_max) - dphi_max))**2)
    return f

def _fit_phase_only(t, phase, amp, phase_reversals=True):
    if phase_reversals:
        dphi_max = np.pi/2
    else:
        dphi_max = np.pi
    f = lambda x: np.sum(amp**2*abs((abs(abs(phase - (x[0])) - dphi_max) - dphi_max))**2)
    return f


def auto_phase(t, z, x0=np.array([0., 0.]), phase_reversals=True, adjust_f0=True):
    """"""
    phase = np.angle(z)
    amp = abs(z) / np.std(z)
    if adjust_f0:
        mb = optimize.fmin_slsqp(_fit_phase(t, phase, amp, phase_reversals), x0,)
    else:
        mb = optimize.fmin_slsqp(_fit_phase_only(t, phase, amp, phase_reversals), x0[-1:],)

    mb[-1] = mb[-1] - np.pi/2
    return mb


def freq_from_fft(sig, fs):
    """Estimate frequency from peak of FFT

    """
    # Compute Fourier transform of windowed signal
    N = next_fast_len(sig.size)
    windowed = sig * signal.blackmanharris(len(sig))
    f = np.fft.rfft(windowed, N)

    # Find the peak and interpolate to get a more accurate peak
    i = np.argmax(abs(f)) # Just use this for less-accurate, naive version
    true_i = parabolic(np.log(abs(f)), i)[0]

    # Convert to equivalent frequency
    return fs * true_i / N


def parabolic(f, x):
    """Quadratic interpolation for estimating the true position of an
    inter-sample maximum when nearby samples are known.

    f is a vector and x is an index for that vector.

    Returns (vx, vy), the coordinates of the vertex of a parabola that goes
    through point x and its two neighbors.

    Example:
    Defining a vector f with a local maximum at index 3 (= 6), find local
    maximum if points 2, 3, and 4 actually defined a parabola.

    In [3]: f = [2, 3, 1, 6, 4, 2, 3, 1]

    In [4]: parabolic(f, argmax(f))
    Out[4]: (3.2142857142857144, 6.1607142857142856)

    """
    xv = 1/2. * (f[x-1] - f[x+1]) / (f[x-1] - 2 * f[x] + f[x+1]) + x
    yv = f[x] - 1/4. * (f[x-1] - f[x+1]) * (xv - x)
    return (xv, yv)


def _print_magnitude_data(w, rep, fs):
    df = pd.DataFrame()
    df['f'] = w / (2*np.pi) * fs
    df['mag'] = abs(rep)
    df['dB'] = 20 * np.log10(df['mag'].values)
    df.sort_values(by="f", inplace=True)
    print(df.to_string(index=False, float_format="{:.3f}".format))
    return df

def fir_weighted_lsq(weight_func, N):
    """Return intercept, slope filter coefficients for a linear least squares
    fit with weight function ``weight_func``, using ``N`` most recent points."""
    i = np.arange(N)
    w = weight_func(i)
    s0 = np.sum(w)
    s1 = np.sum(i*w)
    s2 = np.sum(i**2 * w)
    prefactor = 1./(s0*s2 - s1**2)
    return prefactor*w*(s2 - s1*i), prefactor*w*(s0*i - s1)


# x data
# (guess f0)
# filter (b, a)
# phasing
# Don't actually need time data

def lock2(f0, fp, fc, fs, coeff_ratio=8.0, coeffs=None,
          window='blackman', print_response=True):
    """Create a gentle fir filter. Pass frequencies below fp, cutoff frequencies
    above fc, and gradually taper to 0 in between.

    These filters have a smoother time domain response than filters created
    with lock."""

    # Convert to digital frequencies, normalizing f_nyq to 1,
    # as requested by scipy.signal.firwin2
    nyq = fs / 2
    fp = fp / nyq
    fc = fc / nyq

    if coeffs is None:
        coeffs = int(round(coeff_ratio / fc, 0))

    # Force number of tukey coefficients odd
    alpha = (1-fp*1.0/fc)
    n = int(round(1000. / alpha) // 2)

    N = n * 2 + 1
    f = np.linspace(0, fc, n+1)

    fm = np.zeros(n + 2)
    mm = np.zeros(n + 2)
    fm[:-1] = f
    # Append fm = nyquist frequency by hand; needed by firwin2
    fm[-1] = 1.
    m = signal.tukey(N, alpha=alpha)
    # Only take the falling part of the tukey window,
    # not the part equal to zero
    mm[:-1] = m[n:]

    # Use approx. 8x more frequencies than total coefficients we need
    nfreqs = 2**(int(round(np.log2(coeffs)))+3)+1

    b = signal.firwin2(coeffs, fm, mm,
                       nfreqs=nfreqs,
                       window=window)

    # Force filter gain to 1 at DC; corrects for small rounding errors
    b = b / np.sum(b)

    w, rep = signal.freqz(b, worN=np.pi*np.array([0., fp/2, fp, fc, 2*fc,
                                                  0.5*f0/nyq, f0/nyq, 1.]))
    if print_response:
        print("Response:")
        _print_magnitude_data(w, rep, fs)

    return b