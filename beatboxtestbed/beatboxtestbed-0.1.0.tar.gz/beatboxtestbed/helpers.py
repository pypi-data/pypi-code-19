#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import shutil
import ConfigParser
try:
    import cPickle as pickle
except:
    import pickle

import numpy as np

import boxmox

import pkg_resources

default_config_path= pkg_resources.resource_filename(__name__, os.path.join('data','settings.cfg'))

def make_exp_path(exp, createDir=False, overwrite=False):
    '''
    Returns the absolute path of a BEATBOX experiment,
    creates the directory if createDir = True,
    overwrites existing directories if overwrite = True
    '''
    exp_path = os.path.join(os.environ['BEATBOX_WORK_PATH'], os.path.normpath(exp))
    if createDir:
        if overwrite:
            try:
                if os.path.isdir( exp_path ):
                    shutil.rmtree(exp_path)
            except:
                raise Exception('Could not remove existing experiment directory at '+exp_path)
        if not os.path.isdir( exp_path ):
            try:
                os.makedirs( exp_path )
            except:
                raise Exception('Could not create experiment directory at '+exp_path)
    return exp_path

def archive(exp_path, exp):
    '''
    Archive BEATBOX experiment
    '''
    if not os.path.isdir( exp_path ):
        raise Exception('{:s} input path does not exist.'.format(exp_path) )
    target_path = os.path.join(os.environ['BEATBOX_ARCHIVE_PATH'], exp)
    if os.path.isdir( target_path ):
        shutil.rmtree( target_path )
    shutil.move( exp_path, os.environ['BEATBOX_ARCHIVE_PATH'] )

def get_archive_path(exp):
    '''
    Get absolute path to archived experiment exp
    '''
    path = os.path.join( os.environ['BEATBOX_ARCHIVE_PATH'], exp )
    if not os.path.isdir( path ):
        raise IOError('Experiment {:s} does not exist in archive.'.format(exp))
    return path

def str_to_list( values, dtype=str ):
    '''
    A string out of comma-separated values is taken a list of the values is returned.

    :param str values: Comma_separated string
    :param type dtype: Function which converts a string value to a certain data type; default=str
    :return: list of values
    :rtype: list

    Example::

        str_to_list('1, 2,34,5', dtype=int)
        [1,2,34,5]

    '''
    # Split comma-separated values:
    values = values.split(',')
    # Remove blanks and wordwraps:
    values = map( str.strip, values )
    # Convert values to right data type:
    values = map( dtype, values )

    return values

def calc_ens_sen ( ens_TS, state, obs ):
    '''
    The concentration time series of each ensemble member of an ensemble run
    are taken and the ensemble sensitivities of the species in the state
    vector to the observed species are calculated.

    Calculation of ensemble sensitvities:
        corr(xobs,xstate) * stdev(xstate) / stdev(xobs)
            = sensitivity of state species "xstate" to the observed species
                "xobs" (standard deviation and correlation with respect to the
                "number of ensembles"-dimension at every timestep)

    :param numpy.ndarray ens_TS: Concentration time series of N ensembles and
        of dim_state species shape: ("number of ensembles", dim_time, dim_state)
    :param str/list state: state vector; single species or list of species
        which exists/exist in the BOXMOX run
    :param str/list obs: Observed species; single species or list of species
        which exists/exist in the BOXMOX run

    :return: ensemble sensitivity of the species in the state vector to the observed species
    :rtype: numpy.ndarray; shape: (dim_time, dim_obs, dim_state)
    '''

    np.seterr(invalid='ignore')

    # If <state>/<obs> is a single species and not a list a <state>/<obs>-list will be
    # generated:
    state = state if type(state)==list else [state]
    obs   = obs   if type(obs  )==list else [obs  ]

    # Get dimensions:
    dim_obs = len(obs)
    # ens_TS shape :: (dim_ens,dim_time,dim_state)
    _, dim_time, dim_state = ens_TS.shape

    # Calculate ensemble sensitivity :: corr(xobs,xstate) * stdev(xstate) / stdev(xobs)
    # shape :: (dim_time,dim_obs,dim_state)
    ens_sen = np.zeros( (dim_time,dim_obs,dim_state), dtype=float )
    for itime in range(dim_time):

        for iobs,xobs in enumerate(obs):
            ind_obs_state = state.index( xobs )

            for istate in range(dim_state):
                # corr(ens_xobs,ens_xstate) * stdev(ens_xstate) / stdev(ens_xobs)
                ens_xstate = ens_TS[:,itime,       istate]
                ens_xobs   = ens_TS[:,itime,ind_obs_state]
                ens_sen[itime,iobs,istate] = np.corrcoef( ens_xstate, ens_xobs )[0,1] *    \
                                             np.std(ens_xstate) / np.std(ens_xobs)


    return ens_sen

