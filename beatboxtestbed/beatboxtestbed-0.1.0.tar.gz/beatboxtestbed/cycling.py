#!/usr/bin/env python
# -*- coding: utf-8 -*-

#########################################################################################
#                                                                                       #
#         This routine creates new multiMOX initial conditions files from               #
#               multiMOX concentration output files involving BEATBOX                   #
#                                                                                       #
#########################################################################################
#                                                                                       #
# After the first multiMOX forecast:                                                    #
#           output:                          new input:                                 #
#      ("*.conc"-files)           ("*_InitialConditions_*.csv"-files)                   #
#                                                                                       #
#             NR        ---------------->       NR                                      #
#                                                                                       #
#                         ,------------->       CR                                      #
#             CR        --|                                                             #
#                         `-- BEATBOX -->       AR_var                                  #
#                                                                                       #
#                         ,------------->       EN                                      #
#             EN        --|-- BEATBOX -->       AR_ens                                  #
#                         `-- BEATBOX -->       AR_hyb                                  #
#                                                                                       #
#---------------------------------------------------------------------------------------#
#                                                                                       #
# The second / n'th multiMOX forecast:                                                  #
#           output:                          new input:                                 #
#      ("*.conc"-files)           ("*_InitialConditions_*.csv"-files)                   #
#                                                                                       #
#             NR        ---------------->       NR                                      #
#                                                                                       #
#             CR        ---------------->       CR                                      #
#             AR_var    ----- BEATBOX -->       AR_var                                  #
#                                                                                       #
#             EN        ---------------->       EN                                      #
#             AR_ens    ----- BEATBOX -->       AR_ens                                  #
#             AR_hyb    ----- BEATBOX -->       AR_hyb                                  #
#                                                                                       #
#########################################################################################


import os
import shutil as s
import glob
import ConfigParser
try:
    import cPickle as pickle
except:
    import pickle

import boxmox

from . import beatbox
from . import helpers
from . import multimox

def new_experiment(exp):
    '''
    Create directory for a new experiment
    '''
    try:
        exp_path = helpers.make_exp_path(exp, createDir=True, overwrite=True)
        s.copy(helpers.default_config_path, os.path.join(exp_path, "settings.cfg"))
    except:
        raise Exception('Could not create new experiment.')

    return exp_path

def remove_experiment(exp):
    '''
    Remove directories from a given experiment
    '''
    exp_path = helpers.make_exp_path(exp)

    if os.path.isdir(exp_path):
        shutil.rmtree(exp_path)

    return True

def create_input_from_output ( fname, conc_state, out ):
    '''
    A BOXMOX concentration output file is taken and with the final
    concentrations a new BOXMOX initial conditions file is written. The final
    concentrations of some species can be replaced in the new input file.

    :param str fname: BOXMOX concentration output file
    :param dict conc_state: Concentrations to be replaced in the new input file
        (species name must be part of the species in the BOXMOX concentration output file)
    :param str out: a new BOXMOX initial conditions filename which will be generated
    '''
    #--------------------------------------------------------
    # Read concentration file ...
    input      = boxmox.ConcentrationOutput( fname )
    # remove 'time' item
    specNames = [x for x in input.vars if not x == 'time' ]
    input      = input[ specNames ]

    # get final concentrations
    conc_final = input[-1].copy()

    # Replace final concentrations with the one from <conc_state>:
    for xspec in conc_state:
        conc_final[xspec] = conc_state[xspec]

    #--------------------------------------------------------
    # Write new multiMOX input file ...
    res             = boxmox.InputFile()
    res.timeFormat = 0
    res[specNames] = conc_final
    with open( out, 'w' ) as f:
        res.write(f)

    return

def get_ens_tag ( fname ):
    '''
    The ensemble tag of a multiMOX output file is computed from its filename.

    :param str fname: multiMOX output file
    :return: the ensemble tag of that file
    :rtype: int
    '''

    ind = 1
    fname = os.path.basename(fname)

    # "Count" the number of digits of the ensTag:
    while fname[:ind].isdigit():
        ind +=1

    return int(fname[:(ind-1)])

