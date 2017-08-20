# egegsignals - Software for processing electrogastroenterography signals.

# Copyright (C) 2013 -- 2017 Aleksandr Popov

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Parametes of electrogastroenterography signals and some help functions.

"""

import numpy as np
import scipy.fftpack
from scipy import signal

egeg_fs = {
    'colon' : (0.01, 0.03),
    'stomach' : (0.03, 0.07),
    'ileum' : (0.07, 0.13),
    'nestis' : (0.13, 0.18),
    'duodenum' : (0.18, 0.25),
}

def spectrum(x):
    """Return amplitude spectrum of signal.

    Parameters
    ----------
    x : array_like
        Signal.

    Returns
    -------
    : numpy.array
        Two-side amplitude spectrum.

    """
    return abs(scipy.fftpack.fft(x))

def expand_to(x, new_len):
    """Add zeros to signal. For doing magick with resolution in spectrum.

    Returns
    -------
    : numpy.array
        Signal expanded by zeros.
    
    """
    if new_len <= len(x):
        return x
    x_exp = np.zeros(new_len)
    x_exp[0 : len(x)] = x
    return x_exp

def dominant_frequency(spectrum, dt, fs):
    """
    Return dominant frequency of signal in band of frequencies.

    Parameters
    ----------
    spectrum : array_like
        Pre-calculated spectrum.
    dt : float 
        Sampling period.
    fs : array_like
        Two frequencies bounds.
    
    Returns
    -------
    : float
        Value of parameter.

    """
    f = np.fft.fftfreq(len(spectrum), dt)
    ind = (f>=fs[0]) & (f<=fs[1])
    df_ind = spectrum[ind].argmax()
    return f[ind][df_ind]

def energy(spectrum, dt, fs):
    """
    Return the energy of the part of the specturm.

    Parameters
    ----------
    spectrum : array_like
       Pre-calculated spectrum.
    dt : float 
       Sampling period
    fs : array_like
       Two frequencies bounds
    
    Returns
    -------
    : float
        Value of parameter.

    """
    f = np.fft.fftfreq(len(spectrum),dt)
    ind = (f>=fs[0]) & (f<=fs[1])
    return dt * sum(spectrum[ind]**2) / len(spectrum)

def power(spectrum, dt, fs):
    """
    Return the power of the part of the specturm.

    Parameters
    ----------
    spectrum : array_like
       Pre-calculated spectrum.
    dt : float 
       Sampling period
    fs : array_like
       Two frequencies bounds
    
    Returns
    -------
    : float
        Value of parameter.

    """
    return energy(spectrum, dt, fs) / (len(spectrum) * dt)

def rhythmicity(spectrum, dt, fs):
    """
    Return Gastroscan-GEM version of the rhythmicity coefficient. Do not use it.

    Parameters
    ----------
    spectrum : array_like
       Pre-calculated spectrum.
    dt : float 
       Sampling period
    fs : array_like
       Two frequencies bounds
    
    Returns
    -------
    : float
        Value of parameter.

    """
    f = np.fft.fftfreq(len(spectrum),dt)
    ind = (f>=fs[0]) & (f<=fs[1])
    spectrum = spectrum[ind]
    envelope = sum([abs(spectrum[i] - spectrum[i-1]) for i in range(len(spectrum))])
    return  envelope / len(spectrum)

def rhythmicity_norm(spectrum, dt, fs):
    """
    Return normalized Gastroscan-GEM version of the rhythmicity coefficient.

    Parameters
    ----------
    spectrum : array_like
       Pre-calculated spectrum.
    dt : float 
       Sampling period
    fs : array_like
       Two frequencies bounds
    
    Returns
    -------
    : float
        Value of parameter.

    """
    f = np.fft.fftfreq(len(spectrum),dt)
    ind = (f>=fs[0]) & (f<=fs[1])
    spectrum = spectrum[ind]
    envelope = sum([abs(spectrum[i] - spectrum[i-1]) for i in range(len(spectrum))])
    return  envelope / len(spectrum) / np.max(spectrum)

def stft(x, dt, nseg, nstep, window='hanning', nfft=None, padded=False):
    """
    Return result of short-time fourier transform.

    Parameters
    ----------
    x : numpy.ndarray
        Signal.
    dt : float 
       Sampling period.
    window : str
        Type of window.
    nseg : int
        Length of segment (in samples).
    nstep : int
        Length of step (in samples).
    nfft : int 
        Length of the FFT. If None or less than nseg, the FFT length is nseg.

    Returns
    -------

    : list of numpy.ndarray
        Result of STFT.
    
    """
    wind = signal.get_window(window, nseg)
    Xs=[]
    if padded:
        L = len(x) + (nseg - len(x) % nseg) % nseg
        x = expand_to(x, L)

    if not nfft:
        nseg_exp = nseg
    else:
        nseg_exp = max(nseg, nfft)
        
    for i in range(0, len(x)-nseg + 1, nstep):
        seg = x[i : i+nseg] * wind
        seg = expand_to(seg, nseg_exp)
        X = spectrum(seg)
        Xs.append(X)
    return Xs

def dfic(fs, x, dt, nseg, nstep, window='hanning', nfft=None, padded=False):
    """
    Return dominant frequency instability coefficient.

    Parameters
    ----------
    fs : array_like
       Two frequencies bounds
    x : numpy.ndarray
        Signal.
    dt : float 
       Sampling period.
    window : str
        Type of window.
    nseg : int
        Length of segment (in samples).
    nstep : int
        Length of step (in samples).
    nfft : int 
        Length of the FFT. Use it for doing magick with resolution in spectrum. If None or less than nseg, the FFT length is nseg.

    Returns
    -------
    : float
        Value of parameter.

    """
    Xs = stft(x, dt, nseg, nstep, window, nfft, padded)
    dfs = np.array([dominant_frequency(X, dt, fs) for X in Xs])
    return np.std(dfs) / np.average(dfs)