def apply_inflation( ensemble, lambd, locz ):
    '''
    Apply the inflation coefficient to each ensemble member
    a security clamping is also applied to reset negatives values to their original values
    (just in case), this should not happen if posdef_infl() is used, see below

    :param numpy.ndarray ensemble: the ensemble distribution of dimensions (n ensembles, m state_variables)
    :param float lambd: the inflation coefficient

    :return: inflated distribution
    :rtype: <numpy.ndarray> dimensions (n ensembles, m state_variables)
    '''

    ensemble_infl = np.zeros_like( ensemble, dtype=float )

    ensemble_mean = ensemble.mean( axis=0 )

    for ens in range( ensemble_infl.shape[0] ):
        for istate in range( ensemble_infl.shape[1] ):
            xens_mem  = ensemble     [ens,istate]
            xens_mean = ensemble_mean    [istate]

            lambd_loc=max(locz[istate] * lambd, 1.0)

            xinfl = np.sqrt(lambd_loc) * (xens_mem - xens_mean) + xens_mean

            #this condition should not be reach if posdef_infl is used...
            if xinfl < 0.0:
                ensemble_infl[ens,istate] = ensemble[ens,istate]
            else:
                ensemble_infl[ens,istate] = xinfl

    return ensemble_infl

def posdef_infl( ensemble, lambd, locz ):
    '''
    Filter the inflation coefficient to ensure that the inflated ensemble
    distribution is positive definite, this will avoid clamping on ensemble members
    and then ensure a more physical evolution of the ensemble

    :param numpy.ndarray ensemble: the ensemble distribution of dimensions (n ensembles, m state_variables)
    :param float lambd: the inflation coefficient

    :return: lambd, the filtered inflation coefficient
    :rtype: float
    '''

    ensemble_mean = ensemble.mean( axis=0 )

    for ens in range( ensemble.shape[0] ):
        for istate in range( ensemble.shape[1] ):
            xens_mem  = ensemble     [ens,istate]
            xens_mean = ensemble_mean    [istate]

            lambd_loc=max(locz[istate] * lambd, 1.0)

            xinfl = np.sqrt(lambd_loc) * (xens_mem - xens_mean) + xens_mem

            t_lambd = (xens_mean/(xinfl - xens_mean))**2

            if lambd_loc > t_lambd:
                print('lambd def pos adjust :: {:f} {:f}'.format(lambd_loc, max(t_lambd,1.0)))
                lambd = lambd_loc * t_lambd/lambd_loc
#            lambd=max(lambd,1.0)

    return lambd

def calc_infl_simple( mod_obs_mean, mod_err, obs_val, obs_err, lambd, lambd_var ):
    '''
    Naive / simple way of estimating the inflation factor

    :param float mod_obs_mean: ensemble mean
    :param float mod_err: ensemble spread
    :param float obs_val: observation value
    :param float obs_err: observation error
    :param float lambd: (unused)
    :param float lambd_var: (unused)

    :return: lambd, inflation value
    :rtype: float
    '''
    lambd = ((mod_obs_mean-obs_val)**2 - obs_err**2) / mod_err**2

    if lambd > 1.0:
        lambd = lambd[0]
    else:
        lambd = 1.0

    return lambd, lambd_var