def gen_ass_IC (exp, ifcst):
    '''
    Generate new initial condition from an analysis to run subsequent forecast

    :param str exp: name of the experiment
    :param int ifcst: forecast number
    '''

    exp_path = helpers.make_exp_path( exp )
    inDir    = os.path.join(exp_path,'fcst_{0:d}'.format(ifcst))

    # Assimilated data:
    BEATBOX = pickle.load( open(os.path.join(exp_path,'fcst_{0:d}'.format(ifcst),'BEATBOX.p'), 'rb') )

    nameTags = ['CR', 'AR_var', 'EN', 'AR_ens', 'AR_hyb']

    mech_CR = BEATBOX['mech_CR']
    mech_NR = BEATBOX['mech_NR']

    state_CR = BEATBOX['state_CR']
    state_NR = BEATBOX['state_NR']

    # Path where the output files can be found:
    path_run_CR = os.path.join(exp_path,'fcst_{0:d}'.format(ifcst),mech_CR)
    path_run_NR = os.path.join(exp_path,'fcst_{0:d}'.format(ifcst),mech_NR)
    # Path where the new input files will be saved:
    path_out_CR = os.path.join(exp_path,mech_CR)
    path_out_NR = os.path.join(exp_path,mech_NR)
    if not os.path.isdir(os.path.join(path_out_CR,'input')):
        os.makedirs(os.path.join(path_out_CR,'input'))
    if not os.path.isdir(os.path.join(path_out_NR,'input')):
        os.makedirs(os.path.join(path_out_NR,'input'))


    ##### Control Run:
    # Get all multiMOX concentration output files in <path_run>/output/ with their
    # absolute paths:
    all_fnames = glob.glob(os.path.join(path_run_CR,'output','*.conc'))

    # This will be the path and filename of the new multiMOX input file:
    inp_fname = lambda ensTag,nameTag:                                                  \
        os.path.join(path_out_CR,'input','{1:s}_InitialConditions_{0:d}.csv'.format(ensTag,nameTag))


    # <args.nameTag> creates len( nameTag ) output files:
    fnames_dict = {}
    for xnameTag in nameTags:
        # Sort the loaded output filenames by their nameTags:
        fnames_dict[xnameTag] = []
        for xfile in all_fnames:
            if xnameTag in os.path.basename(xfile):
                fnames_dict[xnameTag].append( xfile )
        # If there are no output files with nameTag 'AR_var'/'AR_ens'/'AR_hyb', files with
        # nameTag 'CR'/'EN'/'EN' are used to generate 'AR_var'/'AR_ens'/'AR_hyb' input
        # files:
        if len(fnames_dict[xnameTag])>0:
            fnames = fnames_dict[xnameTag]
        else:
            if xnameTag=='AR_var':
                fnames = fnames_dict['CR']
            else: # If there are no files with <xnameTag> and <xnameTag> is not 'AR_var'
                  # it must be 'AR_ens' or 'AR_hyb'
                fnames = fnames_dict['EN']
        # Create new input file with right name and right state concentrations...
        for xfname in fnames:
            ensTag = get_ens_tag( xfname )
            if xnameTag in ['EN','AR_ens','AR_hyb']:
                # BEATBOX['EN'/'AR_ens'/'AR_hyb'] has shape (dim_ens,dim_state); the
                # first ensemble member (ensTag=1) can be called with BEATBOX[...][0,:]
                # -> <ensInd>
                ensInd     = ensTag-1
                conc_state = BEATBOX[xnameTag][ensInd,:]
            else:
                # BEATBOX['ev_'*] has shape (dim_state)
                conc_state = BEATBOX['ev_'+xnameTag][:]
            # Create dictionary for function create_input:
            conc_state_dict = {xstate:conc_state[istate] for istate,xstate in enumerate(state_CR)}
            # Create the new file:
            out_file = inp_fname(ensTag,xnameTag)
            create_input_from_output ( xfname, conc_state_dict, out_file )



    ##### Nature Run:
    # There should be only one NR output file ...
    NR_out_fname = os.path.join(path_run_NR,'output','1NR.conc')
    # New Nature Run input file:
    NR_inp_fname = os.path.join(path_out_NR,'input','NR_InitialConditions_1.csv')

    # "Old" Nature Run concentration:
    NR_conc = BEATBOX['ev_NR'][:]
    NR_conc = {xstate:NR_conc[istate] for istate,xstate in enumerate(state_NR)}

    # Create the new input file:
    create_input_from_output( NR_out_fname, NR_conc, NR_inp_fname )

    return

def gen_ass_input (exp, ifcst):
    '''
    Copy all the input files from the analysis to the correct directories

    :param str exp: name of the experiment
    :param int ifcst: forecast number
    '''
    gen_ass_IC( exp, ifcst )

    exp_path = helpers.make_exp_path( exp )

    inDir    = os.path.join(exp_path,'fcst_{0:d}'.format(ifcst))

    # Assimilated data:
    BEATBOX = pickle.load( open(os.path.join(exp_path,'fcst_{0:d}'.format(ifcst),'BEATBOX.p'), 'rb') )

    mech_NR = BEATBOX['mech_NR']
    mech_CR = BEATBOX['mech_CR']

    CRFiles = glob.glob(os.path.join(inDir,mech_CR,'input','Environment_*.csv'    )) + \
              glob.glob(os.path.join(inDir,mech_CR,'input','PhotolysisRates_*.csv'))
    for xfile in CRFiles:
        if not os.path.isdir(os.path.join(exp_path,mech_CR,'input')):
            os.makedirs(os.path.join(exp_path,mech_CR,'input'))
        s.copy(xfile, os.path.join(exp_path,mech_CR,'input'))

    NRFiles = glob.glob(os.path.join(inDir,mech_NR,'input','Environment_*.csv'    )) + \
              glob.glob(os.path.join(inDir,mech_NR,'input','PhotolysisRates_*.csv'))
    for xfile in NRFiles:
        if not os.path.isdir(os.path.join(exp_path,mech_NR,'input')):
            os.makedirs(os.path.join(exp_path,mech_NR,'input'))
        s.copy(xfile, os.path.join(exp_path,mech_NR,'input'))


    return


