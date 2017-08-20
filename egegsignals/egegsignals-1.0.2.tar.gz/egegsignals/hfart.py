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

"""
Functions for high-frequency analysis (HFA) of electophysiological signals for detection of short artifacts and quantitative assessment of the quality of signals.

This module written with Anastasia Kuzmina in 2014.

"""

import numpy as np
from scipy.signal import hanning, butter, lfilter, firwin

def three_sigma(t, x, aver = 60*10, step = 30):
    """
    Calculates the 3*sigma zone (normal distribution) with averaging on intervals.
    
    :param t: Time sequence (sec)
    :type t: numpy.ndarray
    
    :param x: Sample sequence
    :type x: numpy.ndarray

    :param aver: Length of averaging interval (sec)
    :type aver: float
    
    :param step: Step (sec)
    :type step: float
    
    :returns: numpy.ndarray
    
    """
    s = x.copy()
    bcalc = 0
    ecalc = aver
    bfill = 0
    efill = aver/2
    while ecalc <= t[-1] + step:
        s[(t>=bfill)&(t<efill)] = 3*np.std(x[(t>=bcalc)&(t<ecalc)])
        bcalc += step
        ecalc += step
        bfill = efill
        efill += step
    s[t>=bfill] = 3*np.std(x[t>=bcalc])
    return s

def outliers(t, x):
    """
    Finds outliers
    
    :param t: Time sequence (sec)
    :type t: numpy.ndarray
    
    :param x: Sample sequence
    :type x: numpy.ndarray
    
    :returns: numpy.ndarray

    """
    m = np.mean(x)
    s = three_sigma(t, x)
    ot = []
    for ti,xi,si in zip(t,x,s):
        if (xi < m - si) | (xi > m + si):
            ot.append(ti)
    ot = np.array(ot)
    return ot

def hfa_filter(t, x, l=60, cutoff = 0.3):
    """
    Filtrates signal for HFA using FIR filter
    
    :param t: Time sequence (sec)
    :type t: numpy.ndarray
    
    :param x: Sample sequence
    :type x: numpy.ndarray
    
    :param l: Length of operator
    :type l: float (sec)
    
    :param cutoff: Bound (Hz)
    :type cutoff: float
    
    :returns: numpy.ndarray

    """
    dt = t[1] - t[0]
    h = hanning(2*l/dt)
    x[t<l] *= h[0:len(h)/2]
    x[t>(t[-1]-l)] *= h[len(h)/2:]
    taps = firwin(l/dt+1, cutoff, pass_zero = False, nyq=1/dt/2)
    xf = np.convolve(x, taps, mode = 'same')
    return (t, xf)

def hfa(t, x):
    """
    HFA procedure
    
    :param t: Time sequence (sec)
    :type t: numpy.ndarray
    
    :param x: Sample sequence
    :type x: numpy.ndarray
    
    :returns: tuple

    """
    t, xf = hfa_filter(t, x)
    at = outliers(t, xf)
    return at, xf

def longest_fragment(t, at, n=0):
    """
    Selects longest fragment of signal with n artifacts
    
    :param t: Time sequence (sec)
    :type t: numpy.ndarray
    
    :param at: Time sequence where artifacts are located (sec)
    :type at: numpy.ndarray
    
    :param n: Number of artifacts
    :type n: numpy.ndarray
    
    :returns: tuple
    
    """
    atl = [t[0]] + list(at) + [t[-1]]
    dt = t[1]-t[0]
    df = [j-i for i, j in zip(atl[:-(n+1)], atl[(n+1):])]
    atln = atl[np.argmax(df)]
    return (atln+dt, atln+max(df)-dt)

def quality(t, at, n=0):
    """
    Calculates the quality of signal
    
    :param t: Time sequence (sec)
    :type t: numpy.ndarray
    
    :param at: Time sequence where artifacts are located (sec)
    :type at: numpy.ndarray
    
    :param n: Number of artifacts
    :type n: integer
    
    :returns: float

    """
    dt = t[1] - t[0]
    start, stop = longest_fragment(t, at, n)
    return (stop - start + dt) / (t[-1] - t[0] + dt)

def best_fragment(t, at, ln, percents = False, n=0):
    """
    Selects the best signal's fragment of a given length
    
    :param t: Time sequence (sec)
    :type t: numpy.ndarray
    
    :param at: Time sequence where artifacts are located (sec)
    :type at: numpy.ndarray
    
    :param ln: Length of a fragment (sec)
    :type ln: float
    
    :returns: tuple
    
    """
    if percents==True:
        ln *= t[-1]/100
    atl = np.array([t[0]] + list([at_i for at_i in at[t[-1]-at>=ln]]) + [t_i for t_i in t[t==t[-1]-ln]]) # array of the first points of the fragments
    aq = [quality(t[(t>=i)&(t<i+ln)],[j for j in at[(at>=i)&(at<i+ln)]], n) for i in atl] # quality array
    start = atl[np.argmax(aq)] # the first point of the best fragment
    return(start,start+ln)

def merge_artifacts(at1, at2):
    """
    Merges artifacts locations.
    
    :param at1: Time sequence where artifacts from 1'st group are located (sec)
    :type at1: numpy.ndarray
    
    :param at2: Time sequence where artifacts from 2'nd group are located (sec)
    :type at2: numpy.ndarray
    
    :returns: numpy.ndarray
    
    """
    at = list(at1)
    for at2_i in at2:
        if at2_i not in at:
            at.append(at2_i)
    return np.array(sorted(at))