def _norm_pdf(x, loc, scale):
    # see scipy documentation for scipy.stats.norm
    y   = (x - loc) / scale
    res = np.exp(-y**2/2)/np.sqrt(2*np.pi)
    return res/scale

def calc_infl( mod_obs_mean, mod_err, obs_val, obs_err, lambd, lambd_var ):
    '''
    Estimation of the inflation value following Anderson(2006)

    :param float mod_obs_mean: ensemble mean
    :param float mod_err: ensemble spread
    :param float obs_val: observation value
    :param float obs_err: observatio error

    :return: lambd, inflation value
    :return: lambd_var: inflation variance value
    :rtype: float, float
    '''

    dim_obs = len(obs_val)

    obs_var = obs_err**2     # shape :: (dim_obs)
    mod_var = mod_err**2     # shape :: (dim_obs)

    # Anderson(2006); paragraph before eq. (5.8)
    D_sq    = abs(obs_val - mod_obs_mean)**2    # shape :: (dim_obs)

    for iobs in range(dim_obs):
        # (A.8) in Anderson (2006)----------------------------
        poly = [1.0                                             ,
                -(obs_var[iobs] + lambd * mod_var[iobs])        ,
                0.5 * lambd_var * mod_var[iobs]**2              ,
                -0.5 * lambd_var * mod_var[iobs]**2 * D_sq[iobs]]

        theta_sq_com = np.roots( poly )

        # From Anderson(2006): If there is only one real value take this one, if there are several
        # real values take the one nearest to lambda_prior
        theta_sq_real = [xtheta_sq.real for xtheta_sq in theta_sq_com if xtheta_sq.imag==0.0]
        if len(theta_sq_real)==1:
            theta_sq = theta_sq_real[0]

        elif len(theta_sq_real)>1:
            diff = 9.999E9
            for xtheta_sq_real in theta_sq_real:
                xdiff = abs(lambd - xtheta_sq_real)
                if xdiff<diff:
                    theta_sq = xtheta_sq_real*1.0
                    diff     = xdiff*1.0

        else:
            raise ValueError('Inflation :: No real theta**2')
        # ----------------------------------------------------


        # (A.7) in Anderson:
        lambd_post = (theta_sq - obs_var[iobs]) / mod_var[iobs]

        # In Anderson: Chapter "Adaptive Inflation"; paragraph before eq. (5.10)
#        lambd_distr = scipy.stats.norm(loc=lambd, scale=lambd_var)
#        R = lambd_distr.pdf( lambd_post+lambd_var ) / lambd_distr.pdf( lambd_post )
        lambd_distr_pdf = lambda x: _norm_pdf(x, lambd, lambd_var)
        R = lambd_distr_pdf( lambd_post+lambd_var ) / lambd_distr_pdf( lambd_post )

        # Anderson; eq. (5.10)
        lambd_var_post = - lambd_var / 2.0 / np.log(R)

        # Observations are processed sequentially:
        lambd, lambd_var = lambd_post*1.0, lambd_var_post*1.0

    return lambd, lambd_var

def print_table ( col_names, *col_values ):
    '''
    A table is printed, like this::

        col_names [0]     col_names [1]     ...
        col_values[0][1]  col_values[1][1]  ...
        col_values[0][2]  col_values[1][2]  ...
             ...                ...

    :param str/list col_names: column name/s
    :param list col_values: values of a column; first <col_values>
            corresponds to first <col_names> and so on
    '''

    if type(col_names)==list:
        col_space = 2

        # Define column width----------------------------------------------------
        cols = [[xcol_name] for xcol_name in col_names]
        for icol,xcol in enumerate(cols):
            cols[icol].extend( col_values[icol] )

        for icol,xcol in enumerate(cols):
            for jcol,ycol in enumerate(xcol):
                try:
                    # Float values are always displayed in the same format
                    cols[icol][jcol] = '{0:1.4e}'.format(ycol)
                except ValueError:
                    cols[icol][jcol] =       '{}'.format(ycol)

        # If the last column name is empty (='') the entries won't influence the
        # column  width
        cols_h = cols[:-1] if col_names[-1]=='' else cols
        col_width = max( [max( map(len, xcol) ) for xcol in cols_h] ) + col_space
        #------------------------------------------------------------------------

        # Print everything:
        for xcol in zip(*cols):
            for ycol in xcol:
                print ycol.ljust(col_width),
            print("")

    # If there is only one column a special table will be plotted:
    else:
        print(col_names.ljust(12)+'::  ' + col_values[0][0])
        for xcol_value in col_values[0][1:]:
            print(''.center(len(col_names.ljust(12)+'::  ')) + xcol_value)

    return