def write_config ( ds, ds_args, exp, ifcst ):
    '''
    Read and write the settings.cfg file for diurnal cycles and inflation
    inflation values from the analysis are written on the settings.cfg files

    :param str exp: name of the experiment
    :param int ifcst: forecast number
    '''

    exp_path = helpers.make_exp_path( exp )

    config = ConfigParser.ConfigParser()
    config.read( os.path.join(exp_path, 'settings.cfg') )

    if config.getboolean('genBOX', 'diurnal_cycle'):
        tag     = config.get     ('Global', 'case'    )
        runtime = config.getfloat('BOXMOX', 'runtime' )
        DT      = config.getfloat('BOXMOX', 'DT'      )

        TSTART = ds.get_local_sun_time( **ds_args ) * 3600.0 + \
                    float(ifcst) * runtime * 3600.0
        TEND   = TSTART + runtime * 3600.0

        nml                     = boxmox.Namelist()
        nml['tstart']           = TSTART
        nml['tend']             = TEND
        nml['dt']               = DT
        nml['lboxmox_verbose']  = False
        nml.write(os.path.join(exp_path, 'BOXMOX.nml'))

    else:
        pass

    if config.getboolean('BEATBOX', 'inflation'):

        BEATBOX = pickle.load( open(os.path.join(exp_path,'fcst_{0:d}'.format(ifcst),'BEATBOX.p'),'rb') )

        config.set( 'BEATBOX', 'inflation'    , True              )
        config.set( 'BEATBOX', 'lambd_ens'    , BEATBOX['inflation']['post_lambd_ens']     )
        config.set( 'BEATBOX', 'lambd_var_ens', BEATBOX['inflation']['post_lambd_var_ens'] )
        config.set( 'BEATBOX', 'lambd_hyb'    , BEATBOX['inflation']['post_lambd_hyb']     )
        config.set( 'BEATBOX', 'lambd_var_hyb', BEATBOX['inflation']['post_lambd_var_hyb'] )

    else:
        pass

    with open(os.path.join(exp_path, 'settings.cfg'),'w') as f:
        config.write(f)

    return

def run ( ds, ds_args, tuv, translator, exp, cfg_path ):
    '''
    Runs the experiment through the desired cycles called by ./make_cycling_run exp cfg

    :param frappedata.Dataset ds: BOXMOX input dataset
    :param dict ds_args: BOXMOX input dataset input settings dictionary
    :param tuv.DB tuv: TUV database
    :param chemspectranslator.Translator translator: chemspectranslator
    :param str exp: name of the experiment
    :param str cfg_path: the path to the .cfg file that defines the experiment parameters
    :return: path where the calculations are made
    :rtype: str
    '''
    exp_path = new_experiment(exp)

    s.copy(cfg_path,os.path.join(exp_path,'settings.cfg'))

    # Read relevant configuration:
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(exp_path, 'settings.cfg'))

    mech_NR = config.get   ('Global' , 'mech_NR')
    mech_CR = config.get   ('Global' , 'mech_CR')
    nfcst   = config.getint('Cycling', 'nfcst'  )

    print("")
    print("*")
    print("|    Forecast 1")
    print("*")
    print("")

    # First forecast ...
    multimox.create_input  ( ds, ds_args, tuv, translator, exp, exp_path )
    multimox.run           ( exp, exp_path, 1 )

    beatbox.run            ( translator, exp_path )

    inDir  = os.path.join(exp_path,'fcst_1')
    if not os.path.isdir( inDir ):
        os.makedirs( inDir )
    s.move( os.path.join(exp_path,mech_NR    ), inDir )
    if not mech_NR == mech_CR:
        s.move( os.path.join(exp_path,mech_CR    ), inDir )
    s.move( os.path.join(exp_path,'BEATBOX.p'), inDir )

    for ifcst in range(1,nfcst):

        print("")
        print("* ")
        print("|    Forecast "+str(ifcst+1))
        print("*")
        print("")
        # Prior forecast directory:
        inDir = os.path.join(exp_path,'fcst_{0:d}'.format(ifcst))

        # Current forecast directory:
        outDir = os.path.join(exp_path,'fcst_{0:d}'.format(ifcst+1))
        if not os.path.isdir( outDir ):
            os.makedirs( outDir )

        # Generate the new input:
        gen_ass_input( exp, ifcst )

        # New configuration:
        write_config( ds, ds_args, exp, ifcst )

        # Run the new forecast:
        multimox.run( exp, exp_path, ifcst+1 )

        # BEATBOXing...
        beatbox.run( translator, exp_path )

        s.move( os.path.join(exp_path,mech_NR    ), outDir )
        if not mech_NR == mech_CR:
            s.move( os.path.join(exp_path,mech_CR    ), outDir )
        s.move( os.path.join(exp_path,'BEATBOX.p'), outDir )

    return exp_path
