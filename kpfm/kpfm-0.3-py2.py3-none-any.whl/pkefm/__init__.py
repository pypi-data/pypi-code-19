# -*- coding: utf-8 -*-
"""
======
pk-EFM
======

The goal here is to define clear interfaces / boundaries between different parts
of the pk-EFM workup. So far we have,

1. Raw h5 file, cantilever oscillation data => cantilever position, timing information
     - Note: Should be general: tp_light, tp_tip 
     - This state has two functions.
        - Decouple rest of workup code from specifics of hdf5 file implementation.
          A new hdf5 file type should only require a new input read function here.
        - Use this intermediate to create output (phase shift vs pulse time, ancillary information).
          Workup this same data structure to produce any addition
2. Python freq, amp, phase information => dphi
   Python freq, amp, phase information => phase_correction
   Etc (At this point, relevant information summarized in a dataframe).
   - Do I need a supplemental dictionary?
3. csv file(s) (+ dictionary?) => fits (simple best fit in python, better best fit in pystan)
    - Print report of best fit workup



"""
from __future__ import division, absolute_import, print_function
import copy
import numpy as np

from .phasekick import individual_phasekick2, weight, get_plot_data, pk_dictionary_to_dataframe, make_df_dict

def calc_t2_tp(half_periods, N2even):
    t2 = np.sum(half_periods[:N2even+1])
    tp = np.sum(half_periods[N2even+1:])
    return t2, tp

def _h5gr_to_workup_input_bnc(gr):
    y = gr['cantilever-nm'][:]
    dt = gr['dt [s]'].value

    half_periods = gr["half periods [s]"][:]
    N2even = gr.attrs['Calc BNC565 CantClk.N2 (even)']

    t1 = gr.attrs['Abrupt BNC565 CantClk.t1 [s]']
    t2, tp = calc_t2_tp(half_periods, N2even)
    t0 = -(t1 + t2)
    t3 = gr.attrs['Abrupt BNC565 CantClk.t3 [s]']
    relative_time = gr['relative time [s]'].value

    return dict(y=y, dt=dt, t0=t0, t1=t1, t2=t2, tp=tp, t3=t3,
                relative_time=relative_time)

def _h5gr_to_workup_input_daq(gr):
    y = gr['cantilever-nm'][:]
    dt = gr['dt [s]'].value
    t0 = gr['t0 [s]'].value
    t1 = gr.attrs['Adiabatic Parameters.t1 [ms]'] * 0.001
    t2 = gr.attrs['Adiabatic Parameters.t2 [ms]'] * 0.001
    tp = gr.attrs['Adiabatic Parameters.tp [ms]'] * 0.001
    t3 = gr.attrs['Adiabatic Parameters.t3 [ms]'] * 0.001
    relative_time = gr['relative time [s]'].value

    return dict(y=y, dt=dt, t0=t0, t1=t1, t2=t2, tp=tp, t3=t3,
                relative_time=relative_time)


def h5gr_to_workup_input(gr, format):    
    """Return a dictionary containing important parameters for working up a phasekick
    dataset.

    
    The dictionary contains:

        y: Cantilever oscillation data
        dt: spacing between 
        t0: Initial time
        t1: Time with V = V_1
        t2: Time with V = V_2
        tp: Time with V = V_p
        t3: Time with V = V_3

    """
    if format == 'BNC':
        return _h5gr_to_workup_input_bnc(gr)
    elif format == 'DAQ':
        return _h5gr_to_workup_input_daq(gr)
    else:
        raise ValueError("format must be 'BNC' or 'DAQ'")


def phasekick_workup(workup_input_data, workup_params):
    """Takes dictionaries of workup input data, workup parameters.
    Returns workup output dictionary."""

    d = copy.copy(workup_params)
    d.update(workup_input_data)
    return individual_phasekick2(**d)



def intermediate_dict_to_df(intermediate_dict):
    """Generate the dataframe.
    This is going to require translating dictionary key:values into the df format.
    We also will need to make the report files use intermediate_representation_plot dict
    rather than the ill-defined dictionary of stuff. Should be okay though.
    """
    relabeled_dict = make_df_dict(intermediate_dict)
    return pk_dictionary_to_dataframe(relabeled_dict)


# Versioneer versioning
from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