def loc_func( state, localization ):
    '''
    Defines a localization function between variables
    '''
    func = []

    for istate in state:
        if istate in localization: func.append(float(1.0))
        else: func.append(float(0.0))

    return np.array(func)

def load_config( cfgFile ):
    '''
    Read parameters from the settings.cfg file

    :param str cfgFile: settings.cfg file

    :return: * mech_NR <str> : nature run mechanism
             * mech_CR <str> : control run and assimilation runs mechanism
             * runDir <str> : running directory
             * nens <int> :  number of ensembles
             * state <list> : list of the state vector variables
             * obs <list> or <str> : observed variable(s)
             * localization <list> or <str> : list of variables to infer
             * is_obs_rel <bool>  : if True, the observation error is a fraction of
                the obs value (relative) obs error = obs * rel_obs_err
                if False, then the observation error is an absolute value obs error = abs_obs_err
             * rel_obs_err <float> : relative obs error
             * abs_obs_err <float> : absolute obs error
             * mod_err_coef_in <float> : for the single adjoint diagonal value of B diag(B) = mod_err_coef_in * H(x)
             * use_inflation <bool> : True: inflation is used, False: no inflation
             * prior_lambd_ens <float> : initial inflation, will change through cycles
             * prior_lambd_hyb <float> : initial inflation, will change through cycles
             * prior_lambd_var_ens <float> : initial inflation, will change through cycles
             * prior_lambd_var_hyb <float> : initial inflation, will change through cycles
             * verbose <bool> : verbose output?

    '''

    config = ConfigParser.ConfigParser()
    config.read(cfgFile)

    section = 'Global'
    mech_NR = config.get(section, 'mech_NR')
    mech_CR = config.get(section, 'mech_CR')

    nens = config.getint(section, 'nens')

    section = 'BEATBOX'

    state = str_to_list( config.get(section, 'state'), dtype=str )

    obs             = str_to_list( config.get(section, 'obs'         ), dtype=str   )
    localization    = str_to_list( config.get(section, 'localization'), dtype=str   )
    is_obs_rel     = config.getboolean(section, 'is_obs_rel' )
    rel_obs_err     = str_to_list( config.get(section, 'rel_obs_err' ), dtype=float )
    abs_obs_err     = str_to_list( config.get(section, 'abs_obs_err' ), dtype=float )
    mod_err_coef_in = str_to_list( config.get(section, 'mod_err_coef'), dtype=str   )

    use_inflation       = config.getboolean(section, 'inflation'    )
    prior_lambd_ens     = config.getfloat  (section, 'lambd_ens'    )
    prior_lambd_var_ens = config.getfloat  (section, 'lambd_var_ens')
    prior_lambd_hyb     = config.getfloat  (section, 'lambd_hyb'    )
    prior_lambd_var_hyb = config.getfloat  (section, 'lambd_var_hyb')

    verbose = config.getboolean(section, 'verbose')

    # Check configuration -------------------------------------------------------------------
    # Every species in <obs> must have its own <rel_obs_err> and <mod_err_coef>:
    if len(obs)!=len(rel_obs_err) or len(obs)!=len(mod_err_coef_in):
        raise IOError( '<obs>, <rel_obs_err>, and <mod_err_coef> must have the same size' )
    # Every species in <obs> must also be a species in the <state> vector
    for xobs in obs:
        if not xobs in state:
            raise IOError('Every species in <obs> must be part of the <state> vector')

    return mech_NR, mech_CR, nens, state, obs, localization, \
           is_obs_rel, rel_obs_err, abs_obs_err, mod_err_coef_in, \
           use_inflation, prior_lambd_ens, prior_lambd_hyb, prior_lambd_var_ens,       \
           prior_lambd_var_hyb, verbose

