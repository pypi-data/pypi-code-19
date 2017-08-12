#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import copy
try:
    import cPickle as pickle
except:
    import pickle

import numpy as np

import boxmox

from . import helpers

def run ( translator, exp_path ):

    '''
    This is the main function of the data assimilation code,
    organized as follows:

    - loading concentrations
    - calculating sensitivities
    - generating observations
    - inflate ensembles if necessary
    - compute the analysis
    - write the outputs
    '''

    mech_NR, mech_CR, nens, state, obs, localization, \
    is_obs_rel, rel_obs_err, abs_obs_err, mod_err_coef_in, \
    use_inflation, prior_lambd_ens, prior_lambd_hyb, prior_lambd_var_ens,       \
    prior_lambd_var_hyb, verbose =                        \
    helpers.load_config( os.path.join(exp_path, 'settings.cfg') )

    # Process adjustments -------------------------------------------------------------------
    path_CR = os.path.join(exp_path,mech_CR,'output')
    path_NR = os.path.join(exp_path,mech_NR,'output')

    # Get some dimensions:
    dim_obs   = len(obs)
    dim_state = len(state)
    dim_ens   = nens*1

    # Index of the <obs>erved species in the <state> vector:
    ind_obs_state = [state.index(xobs) for xobs in obs]

    # Species names in the <mech_CR> chemical mechanism may differ from the corresponding
    # species names in the <mech_NR> chemical mechansim:
    obs_dict = helpers.translate_spec_list( translator, obs, mech_NR, mech_CR )
    obs_CR   = obs_dict[mech_CR]
    obs_NR   = obs_dict[mech_NR]

    state_dict = helpers.translate_spec_list( translator, state, mech_NR, mech_CR )
    state_CR   = state_dict[mech_CR]
    state_NR   = state_dict[mech_NR]

    # It is more comfortable to work with <numpy.ndarray>:
    rel_obs_err = np.array( rel_obs_err )
    abs_obs_err = np.array( abs_obs_err )


    #########################################################################################
    # Output of BEATBOX:                                                                    #
    BEATBOX = {}                                                                            #
    #                                                                                       #
    # The concentrations (in ppmv) of the species in the state vector at t_final and the    #
    # configuration will be saved:                                                          #
    #                                                                                       #
    # data type <numpy.ndarray> (key :: description :: shape):                              #
    #  concentrations in ppmv:                                                              #
    #  - "ev_NR"        :: Nature Run                                ::         (dim_state) #
    #  - "ev_CR"        :: Control Run                               ::         (dim_state) #
    #  - "EN"           :: for each ENsemble member                  :: (dim_ens,dim_state) #
    #  - "ev_EN"        :: ENsemble mean                             ::         (dim_state) #
    #  - "ev_AR_var"    :: Assimilation Run VARiational              ::         (dim_state) #
    #  - "AR_ens"       :: Assimilation Run ENSemble for each member :: (dim_ens,dim_state) #
    #  - "ev_AR_ens"    :: Assimilation Run ENSemble                 ::         (dim_state) #
    #  - "AR_hyb"       :: Assimilation Run HYBrid for each member   :: (dim_ens,dim_state) #
    #  - "ev_AR_hyb"    :: Assimilation Run HYBrid                   ::         (dim_state) #
    #  - "obs_val"      :: OBServation VALue                         ::           (dim_obs) #
    #  sensitivities:                                                                       #
    #  - "CR_adj_sen"   :: Control Run ADJoint SENsitivity   ::         (dim_obs,dim_state) #
    #  - "EN_adj_sen"   :: ENsemble ADJoint SENsitivity      :: (dim_ens,dim_obs_dim_state) #
    #  - "EN_ens_sen"   :: ENsemble ENSemble SENsitivity     ::         (dim_obs,dim_state) #
    #  error coefficients:                                                                  #
    #  - "obs_err"      :: OBServation ERRor                         ::           (dim_obs) #
    #  - "rel_obs_err"  :: RELative OBServation ERRor                ::           (dim_obs) #
    #  - "abs_obs_err"  :: ABSolute OBServation ERRor                ::           (dim_obs) #
    #  - "mod_err_coef" :: MODel ERRor COEFficient                   ::           (dim_obs) #
    #  - "mod_err_var"  :: MODel ERRor of AR VARiational             ::           (dim_obs) #
    #  - "mod_err_ens"  :: MODel ERRor of AR ENSemble                ::           (dim_obs) #
    #  - "mod_err_hyb"  :: MODel ERRor of AR HYBrid                  ::           (dim_obs) #
    #                                                                                       #
    # data type <list> (key :: description :: shape):                                       #
    #  - "obs_CR"       :: OBServation in the Control Run mechanism  ::           (dim_obs) #
    #  - "obs_NR"       :: OBServation in the Nature Run mechanism   ::           (dim_obs) #
    #  - "state_CR"     :: STATE in the Control Run mechanism        ::         (dim_state) #
    #  - "state_NR"     :: STATE in the Nature Run mechanism         ::         (dim_state) #
    #                                                                                       #
    # data type <int> (key :: description):                                                 #
    #  - "nens"         :: Number of ENSembles                                              #
    #                                                                                       #
    # data type <str> (key :: description):                                                 #
    #  - "mech_NR"      :: Nature Run chemical MECHanism                                    #
    #  - "mech_CR"      :: Control Run chemical MECHanism                                   #
    #                                                                                       #
    # data type <dict> or <bool> (key :: # case -> data type: content):                     #
    #  - "inflation" :: 1. If inflation is used -> <dict> (key :: description;data type):   #
    #                      + "prior_lambd_ens"/"post_lambd_ens" ::                          #
    #                              prior/posterior inflation factor of AR ENSemble; <float> #
    #                      + "prior_lambd_var_ens"/"post_lambd_var_ens" ::                  #
    #                              prior/posterior VARiance of the inflation factor of AR   #
    #                              ENSemble; <float>                                        #
    #                      + "prior_lambd_hyb"/"post_lambd_hyb" ::                          #
    #                              prior/posterior inflation factor of AR HYBrid; <float>   #
    #                      + "prior_lambd_var_hyb"/"post_lambd_var_hyb" ::                  #
    #                              prior/posterior VARiance of the inflation factor of AR   #
    #                              HYBrid; <float>                                          #
    #                   2. If inflation is not used -> <bool>: False                        #
    #                                                                                       #
    #                                                                                       #
    # Save configuration:                                                                   #
    BEATBOX['mech_CR'    ] = mech_CR                                                        #
    BEATBOX['mech_NR'    ] = mech_NR                                                        #
    BEATBOX['obs_CR'     ] = obs_CR                                                         #
    BEATBOX['obs_NR'     ] = obs_NR                                                         #
    BEATBOX['state_CR'   ] = state_CR                                                       #
    BEATBOX['state_NR'   ] = state_NR                                                       #
    BEATBOX['nens'       ] = nens                                                           #
    BEATBOX['rel_obs_err'] = rel_obs_err                                                    #
    BEATBOX['abs_obs_err'] = abs_obs_err                                                    #
    #                                                                                       #
    # Save prior inflation factors:                                                         #
    inflation = {}
    if use_inflation:                                                                       #
        inflation['prior_lambd_ens'    ] = prior_lambd_ens                                  #
        inflation['prior_lambd_var_ens'] = prior_lambd_var_ens                              #
        inflation['prior_lambd_hyb'    ] = prior_lambd_hyb                                  #
        inflation['prior_lambd_var_hyb'] = prior_lambd_var_hyb                              #
    #########################################################################################




    ######################## 1.1 CONCENTRATION TIME SERIES ##################################

    #----------------------------------------------------------------------------------------
    # Concentration output files are '<ensTag><nameTag>.conc'
    #                                      ensTag:     nameTag:
    # Nature Run                   ::            1           NR
    # Control Run                  ::            0           CR
    # ENsemble                     ::   1 - <nens>           EN
    # Assimilation Run VARiational ::            0       AR_var
    # Assimilation Run ENSemble    ::   1 - <nens>       AR_ens
    # Assimilation Run HYBrid      ::   1 - <nens>       AR_hyb
    #----------------------------------------------------------------------------------------


    # Nature Run/Control Run; shape :: (dim_time,dim_state)
    NR = boxmox.ConcentrationOutput( os.path.join(path_NR,'1NR.conc'), state_NR ).simplified()
    CR = boxmox.ConcentrationOutput( os.path.join(path_CR,'0CR.conc'), state_CR ).simplified()

    dim_time = NR.shape[0]

    # ENsemble; shape :: (dim_nens,dim_time,dim_state)
    EN = np.zeros( (dim_ens,dim_time,dim_state), dtype=float )
    for ens in range(nens):
        # Ensemble files: 1EN.conc until <nens>.conc -> when loading files "ens+1"
        EN[ens,:,:] = boxmox.ConcentrationOutput ( os.path.join(path_CR,'{0:d}EN.conc'.format(ens+1)), state_CR ).simplified()

    # Save concentrations at t_final:
    BEATBOX['ev_NR'    ] = NR[-1,:].copy()
    BEATBOX['ev_CR'    ] = CR[-1,:].copy()
    BEATBOX['ev_EN'    ] = EN[:,-1,:].mean(axis=0)
    BEATBOX[   'EN'    ] = EN[:,-1,:].copy()


    # This try-except block is for successive forecasts:
    # If there are runs with nameTag 'AR_var', 'AR_ens', and 'AR_hyb' in <path_CR> these
    # output files will be taken and used for data assimilation (the tags 'CR' and 'EN' will
    # be ignored regarding to data assimilation). If there are ONLY runs with tag 'CR' and
    # 'EN' in the <path_CR> these output files will be used.
    try:
        CR_var = boxmox.ConcentrationOutput ( os.path.join(path_CR,'0AR_var.conc'), state_CR ).simplified()
        EN_ens = np.zeros( (dim_ens,dim_time,dim_state), dtype=float )
        EN_hyb = np.zeros( (dim_ens,dim_time,dim_state), dtype=float )
        for ens in range(nens):
            # Ensemble files: 1EN.conc until <nens>.conc -> when loading files "ens+1"
            EN_ens[ens,:,:] = boxmox.ConcentrationOutput (os.path.join(path_CR,'{0:d}AR_ens.conc'.format(ens+1)), state_CR).simplified()
            EN_hyb[ens,:,:] = boxmox.ConcentrationOutput (os.path.join(path_CR,'{0:d}AR_hyb.conc'.format(ens+1)), state_CR).simplified()
    except IOError:
        # If there are NO files with nameTag 'AR_var','AR_ens', and 'AR_hyb':
        # Variational(var)/ensemble(ens)/hybrid(hyb) method uses data with nameTag CR/EN/EN
        CR    , EN_ens , EN_hyb  =     CR[:,:],     EN[:,:,:],     EN[:,:,:]
        tag_CR, tag_ens, tag_hyb =        'CR',          'EN',          'EN'
    else:
        # If there are files with nameTag 'AR_var','AR_ens, 'AR_hyb':
        # Variational(var)/ensemble(ens)/hybrid(hyb) method uses data with nameTag AR_var/
        # AR_ens/AR_hyb
        CR    , EN_ens , EN_hyb  = CR_var[:,:], EN_ens[:,:,:], EN_hyb[:,:,:]
        tag_CR, tag_ens, tag_hyb =    'AR_var',      'AR_ens',      'AR_hyb'


    # Prior states at t_final:
    BEATBOX['ev_AR_var_prior'] = CR      [-1,:]
    BEATBOX['ev_AR_ens_prior'] = EN_ens[:,-1,:].mean(axis=0)
    BEATBOX[   'AR_ens_prior'] = EN_ens[:,-1,:]
    BEATBOX['ev_AR_hyb_prior'] = EN_hyb[:,-1,:].mean(axis=0)
    BEATBOX[   'AR_hyb_prior'] = EN_hyb[:,-1,:]
    ##################################### END OF 1.1 ########################################



    ################################# 1.2 Sensitivities #####################################



    ###### 1.2.1 Adjoint sensitivities:

    #----------------------------------------------------------------------------------------
    # Adjoint output files are '<ensTag><nameTag>.ADJ_results.m' (<ensTag> and <nameTag> as
    # above)
    #
    # The adjoints in the adjoint output files represent: dX(t_final)/dY(t_initial)
    # By using the chain rule the adjoint sensitivity of species X to species Y at t_final
    # can be calculated:
    #
    # dX(t_final)/dY(t_final) = dX(t_final)/dY(t_initial) * (dY(t_final)/dY(t_initial))^-1
    #
    #----------------------------------------------------------------------------------------

    # Control Run ADJoint SENSitivity; shape :: (dim_obs,dim_state)
    CR_ADJ     = boxmox.AdjointOutput(os.path.join(path_CR,'0{0:s}.adjoint'.format(tag_CR)), state_CR)
    CR_adj_sen = CR_ADJ.sensitivity( state_CR, obs_CR )

    # ENsemble ADJoint SENSitivity; shape :: (dim_ens,dim_obs,dim_state)
    EN_adj_sen = np.zeros( (dim_ens,dim_obs,dim_state), dtype=float )
    for ens in range(nens):
        # Ensemble files: 1EN.conc until <nens>.conc -> when loading files "ens+1"
        xADJ                = boxmox.AdjointOutput(os.path.join(path_CR,'{0:d}{1:s}.adjoint'.format(ens+1, tag_hyb)), state_CR)
        EN_adj_sen[ens,:,:] = xADJ.sensitivity( state_CR, obs_CR )



    ##### 1.2.2 Ensemble sensitivity:

    #----------------------------------------------------------------------------------------
    # The ensemble sensitivity of species X to species Y can be calculated at every timestep.
    # If x is an ensemble of concentrations of species X at time t and y is an ensemble of
    # concentrations of species Y at time t the ensemble sensitivity of X to Y at t is:
    #
    #                       corr(x,y) * stdev(x) / stdev(y)
    #
    #----------------------------------------------------------------------------------------


    # ENsemble ENSemble SENsitvity; shape :: (dim_time,dim_obs,dim_state)
    EN_ens_sen = helpers.calc_ens_sen( EN_ens, state_CR, obs_CR )
    # <EN_ens_sen> at t_final -> shape :: (dim_obs,dim_state)
    EN_ens_sen = EN_ens_sen[-1,:,:]


    #####
    BEATBOX['CR_adj_sen'] = CR_adj_sen  [:,:]
    BEATBOX['EN_adj_sen'] = EN_adj_sen[:,:,:]
    BEATBOX['EN_ens_sen'] = EN_ens_sen  [:,:]
    ####################################### END OF 1.2 ######################################



    #----------------------------------------------------------------------------------------
    # Just for convenience: Define a concentration state vector which only contains the
    # concentrations of the observed species at t_final:
    NR_obs     = NR      [-1,ind_obs_state]
    CR_obs     = CR      [-1,ind_obs_state]
    EN_ens_obs = EN_ens[:,-1,ind_obs_state]
    EN_hyb_obs = EN_hyb[:,-1,ind_obs_state]
    #----------------------------------------------------------------------------------------

    #call the localization function
    locz = helpers.loc_func ( state , localization )

    print("Localization function: {:s}".format(locz))

    #----------------------------------------------------------------------------------------
    ######################################## END OF 1. ######################################
    #----------------------------------------------------------------------------------------




    #########################################################################################
    #                                                                                       #
    #                             2. OBSERVATION GENERATOR                                  #
    #                                                                                       #
    #########################################################################################

    # Define perfect observations or with error from Nature Run:
    # In this idealized case observation is only defined at t_final

    # A random number for every observation ...
    obs_pert = np.random.normal( loc=0.0, scale=1.0, size=(len(obs),) )

    # Perfect observation: rel_obs_err=0.0 -> obs_val = NR_val
    if is_obs_rel:
        print("Relative obs error ({:s})".format(rel_obs_err))
        obs_val = obs_pert * rel_obs_err * NR_obs + NR_obs
        obs_err = 1.0      * rel_obs_err * NR_obs
    else:
        print("Absolute obs error ({:s})".format(abs_obs_err))
        obs_val = obs_pert * abs_obs_err + NR_obs
        obs_err = 1.0      * abs_obs_err

    #!!!!!!!!!!!!! TODO:FIXME !!!!!!!!!!!!!!
    # Currently negative observation values are treated very suboptimally - they are set to
    # zero
    obs_val = obs_val.clip(min=0.0)
    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


    #----------------------------------------------------------------------------------------
    if verbose:
        print(' OBSERVATION-GENERATOR '.center(70,'-')+'\n')

        descr = ['perfect observation' if xerr==0.0 else '' for xerr in rel_obs_err]
        helpers.print_table(['obs_spec:', 'NR_value [ppmv]:', 'obs_val [ppmv]:', 'obs_err:', ''  ],
                       obs       ,  NR_obs           ,  obs_val         ,  obs_err  , descr )
        print('\n'+''.center(70,'-')+'\n\n')
    #----------------------------------------------------------------------------------------

    #####
    BEATBOX['obs_err'] = obs_err[:]
    BEATBOX['obs_val'] = obs_val[:]
    ###################################### END OF 2. ########################################
    #----------------------------------------------------------------------------------------

    #########################################################################################
    #                                                                                       #
    #                             3. DATA ASSIMILATION                                      #
    #                                                                                       #
    #########################################################################################
    #                                                                                       #
    # 1. The Best Linear Unbiased Estimator (BLUE) is used to get the analysis of the       #
    #    observed species y_a (shape: (dim_obs)):                                           #
    #                                                                                       #
    #              y_a = (y_o*s_b^2 + y_b*s_o^2) / (s_b^2 + s_o^2)                          #
    #                                                                                       #
    #         where:    -  y_o  ::  observation value   (shape: (dim_obs))                  #
    #                   -  s_o  ::  observation error   (shape: (dim_obs))                  #
    #                   -  y_b  ::  model value         (shape: (dim_obs))                  #
    #                   -  s_b  ::  model error         (shape: (dim_obs))                  #
    #                                                                                       #
    #                                                                                       #
    # 2. The difference between model and analysis gives the increment of the observed      #
    #    species dy (shape: (dim_obs)):                                                     #
    #                                                                                       #
    #                            dy = y_a - y_b                                             #
    #                                                                                       #
    #                                                                                       #
    # 3. With a gain K (can be computed from the adjoint or the ensemble) (shape:           #
    #    (dim_obs,dim_state)) the increment of the remaining state dx (shape: (dim_state))  #
    #    can be computed (for every ensemble member):                                       #
    #                                                                                       #
    #                            dx = K \dot dy                                             #
    #                                                                                       #
    #                                                                                       #
    # 4. Finally the analysis of the whole state x_a (shape: (dim_state)) is calculated:    #
    #                                                                                       #
    #                            x_a = x_b + dx                                             #
    #                                                                                       #
    #                                                                                       #
    #########################################################################################



    ################################# 3.1 VARIATIONAL #######################################


    # Prior state    :     CR     (CR     shape: (dim_tim,dim_state))
    # Posterior state: AR_var     (AR_var shape:         (dim_state))
    AR_var = np.zeros( (dim_state), dtype=float )


    # For perfect observations (rel_obs_err=0.0) the model error is calculated but does
    # affect the result. The model error <mod_err_coef> can be set manually or calculated by
    # looking at the difference between NR and CR ("auto"):
    mod_err_coef = np.zeros( (dim_obs), dtype=float )
    for iobs,err_coef_xobs in enumerate(mod_err_coef_in):
        if err_coef_xobs=='auto':
            mod_err_coef[iobs] = abs(NR_obs[iobs] - CR_obs[iobs])/ CR_obs[iobs]
        else:
            mod_err_coef[iobs] = float( err_coef_xobs )

    # MODel ERRor VARiational = CR(t_final,xobs) * mod_err_coef(t_final,xobs)
    # shape :: (dim_obs)
    mod_err_var = CR_obs  * mod_err_coef


    # Analysis can be computed on the full time series but for now just on t_final...
    analy = (obs_val*mod_err_var**2 + CR_obs*obs_err**2) / (obs_err**2 + mod_err_var**2)
    incr  = analy - CR_obs

    # K (<CR_adj_sen>) from the single member adjoint of the CR (only at t_final) ...
    for istate in range(dim_state):
        AR_var[istate] = CR[-1,istate] + CR_adj_sen[:,istate].T .dot( incr.T ) * locz[istate]

        # Negative concentrations are reset to the original concentrations:
        if AR_var[istate]<0.0:
            AR_var[istate] = CR[-1,istate]


    # Save the results:
    BEATBOX['ev_AR_var'   ] = AR_var      [:]
    BEATBOX['mod_err_coef'] = mod_err_coef[:]
    BEATBOX['mod_err_var' ] = mod_err_var [:]
    del(AR_var)
    #----------------------------------------------------------------------------------------
    if verbose:
        print(' ASSIMILATION RUN: VARIATIONAL '.center(70,'-')+'\n')

        descr = ['from NR-CR' if xcoef=='auto' else '' for xcoef in mod_err_coef_in]
        helpers.print_table(['obs_spec:', 'mod_err_coef:', 'mod_err:'  , ''   ],
                        obs       ,  mod_err_coef  ,  mod_err_var, descr  )
        print('')
        helpers.print_table(['state:', 'NR [ppmv]:'     , 'CR [ppmv]:'     , 'AR_var [ppmv]:'     ],
                        state  ,  BEATBOX['ev_NR'],  BEATBOX['ev_CR'],  BEATBOX['ev_AR_var']  )
        print('\n'+''.center(70,'-')+'\n\n')
    ##################################### END OF 3.1 ########################################




    #################################### 3.2 ENSEMBLE #######################################
    # Prior state    : mean(EN_ens).axis(ens)    (EN_ens shape: (dim_ens,dim_time,dim_state))
    # Posterior state: mean(AR_ens).axis(ens)    (AR_ens shape: (dim_ens,         dim_state))
    AR_ens = np.zeros( (dim_ens,dim_state), dtype=float )


    if use_inflation:
        obs_mean = EN_ens_obs.mean(axis=0)
        mod_err  = EN_ens_obs.std (axis=0)

        #inflation calculation
        lambd_ens, lambd_var_ens = helpers.calc_infl_simple( obs_mean, mod_err, obs_val, obs_err,
                                                             prior_lambd_ens, prior_lambd_var_ens )

        #filter for adjusting inflation for keeping the distribution shape intact
        #and the positive-definitiveness
        lambd_ens = helpers.posdef_infl( EN_ens[:,-1,:], lambd_ens, locz )

        print('################INFLATION##################')
        print('lambd_ens      :: ' + str(lambd_ens))
        print('lambd_ens_var  :: ' + str(lambd_var_ens))
        print('###########################################')

        inflation['post_lambd_ens'    ] = lambd_ens
        inflation['post_lambd_var_ens'] = lambd_var_ens

        #apply inflation on each member
        EN_ens[:,-1,:] = helpers.apply_inflation( EN_ens[:,-1,:], lambd_ens, locz )
        EN_ens_obs     = EN_ens[:,-1,ind_obs_state]

    # Ensemble model errors are implicitly defined by the ensemble spread:
    mod_err_ens = EN_ens_obs.std(axis=0)

    for ens in range( nens ):

        # Increment on each ensemble member:
        analy = (obs_val*mod_err_ens**2 + EN_ens_obs[ens,:]*obs_err**2) / \
                            (obs_err**2 + mod_err_ens**2)
        incr  = analy - EN_ens_obs[ens,:]

        for istate in range( dim_state ):
            # K from ensemble sensitivity (K is the same for each member):
            try:
                AR_ens[ens,istate] = EN_ens[ens,-1,istate] + EN_ens_sen[:,istate].T .dot(incr.T) * locz[istate]
            except TypeError:
                print('spec :: ', state_CR[istate])
                print('ens  :: ', ens)
                print('EN_ens :: ', EN_ens[ens,-1,istate], ', shape :: ', EN_ens.shape)
                print('EN_ens_sen :: ', EN_ens_sen[:,istate], ', shape :: ', EN_ens_sen.shape)
                print('incr :: ', incr, ', incr :: ', incr.shape)

            # Negative concentrations are reset to their original concentrations:
            #(this condition should not be met anyways):
            if AR_ens[ens,istate]<0.0:
                AR_ens[ens,istate] = EN_ens[ens,-1,istate]




    # Save output:
    BEATBOX['ev_AR_ens'  ] = AR_ens.mean(axis=0) # shape ::         (dim_state)
    BEATBOX[   'AR_ens'  ] = AR_ens     [:,:]    # shape :: (dim_ens,dim_state)
    BEATBOX['mod_err_ens'] = mod_err_ens[:]
    del(AR_ens)
    #----------------------------------------------------------------------------------------
    if verbose:
        print(' ASSIMILATION RUN: ENSEMBLE '.center(70,'-')+'\n')
        helpers.print_table(['obs_spec:', 'mod_err:'  ],
                        obs       ,  mod_err_ens  )
        print("")
        helpers.print_table(['state:', 'NR [ppmv]:'     , 'EN [ppmv]:'     , 'AR_ens [ppmv]:'    ],
                        state  ,  BEATBOX['ev_NR'],  BEATBOX['ev_EN'],  BEATBOX['ev_AR_ens'])
        print('\n'+''.center(70,'-')+'\n\n')
    ##################################### END OF 3.2 ########################################




    ####################################### 3.3 HYBRID ######################################
    # Prior state    : mean(EN_hyb).axis(ens)    (EN_hyb shape: (dim_ens,dim_time,dim_state))
    # Posterior state: mean(AR_hyb).axis(ens)    (AR_hyb shape: (dim_ens,         dim_state))
    AR_hyb = np.zeros( (dim_ens,dim_state), dtype=float )

    if use_inflation:
        obs_mean = EN_hyb_obs.mean(axis=0)
        mod_err  = EN_hyb_obs.std (axis=0)

        #inflation calculation
        lambd_hyb, lambd_var_hyb = helpers.calc_infl_simple( obs_mean, mod_err, obs_val, obs_err,
                                                             prior_lambd_hyb, prior_lambd_var_hyb )

        #filter for adjusting inflation for keeping the distribution shape intact
        #and the positive-definitiveness
        lambd_hyb = helpers.posdef_infl( EN_hyb[:,-1,:], lambd_hyb, locz )

        print('#################INFLATION#################')
        print('lambd_hyb      :: ' + str(lambd_hyb))
        print('lambd_var_hyb  :: ' + str(lambd_var_hyb))
        print('###########################################')

        inflation['post_lambd_hyb'    ] = lambd_hyb
        inflation['post_lambd_var_hyb'] = lambd_var_hyb

        #apply inflation on each member
        EN_hyb[:,-1,:] = helpers.apply_inflation( EN_hyb[:,-1,:], lambd_hyb, locz )
        EN_hyb_obs     = EN_hyb[:,-1,ind_obs_state]

    # Ensemble model error are implicitly defined by the ensemble spread:
    mod_err_hyb = EN_hyb_obs.std(axis=0)

    # K from adjoint sensitivity (every member) and increment in each member:
    for ens in range( nens ):

        # Increment on each member:
        analy = (obs_val*mod_err_hyb**2 + EN_hyb_obs[ens,:]*obs_err**2) / \
                            (obs_err**2 + mod_err_hyb**2)
        incr  = analy - EN_hyb_obs[ens,:]

        for istate in range( dim_state ):
            # K from adjoint sensitivity (every member has its own K):
            AR_hyb[ens,istate] = EN_hyb[ens,-1,istate]+ EN_adj_sen[ens,:,istate].T.dot(incr.T) * locz[istate]

            # Negative concentrations are reset to the original concentrations
            # (this condition should not be met anyways):
            if AR_hyb[ens,istate]<0.0:
                AR_hyb[ens,istate] = EN_hyb[ens,-1,istate]



    # Save output:
    BEATBOX['ev_AR_hyb'  ] = AR_hyb.mean(axis=0) # shape ::         (dim_state)
    BEATBOX[   'AR_hyb'  ] = AR_hyb     [:,:]    # shape :: (dim_ens,dim_state)
    BEATBOX['mod_err_hyb'] = mod_err_hyb[:]
    del(AR_hyb)
    #----------------------------------------------------------------------------------------
    if verbose:
        print(' ASSIMILATION RUN: HYBRID '.center(70,'-')+'\n')
        helpers.print_table(['obs_spec:', 'mod_err:'  ],
                             obs       ,  mod_err_hyb  )
        print("")
        helpers.print_table(['state:', 'NR [ppmv]:'     , 'EN [ppmv]:'     , 'AR_hyb [ppmv]:'    ],
                             state  ,  BEATBOX['ev_NR'],  BEATBOX['ev_EN'],  BEATBOX['ev_AR_hyb'])
        print('\n'+''.center(70,'-')+'\n\n')
    ##################################### END OF 3.3 ########################################

    if use_inflation:
        BEATBOX['inflation']     = inflation

    #----------------------------------------------------------------------------------------
    ###################################### END OF 3. ########################################
    #----------------------------------------------------------------------------------------


    # Save output:
    pickle.dump( BEATBOX, open( os.path.join(exp_path,'BEATBOX.p'), 'wb' ) )

    return
