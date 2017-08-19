# -*- coding: utf-8 -*-
# Copyright (c) Virtual Reality and Clinical Gait Analysis Laboratory

from scipy.signal import butter, filtfilt


def bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    cut = cutoff / nyq
    b, a = butter(order, cut, btype='low')
    return b, a


def highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    cut = cutoff / nyq
    b, a = butter(order, cut, btype='high')
    return b, a


def bandpass_filter(data, lowcut, highcut, sample_rate, order=5):
    b, a = bandpass(lowcut, highcut, sample_rate, order=order)
    y = filtfilt(b, a, data)
    return y


def lowpass_filter(data, cutoff, sample_rate, order=5):
    b, a = lowpass(cutoff, sample_rate, order=order)
    y = filtfilt(b, a, data)
    return y


def highpass_filter(data, cutoff, sample_rate, order=5):
    b, a = highpass(cutoff, sample_rate, order=order)
    y = filtfilt(b, a, data)
    return y