def translate_spec_list( translator, spec_list, mech_NR, mech_CR ):
    '''
    Operate name translations for NR, CR and ARs using the chemspectranslator

    :param str/list spec_list: Species list
    :param str mech_NR: Nature run mechanism name
    :param str mech_CR: Control run mechanism name
    :return: translated species by mechanism
    :rtype: dict
    '''

    spec_NR, spec_CR = [], []
    for xspec in spec_list:
        try:
            xspec_NR = translator.translate( xspec, mech_CR, mech_NR )
            if len(xspec_NR.result) == 1:
                spec_NR.append( xspec_NR.result[0][1] )
            else:
                raise Exception('Species "{:s}" is not unique in NR mechanism "{:s}"'.format(xspec, mech_NR))
        except:
            spec_NR.append( xspec )

        try:
            xspec_CR = translator.translate( xspec, mech_NR, mech_CR )
            if len(xspec_CR.result) == 1:
                spec_CR.append( xspec_CR.result[0][1] )
            else:
                raise Exception('Species "{:s}" is not unique in CR mechanism "{:s}"'.format(xspec, mech_CR))
        except:
            spec_CR.append( xspec )

    return { mech_NR: spec_NR, mech_CR: spec_CR }

def read_conc_cycling ( translator, runDir, spec ):
    '''
    Read the concentration after the forecast is done for the
    analysis to be performed

    :param str runDir: where are the concentration files,
    :param str spec: state variable used in the analysis

    :return: concentration values and ensembles indexed by NR,CR,AR,var,hyb,ens
    :rtype: dict
    '''

    config = ConfigParser.ConfigParser()
    config.read( os.path.join(runDir,'settings.cfg') )
    mech_CR = config.get     ( 'Global' , 'mech_CR' )
    mech_NR = config.get     ( 'Global' , 'mech_NR' )
    nens    = config.getint  ( 'Global' , 'nens'    )
    runtime = config.getfloat( 'BOXMOX' , 'runtime' )
    nfcst   = config.getint  ( 'Cycling', 'nfcst'   )

    spec_dict = translate_spec_list( translator, [spec], mech_NR, mech_CR )
    specNR    = spec_dict[mech_NR][0]
    specCR    = spec_dict[mech_CR][0]

    def readAsList(fpath, spec, removeLast):
        out = boxmox.ConcentrationOutput(fpath, spec).simplified()
        if removeLast:
            out = out[:-1]
        return list(out)

    print 'Reading forecasts'

    NR, CR, EN, AR_var, AR_ens, AR_hyb = [], [], [], [], [], []
    for ifcst in range( 1, nfcst+1 ):
        print ifcst
        xrunDirCR = os.path.join(runDir,'fcst_{0:d}'.format(ifcst),mech_CR,'output')
        xrunDirNR = os.path.join(runDir,'fcst_{0:d}'.format(ifcst),mech_NR,'output')

        readNR = lambda fname, removeLast: readAsList(os.path.join(xrunDirNR,fname), specNR, removeLast)
        readCR = lambda fname, removeLast: readAsList(os.path.join(xrunDirCR,fname), specCR, removeLast)

        if ifcst==1:
            NR    .append( readNR('1NR.conc', True) )
            CR    .append( readCR('0CR.conc', True) )
            AR_var.append( readCR('0CR.conc', True) )

            singleTime = readAsList(os.path.join(xrunDirNR, '1NR.conc'), 'time', True)

        elif ifcst==nfcst:
            NR    .append( readNR('1NR.conc', False) )
            CR    .append( readCR('0CR.conc', False) )
            AR_var.append( readCR('0AR_var.conc', False) )
        else:
            NR    .append( readNR('1NR.conc', True) )
            CR    .append( readCR('0CR.conc', True) )
            AR_var.append( readCR('0AR_var.conc', True) )


        xEN, xAR_ens, xAR_hyb = [], [], []
        for ens in range( 1, nens+1 ):
            if ifcst==1:
                xEN    .append( readCR('{0:d}EN.conc'.format(ens), True) )
                xAR_ens.append( readCR('{0:d}EN.conc'.format(ens), True) )
                xAR_hyb.append( readCR('{0:d}EN.conc'.format(ens), True) )
            elif ifcst==nfcst:
                xEN    .append( readCR('{0:d}EN.conc'    .format(ens), False) )
                xAR_ens.append( readCR('{0:d}AR_ens.conc'.format(ens), False) )
                xAR_hyb.append( readCR('{0:d}AR_hyb.conc'.format(ens), False) )
            else:
                xEN    .append( readCR('{0:d}EN.conc'    .format(ens), True) )
                xAR_ens.append( readCR('{0:d}AR_ens.conc'.format(ens), True) )
                xAR_hyb.append( readCR('{0:d}AR_hyb.conc'.format(ens), True) )

        EN    .append( np.array(xEN    ) )
        AR_ens.append( np.array(xAR_ens) )
        AR_hyb.append( np.array(xAR_hyb) )

    ev_NR     = np.concatenate( NR    , axis=0 )
    ev_CR     = np.concatenate( CR    , axis=0 )
    ev_AR_var = np.concatenate( AR_var, axis=0 )

    EN     = np.concatenate( EN    , axis=1 ); ev_EN     = EN.mean( axis=0 )
    AR_ens = np.concatenate( AR_ens, axis=1 ); ev_AR_ens = AR_ens.mean( axis=0 )
    AR_hyb = np.concatenate( AR_hyb, axis=1 ); ev_AR_hyb = AR_hyb.mean( axis=0 )

    time = []
    for ifcst in range(nfcst):
        time += [ x + (float(ifcst)*runtime) for x in singleTime ]
    if nfcst > 1:
        time += [ float(nfcst)*runtime ]

    return {'ev_NR':ev_NR, 'ev_CR'    :ev_CR         , 'ev_AR_var':ev_AR_var,\
            'ev_EN':ev_EN, 'ev_AR_ens':ev_AR_ens     , 'ev_AR_hyb':ev_AR_hyb,\
            'EN'   :EN   , 'AR_ens'   :AR_ens        , 'AR_hyb'   :AR_hyb   ,\
            'spec' :spec , 'time'     :np.array(time), 'runtime'  :runtime  ,\
            'nfcst':nfcst }

def load_obs_cycling ( runDir ):
    '''
    Read the observation parameters from the BEATBOX.p on a given cycle

    :param str runDir: where the file to read is

    :return: obs parameters
    :rtype: dict
    '''
    num_of_fcst = len( glob.glob(os.path.join(runDir,'fcst_*')) )

    obs_val, obs_err = [], []
    for ifcst in range( 1, num_of_fcst ):
        xdata = pickle.load( open(os.path.join(runDir,'fcst_{0:d}'.format(ifcst),'BEATBOX.p'),'rb') )

        obsCR  , obsNR = xdata['obs_CR' ], xdata['obs_NR']
        rel_obs_err    = xdata['rel_obs_err']

        obs_val.append( xdata['obs_val'] )
        obs_err.append( xdata['obs_err'] )

    obs_val = np.concatenate( obs_val, axis=0 )
    obs_err = np.concatenate( obs_err, axis=0 )

    return {'obsCR':obsCR, 'obsNR':obsNR, 'obs_err':obs_err,\
            'rel_obs_err':rel_obs_err, 'obs_val':obs_val    }

