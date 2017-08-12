import shutil as s
import os
import ConfigParser
import re
import glob

import boxmox

import genbox as g
import genbox.perturb as p

def create_input(ds, ds_args, tuv, translator, exp, exp_path):
    '''
    Creates input data for a beatbox experiment
    '''
    c = ConfigParser.ConfigParser()
    c.read(os.path.join(exp_path, 'settings.cfg'))

    globals = lambda x : c.get('Global', x)
    genBOX = lambda x : c.get('genBOX', x)

    exp_NR = os.path.join(exp_path, globals('mech_NR'),'input')
    if not os.path.isdir(exp_NR):
        os.makedirs(exp_NR)
    exp_CR = os.path.join(exp_path, globals('mech_CR'),'input')
    if not os.path.isdir(exp_CR):
        os.makedirs(exp_CR)

    diurnal_cycle = c.getboolean('genBOX', 'diurnal_cycle')

    # Create namelist:
    runtime = c.getfloat('BOXMOX', 'runtime')
    DT      = c.getfloat('BOXMOX', 'DT'  )

    TSTART = ds.get_local_sun_time( **ds_args ) * 3600.0
    TEND   = TSTART + runtime*3600.0

    nml                     = boxmox.Namelist()
    nml['tstart']           = TSTART
    nml['tend']             = TEND
    nml['dt']               = DT
    nml['lboxmox_verbose']  = False

    nml.write(os.path.join(exp_path, 'BOXMOX.nml'))

    # Create NR input:
    with open(os.path.join(exp_NR,'Environment_1.csv'),'w') as f:
        g.createEnvironment(ds, ds_args, diurnal_cycle=diurnal_cycle, f=f)
    with open(os.path.join(exp_NR,'PhotolysisRates_1.csv'),'w') as f:
        g.createPhotolysisRates(ds, ds_args, tuv, diurnal_cycle=diurnal_cycle, f=f)
    with open(os.path.join(exp_NR,'NR_InitialConditions_1.csv'),'w') as f:
        g.createInitialConditions(ds, ds_args, translator, globals('mech_NR'), f=f)

    # Create CR input:
    with open(os.path.join(exp_CR,'Environment_0.csv'),'w') as f:
        g.createEnvironment(ds, ds_args, scale_factor=float(genBOX('mean_scaletemp')), diurnal_cycle=diurnal_cycle, f=f)
    with open(os.path.join(exp_CR,'PhotolysisRates_0.csv'),'w') as f:
        g.createPhotolysisRates(ds, ds_args, tuv, scale_factor=float(genBOX('mean_scalephot')), diurnal_cycle=diurnal_cycle, f=f)
    with open(os.path.join(exp_CR,'CR_InitialConditions_0.csv'),'w') as f:
        g.createInitialConditions(ds, ds_args, translator, globals('mech_CR'), scale_factor=float(genBOX('mean_scaleic')),scale_species=genBOX('perturbspecies'), f=f)

    # Create EN input:
    nens = int(globals('nens'))
    if nens > 0:
        pertTEMP = p.perturb_factors(float(genBOX('mean_scaletemp')), float(genBOX('rel_stdev_scaletemp')), nens, distr=genBOX('pert_distrtemp'))
        pertPhot = p.perturb_factors(float(genBOX('mean_scalephot')), float(genBOX('rel_stdev_scalephot')), nens, distr=genBOX('pert_distrphot'))
        pertIC   = p.perturb_factors(float(genBOX('mean_scaleic'  )), float(genBOX('rel_stdev_scaleic'  )), nens, distr=genBOX('pert_distric'  ))
        for ens in range(nens):
            with open(os.path.join(exp_CR,'Environment_{0:d}.csv'.format(ens+1)),'w') as f:
                g.createEnvironment(ds, ds_args, scale_factor=pertTEMP[ens], diurnal_cycle=diurnal_cycle, f=f)
            with open(os.path.join(exp_CR,'PhotolysisRates_{0:d}.csv'.format(ens+1)),'w') as f:
                g.createPhotolysisRates(ds, ds_args, tuv, scale_factor=pertPhot[ens], diurnal_cycle=diurnal_cycle, f=f)
            with open(os.path.join(exp_CR,'EN_InitialConditions_{0:d}.csv'.format(ens+1)),'w') as f:
                g.createInitialConditions(ds, ds_args, translator, globals('mech_CR'), scale_factor=pertIC[ens], scale_species=genBOX('perturbspecies'), f=f)

    return

