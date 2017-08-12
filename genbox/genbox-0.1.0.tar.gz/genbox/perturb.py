#!/usr/bin/env python

possible_distr = ['normal','lognormal']

import numpy as np

def _is_positive   ( array ):
    return ( array.min() > 0.0 ).all()

def _check_mean  ( array_mean, mean, max_err ):
    mean_min   = (1.0-max_err) * mean
    mean_max   = (1.0+max_err) * mean
    return array_mean>mean_min and array_mean<mean_max

def _check_rel_stdev ( array_rel_stdev, rel_stdev, max_err ):
    rel_stdev_min   = rel_stdev - max_err
    rel_stdev_max   = rel_stdev + max_err
    return array_rel_stdev>rel_stdev_min and array_rel_stdev<rel_stdev_max


def list_distr():
    '''
    List possible perturbation error distributions
    '''
    return possible_distr


def perturb_factors(mean, rel_stdev, num, distr='normal', max_err=0.01):
    '''
    Perturb a variable using different assumptions about error distribution
    and magnitude.
    '''
    # check input:
    if not distr in possible_distr:
        raise IOError('unknown <distr> "{}" - use one of: {}'.format(distr,', '.join(possible_distr)))


    if rel_stdev==0.0:
        pert_func = lambda mean,std,size: np.ones( size )
    elif distr=='normal':
        pert_func = lambda mean,std,size: np.random.normal( mean, std, size=size )
    elif distr=='lognormal':
        pert_func = lambda mean,std,size: np.random.lognormal(np.log(mean),std,size=size)
    else:
        raise IOError('check your input parameters')


    # Normal/Lognormal distributed random numbers with mean=args.mean and
    # std=args.rel_stdev*args.mean are generated:
    pert = pert_func( mean, rel_stdev*mean, (num,) )

    # Just for convenience...
    pert_mean      = pert.mean()
    pert_rel_stdev = pert.std () / pert_mean


    #------------------------------------------------------------------------------------
    # Test whether:
    #     - there are no negative perturbation values
    #     - the mean is correct (+- max_err*pert_mean)
    #     - the relative standard deviation is correct (+- max_err)
    #
    # If any test is 'False' a new set of perturbation values is generated and tested:
    while not ( _is_positive    ( pert                               )      and  \
                _check_mean     ( pert_mean     , mean     , max_err )      and  \
                _check_rel_stdev( pert_rel_stdev, rel_stdev, max_err )          ):

        pert = pert_func( mean, rel_stdev*mean, (num,) )

        pert_mean      = pert.mean()
        pert_rel_stdev = pert.std()
    #------------------------------------------------------------------------------------

    return pert