def __run( model, exp, exp_path, ensTag, nameTag, nmlFile ):

    print("{:<20s} {:<8s} {:>4d}".format(model, nameTag, ensTag))

    box = boxmox.Experiment(model)

    if 'adjoint' in model:
        model_raw = '_'.join(model.split('_')[:-1])
    else:
        model_raw = model

    box.namelist.read(nmlFile)

    box.addInputFromFile('Environment',
                         os.path.join(exp_path,model_raw,'input','Environment_{0:d}.csv'.format(ensTag)))
    box.addInputFromFile('PhotolysisRates',
                         os.path.join(exp_path,model_raw,'input','PhotolysisRates_{0:d}.csv'.format(ensTag)))
    box.addInputFromFile('InitialConditions',
                         os.path.join(exp_path,model_raw,'input','{0:s}_InitialConditions_{1:d}.csv'.format(nameTag,ensTag)))

    try:
        res = box.run(dumbOutput=True) # run, and only reference output for faster processing
    except Exception as e:
        raise Exception('BOXMOX integration failed:' + str(e))

    if not os.path.isdir(os.path.join(exp_path,model_raw,'output')):
        os.makedirs(os.path.join(exp_path,model_raw,'output'))

    if not 'adjoint' in model:
        box.output['Concentrations'].copy( os.path.join(exp_path,model,'output','{0:d}{1:s}.conc'    .format(ensTag,nameTag) ) )
        box.output['Rates'].copy( os.path.join(exp_path,model,'output','{0:d}{1:s}.rates'   .format(ensTag,nameTag) ) )
        box.output['Jacobian'].copy( os.path.join(exp_path,model,'output','{0:d}{1:s}.jacobian'.format(ensTag,nameTag) ) )
        try:
            box.output['Hessian'].copy( os.path.join(exp_path,model,'output','{0:d}{1:s}.hessian'.format(ensTag,nameTag)) )
        except:
            pass
    else:
        box.output['Adjoint'].copy( os.path.join(exp_path,model_raw,'output','{0:d}{1:s}.adjoint'.format(ensTag,nameTag)) )

    del box

    return


def run( exp, exp_path, nfcst ):
    '''
    Runs the box model for all beatbox experiment members
    '''
    if not os.path.exists(exp_path):
        raise IOError('Could not find experiment path "{0:s}"'.format(exp_path))

    ##### Read configuration:
    config = ConfigParser.ConfigParser()
    config.read(os.path.join(exp_path, 'settings.cfg'))

    mech_NR = config.get   ('Global', 'mech_NR')
    mech_CR = config.get   ('Global', 'mech_CR')

    ##### Get Namelist path:
    nmlFile = os.path.join( exp_path, 'BOXMOX.nml' )

    ##### Do calculations:
    print("Running experiment {:s}".format(exp))
    print("")
    print("{:<20s} {:<8s} {:>4s}".format('mechanism', 'run type', '#'))

    # number of CPUs used for parallel calculations
    ncpus = int(config.get   ('Global', 'ncpus'))

    def make_runs(mechName, nameTag):
        pathTag = mechName.replace('_adjoint', '')
        ICFiles = glob.glob(os.path.join(exp_path, pathTag, 'input', nameTag + '_InitialConditions*.csv'))
        ensTags = []
        for ICFile in ICFiles:
            m      = re.search(nameTag + '_InitialConditions_([0-9]+).csv', ICFile)
            ensTags.append(int(m.group(1)))
        try:
            # Parallel version
            from joblib import Parallel, delayed
            Parallel(n_jobs=ncpus)(delayed(__run)(mechName, exp, exp_path, ensTag, nameTag, nmlFile) for ensTag in ensTags)
        except:
            # Fallback to serial version
            for ensTag in ensTags:
                __run(mechName, exp, exp_path, ensTag, nameTag, nmlFile)

    # Nature run
    make_runs(mech_NR, 'NR')

    # Forward runs
    nul = [ make_runs(mech_CR, tag) for tag in [ 'CR', 'EN', 'AR_var', 'AR_ens', 'AR_hyb'] ]

    # Adjoint runs
    nul = [ make_runs(mech_CR + '_adjoint', tag) for tag in [ 'CR', 'EN', 'AR_var', 'AR_hyb' ] ]

    return

