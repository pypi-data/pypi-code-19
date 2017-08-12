#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import ConfigParser

try:
    import cPickle as pickle
except:
    import pickle

from . import helpers

import numpy as np

def _skill_score(x, ref, truth):
    return 1.0 - np.abs(truth - x) / np.abs(truth - ref)

def _niceSpecs(specs):
    isList = isinstance(specs, list)

    if not isList:
        specs = [ specs ]

    specs = [ r'CH$_2$O' if x == 'CH2O' else x for x in specs ]
    specs = [ r'NO$_2$'  if x == 'NO2'  else x for x in specs ]
    specs = [ r'O$_3$'   if x == 'O3'   else x for x in specs ]

    if not isList:
        specs = specs[0]

    return specs

def cycling( translator, runDir, spec, conc=None,
             runTypes=['obs', 'NR', 'CR', 'EN', 'AR_var', 'AR_ens', 'AR_hyb'],
             ax=None, fig=None, plot_legend=True,
             xlabel="", ylabel="", title="", plabel=None,
             scaleFactor = 1e3 ):
    '''
    Plot time series of a cycling run
    '''
    if conc is None:
        conc = helpers.read_conc_cycling( translator, runDir, spec )

    if ax is None:
        from matplotlib.pyplot import subplots
        fig, ax = subplots()

    if 'NR'     in runTypes: ax.plot( conc['time'], conc['ev_NR']*scaleFactor, c='black' , label='NR'   , ls='-' , zorder=4 )
    if 'CR'     in runTypes: ax.plot( conc['time'], conc['ev_CR']*scaleFactor, c='blue'  , label='CR'  , ls='-' , zorder=2 )
    if 'EN'     in runTypes: ax.plot( conc['time'], conc['ev_EN']*scaleFactor, c='blue'  , label='CR ens mean', ls='--', zorder=2 )

    if 'AR_var' in runTypes: ax.plot( conc['time'], conc['ev_AR_var']*scaleFactor, c='red', label='AR adjoint', zorder=3)
    if 'AR_ens' in runTypes:
        ax.plot( conc['time'], conc['ev_AR_ens']*scaleFactor, c='magenta', label='AR ensemble'   , zorder=3)
        max_ens, min_ens = conc['ev_AR_ens']+conc['AR_ens'].std(axis=0), conc['ev_AR_ens']-conc['AR_ens'].std(axis=0)
        ax.fill_between( conc['time'], max_ens*scaleFactor, min_ens*scaleFactor, color='magenta', alpha=0.3 )
    if 'AR_hyb' in runTypes:
        ax.plot( conc['time'], conc['ev_AR_hyb']*scaleFactor, c='cyan'   , label='AR hybrid'     , zorder=3)
        max_hyb, min_hyb = conc['ev_AR_hyb']+conc['AR_hyb'].std(axis=0), conc['ev_AR_hyb']-conc['AR_hyb'].std(axis=0)
        ax.fill_between( conc['time'], max_hyb*scaleFactor, min_hyb*scaleFactor, color='cyan'   , alpha=0.2 )

    ax.grid( alpha=0.5 )
    ax.set( xlim=(conc['time'][0],conc['time'][-1]), xlabel=xlabel, ylabel=ylabel, title=title )

    if 'obs' in runTypes:
        obs = helpers.load_obs_cycling( runDir )
        if spec in obs['obsCR'] or spec in obs['obsNR']:
           obsTime = [conc['runtime']*float(ifcst) for ifcst in range(1,conc['nfcst'])]

           ax.errorbar( obsTime, obs['obs_val']*scaleFactor, yerr=obs['obs_err']*scaleFactor, marker='o',\
                        mec='green', ls='none', color='green', label='Obs',   \
                        markersize=5, elinewidth=1.0, zorder=5                                 )

    ax.yaxis.get_major_formatter().set_powerlimits((-1, 5))

    if not plabel is None:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        ax.text( xmin + 0.05 * (xmax - xmin), ymin + 0.95 * (ymax - ymin), plabel,
                 horizontalalignment='center', verticalalignment='center')

    if plot_legend:
        ax.legend(loc='best', fontsize='x-small', ncol=2)

    return fig

def skill_across_state( BEATBOX ):
    '''
    Plot the skill score of a beatbox experiment for all state vector species
    '''
    B = pickle.load( open(BEATBOX,'rb') )

    from matplotlib.pyplot import subplots
    fig, ax = subplots()

    ax.plot(_skill_score(B['ev_AR_var'], B['ev_CR'], B['ev_NR']), 'r:' , marker='x', label='AR adjoint')
    ax.plot(_skill_score(B['ev_AR_ens'], B['ev_EN'], B['ev_NR']), 'r--', marker='x', label='AR ensemble'   )
    ax.plot(_skill_score(B['ev_AR_hyb'], B['ev_EN'], B['ev_NR']), 'r-' , marker='x', label='AR hybrid'     )

    ind_obs_state = [B['state_CR'].index(xobs) for xobs in B['obs_CR']]
    ax.scatter(ind_obs_state,np.zeros((len(B['obs_CR']),)), marker='*', c='black', s=100,
               label='observed species')

    ax.set(xlim=(-0.1,len(B['state_CR'])-0.9), ylim=(-1.0,1.0), xticks=range(len(B['state_CR'])),         \
           xticklabels=B['state_CR'], xlabel='<state> species', ylabel='skill score (1.0-|NR-AR|/|NR-CR|)')

    ax.legend(loc='best')
    ax.grid( alpha=0.5 )
    ax.axhline(y=0.0, alpha=0.6, c='black', zorder=1)

    return fig


def relative_to_NR( BEATBOX ):
    '''
    Plot performance relative to nature run
    '''
    B = pickle.load( open(BEATBOX,'rb') )

    from matplotlib.pyplot import subplots
    fig, ax = subplots()

    ax.plot(B['ev_CR'    ]/B['ev_NR'], 'b-' , marker='x', label='Control run'   )
    ax.plot(B['ev_EN'    ]/B['ev_NR'], 'b--', marker='x', label='Prior ensemble')
    ax.plot(B['ev_AR_var']/B['ev_NR'], 'r:' , marker='x', label='AR adjoint')
    ax.plot(B['ev_AR_ens']/B['ev_NR'], 'r--', marker='x', label='AR ensemble'   )
    ax.plot(B['ev_AR_hyb']/B['ev_NR'], 'r-' , marker='x', label='AR hybrid'     )

    ind_obs_state = [B['state_CR'].index(xobs) for xobs in B['obs_CR']]
    ax.scatter(ind_obs_state,np.ones((len(B['obs_CR']),)), marker='*', c='black', s=100,
               label='observed species')

    ax.set( xlim=[-0.1,len(B['state_CR'])-0.9], ylim=[0.0,2.0],         \
            xticks=range(len(B['state_CR'])), xticklabels=B['state_CR'],\
            xlabel='<state> species', ylabel='<state> / NR',            \
            title='Results relative to NR'                              )

    ax.legend(loc='best')
    ax.grid(alpha=0.5)
    ax.axhline(y=1.0, alpha=0.6, c='black', zorder=1)

    return fig


def scatter( BEATBOX, obs_spec = None, scaleFactor=1e3, axarr=None, fig=None, plabels=None ):
    '''
    Scatter plot
    '''
    B = pickle.load( open(BEATBOX,'rb') )

    if obs_spec is None:
        obs_spec = B['obs_CR'][0]

    iobs = B['state_CR'].index(obs_spec)

    import matplotlib.pyplot as plt

    for toScale in [ 'ev_NR',
                     'ev_CR',
                     'ev_AR_var',
                     'EN',
                     'AR_ens',
                     'AR_hyb',
                     'AR_ens_prior',
                     'AR_hyb_prior',
                     'ev_AR_var_prior',
                     'obs_val',
                     'obs_err']:
        B[toScale] *= scaleFactor

    if fig is None:
        fig, axarr = plt.subplots(1, len(B['state_CR']), figsize=(5*len(B['state_CR']), 5))

    for istate, xstate in enumerate(B['state_CR']):
        xstate_lower_bound = min( B['ev_NR'][istate], B['ev_CR'][istate], B['ev_AR_var'][istate],
                                  B['EN'][:,istate].min(), B['AR_ens'][:,istate].min(),
                                  B['AR_hyb'][:,istate].min() )
        xstate_upper_bound = max( B['ev_NR'][istate], B['ev_CR'][istate], B['ev_AR_var'][istate],
                                  B['EN'][:,istate].max(), B['AR_ens'][:,istate].max(),
                                  B['AR_hyb'][:,istate].max() )

        xax = axarr[istate]

        xax.scatter(B['AR_ens_prior']    [:,istate], B['AR_ens_prior']    [:,iobs], marker='s', c='cyan', s=15, edgecolor='none',
                    zorder=2, label='Prior ensemble')
        xax.scatter(B['AR_ens'][:,istate], B['AR_ens'][:,iobs], marker='s', c='orange' , s=15, edgecolor='none',
                    zorder=2, label='Posterior ensemble'   )
        xax.scatter(B['AR_hyb_prior']    [:,istate], B['AR_hyb_prior']    [:,iobs], marker='s', c='blue', s=15, edgecolor='none',
                    zorder=2, label='Prior hybrid')
        xax.scatter(B['AR_hyb'][:,istate], B['AR_hyb'][:,iobs], marker='s', c='red' , s=15, edgecolor='none',
                    zorder=2, label='Posterior hybrid'     )
        for ens in range(B['nens']):
            xax.plot([B['AR_ens_prior'][ens,istate],B['AR_ens'][ens,istate]],[B['AR_ens_prior'][ens,iobs],B['AR_ens'][ens,iobs]],
                     c='black', ls='--', alpha=0.1, zorder=1)
            xax.plot([B['AR_hyb_prior'][ens,istate],B['AR_hyb'][ens,istate]],[B['AR_hyb_prior'][ens,iobs],B['AR_hyb'][ens,iobs]],
                     c='black', ls='-' , alpha=0.1, zorder=1)

        xax.scatter(B['ev_AR_var_prior']    [istate], B['ev_AR_var_prior']    [iobs], marker='o', c='blue', s=50, lw=0.1,
                    zorder=3, edgecolor='black', label='Prior adjoint'   )
        xax.scatter(B['ev_AR_var'][istate], B['ev_AR_var'][iobs], marker='o', c='red'  , s=50, lw=0.1,
                    zorder=3, edgecolor='black', label='Posterior adjoint')
        xax.plot([B['ev_AR_var_prior'][istate],B['ev_AR_var'][istate]],[B['ev_AR_var_prior'][iobs],B['ev_AR_var'][iobs]], 'b:', lw=0.1,
                 alpha=0.5)

        xax.scatter(B['ev_NR'][istate], B['ev_NR'][iobs], marker='*', c='black', s=100, zorder=3, edgecolor='none',
                    label='Nature run')
        if iobs!=istate:
            xax.errorbar( B['ev_NR'][istate], B['obs_val'], yerr=B['obs_err'], marker='*',\
                mec='green', ls='none', color='green', label='Obs',   \
                markersize=7, elinewidth=1.5, zorder=5                                 )
        else:
            xax.errorbar( B['obs_val'], B['obs_val'], yerr=B['obs_err'], marker='*',\
                mec='green', ls='none', color='green', label='Obs',   \
                markersize=7, elinewidth=1.5, zorder=5                                 )

        xobs_lower_bound = min( B['ev_NR'][iobs], B['ev_AR_var_prior'][iobs], B['ev_AR_var'][iobs],
                                B['AR_ens_prior'][:,iobs].min(), B['AR_ens'][:,iobs].min(),
                                B['AR_hyb_prior'][:,iobs].min(), B['AR_hyb'][:,iobs].min() )
        xobs_upper_bound = max( B['ev_NR'][iobs], B['ev_AR_var_prior'][iobs], B['ev_AR_var'][iobs],
                                B['AR_ens_prior'][:,iobs].max(),B['AR_ens'][:,iobs].max(),
                                B['AR_hyb_prior'][:,iobs].max(), B['AR_hyb'][:,iobs].max() )

        xlim_min = xstate_lower_bound-abs(0.1*xstate_lower_bound)
        xlim_max = xstate_upper_bound+abs(0.1*xstate_upper_bound)
        ylim_min =   xobs_lower_bound-abs(0.1*  xobs_lower_bound)
        ylim_max =   xobs_upper_bound+abs(0.1*  xobs_upper_bound)

        pstate = _niceSpecs(xstate)
        pobs   = _niceSpecs(B['state_CR'][iobs])

        xax.set(xlabel='state space\n{0:s} concentration in ppbv'.format(pstate),
                ylabel='obs space\n{0:s} concentration in ppbv'.format(pobs),
                xlim=(xlim_min,xlim_max), ylim=(ylim_min,ylim_max))
        xax.grid(alpha=0.6)

        xax.set_xticklabels(xax.get_xticks(), rotation=45)

        if not plabels is None:
            xmin, xmax = xax.get_xlim()
            ymin, ymax = xax.get_ylim()
            xax.text( xmin + 0.05 * (xmax - xmin), ymin + 0.95 * (ymax - ymin), plabels[istate],
                     horizontalalignment='center', verticalalignment='center')

    axarr[2].legend(loc='best', fontsize='x-small')
    fig.tight_layout()

    return fig


def NRCR( runDir, spec, translator, conc=None, scaleFactor=1e3, ax=None, fig=None,
          xlabel="", ylabel="", title="", plabel=None):
    '''
    Plot only nature run and control run
    '''
    if conc is None:
        conc = helpers.read_conc_cycling( translator, runDir, spec )

    if ax is None:
        from matplotlib.pyplot import subplots
        fig, ax = subplots()

    ax.plot( conc['time'], conc['ev_NR']*scaleFactor, c='black' , lw=3.0, label='Nature Run'   , ls='-' , zorder=4 )
    ax.plot( conc['time'], conc['ev_CR']*scaleFactor, c='blue'  , lw=2.0, label='Control Run'  , ls='-' , zorder=2 )

    ax.yaxis.get_major_formatter().set_powerlimits((-1, 5))

    ax.grid( alpha=0.5 )
    ax.set( xlim=(conc['time'][0],conc['time'][-1]), xlabel=xlabel, ylabel=ylabel,\
            title=title )

    if not plabel is None:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        ax.text( xmin + 0.05 * (xmax - xmin), ymin + 0.95 * (ymax - ymin), plabel,
                 horizontalalignment='center', verticalalignment='center')

    return fig


def sensitivities (runDir, max_val=1000.0,  ncolors=21, abs_max=60.0, fig=None, axarr=None):
    '''
    Plot sensitivities over time
    '''
    xBBFiles = glob.glob(runDir+'/fcst_*/BEATBOX.p')
    nfcst   = len(xBBFiles)
    BBFiles = []
    for ifcst in range( 1, nfcst+1 ):
        BBFiles.append(os.path.join(runDir,'fcst_{0:d}'.format(ifcst),'BEATBOX.p'))

    #find the obs index
    BB = pickle.load( open(xBBFiles[0],'rb') )
    state_raw = BB['state_CR']
    obs       = BB['obs_CR'  ]

    for istate,xstate in enumerate(state_raw):
        if xstate in obs:
            ind_obs=istate

    adj = []; ens = []; r_adj=[]; r_ens=[]
    for xBBFile in BBFiles:
        BB = pickle.load( open(xBBFile,'rb') )
        adj.append( BB['CR_adj_sen'][0,:] )
        ens.append( BB['EN_ens_sen'][0,:] )
        r_adj.append( 100.*(BB['CR_adj_sen'][0,:]/(1000.0*BB['ev_CR'][:])) )
        r_ens.append( 100.*(BB['EN_ens_sen'][0,:]/(1000.0*BB['ev_EN'][:])) )

    adj = np.array( adj )
    ens = np.array( ens )
    r_adj = np.array( r_adj )
    r_ens = np.array( r_ens )

    ## Remove observed species from state vector:
    ind, state = [], []
    for istate,xstate in enumerate(state_raw):
        if not xstate in obs:
            state.append( xstate )
            ind  .append( istate )

    config = ConfigParser.ConfigParser()
    config.read(runDir+'/settings.cfg')
    runtime = config.getfloat('BOXMOX','runtime')

    import matplotlib as mpl
    import matplotlib.pyplot as plt
    from matplotlib.cm import get_cmap

    def disc ( cmap, N):
        cmap = get_cmap(cmap)
        colors_i = np.concatenate((np.linspace(0, 1., N), (0.,0.,0.,0.)))
        colors_rgba = cmap(colors_i)
        indices = np.linspace(0, 1.0, N+1)
        cdict = {}
        for ki,key in enumerate(('red','green','blue')):
            cdict[key] = [ (indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki]) for i in xrange(N+1) ]

        return mpl.colors.LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)

    cmap = disc( 'bwr', ncolors )

    shp = r_ens[:,ind].T.shape
    img = axarr[0].imshow( r_adj[:,ind].T, interpolation='none', origin='lower',
                           extent=(0, shp[1], 0, shp[0]), aspect='auto',
                           vmin=-abs_max, vmax=abs_max, cmap=cmap)
    img = axarr[1].imshow( r_ens[:,ind].T, interpolation='none', origin='lower',
                           extent=(0, shp[1], 0, shp[0]), aspect='auto',
                           vmin=-abs_max, vmax=abs_max, cmap=cmap)

    state = _niceSpecs(state)

    for ax in axarr:
        ax.set_yticks([ x + 0.5 for x in range(shp[0])])
        ax.set_yticklabels(state)

    axarr[0].set_ylabel('Adjoint')
    axarr[1].set_ylabel('Ensemble')

    axarr[1].set_xticks([ x + 0.5 for x in range(shp[1])])
    axarr[1].set_xticklabels((np.linspace(runtime,int(nfcst)*runtime,nfcst).astype(int)))

    axarr[1].set_xlabel('Time in h')

    c=fig.colorbar(img,extend='both', label='Sensitivity to 1 ppbv {0:s} change \n to the state in %'.format(obs[0]),
                   cax=axarr[2], ax=axarr[0])

    fig.tight_layout()

    return fig

def _regime(runDir, mechCR):

    if not mechCR == 'MOZART_T1':
        raise Exception("Only coded for MOZART_T1 so far.")

    import numpy as np
    import matplotlib.pyplot as plt

    from os.path import abspath
    runDir  = abspath( runDir  )+'/'

    from glob import glob
    nfcst = len( glob(runDir+'fcst_*/') )

    def GetComConcTS ( fname ):

        with open(fname,'r') as f:
            head = f.readline().split()
            data = np.array([[float(value) for value in line.split()] for line in f.readlines()])

        time = data[:,0 ]
        data = data[:,1:]

        return head[1:], time, data

    def getSpecList ( ratioTag ):

        SpecLists = {
                      'NOx'      :  [
                                        ['NO', 1.0], ['NO2', 1.0]
                                    ],
                      \
                      'NOy'      :  [
                                        ['NO'  , 1.0], ['NO2'   , 1.0], ['NO3', 1.0], ['N2O5', 1.0], ['HONO', 1.0],
                                        ['HNO3', 1.0], ['HO2NO2', 1.0], ['PAN', 1.0], ['MPAN', 1.0]
                                    ],
                      \
                      'VOC'      :  [
                                        ['CH3OOH', 1.0], ['CH2O', 1.0], ['CH3OH', 1.0], ['HCOOH', 1.0],
                                        \
                                        ['C2H4'   , 2.0], ['C2H6'  , 2.0], ['CH3CHO' , 2.0], ['C2H5OH'  , 2.0], ['CH3COOH', 2.0],
                                        ['GLYOXAL', 2.0], ['GLYALD', 2.0], ['C2H5OOH', 2.0], ['CH3COOOH', 2.0], ['PAN'    , 2.0],
                                        ['C2H2'   , 2.0],
                                        \
                                        ['C3H6', 3.0], ['C3H8'    , 3.0], ['C3H7OOH', 3.0], ['POOH', 3.0], ['CH3COCH3', 3.0],
                                        ['HYAC', 3.0], ['CH3COCHO', 3.0], ['ROOH'   , 3.0], #['ONIT', 3.0],
                                        \
                                        ['BIGENE', 4.0], ['MEK'    , 4.0], ['MEKOOH' , 4.0], ['MVK'   , 4.0], ['MACR', 4.0],
                                        ['MPAN'  , 4.0], ['MACROOH', 4.0], ['BIGALD1', 4.0], ['HMPROP', 4.0],
                                        \
                                        ['BIGALK', 5.0], ['ALKOOH', 5.0], ['ISOP' , 5.0], ['ISOPOOH', 5.0], ['HYDRALD', 5.0],
                                        ['XOOH'  , 5.0], ['BIGALD', 5.0], ['ONITR', 5.0], ['BIGALD2', 5.0], ['BIGALD3', 5.0],
                                        ['MBO'   , 5.0], ['MBOOOH', 5.0],
                                        \
                                        ['BENZENE', 6.0], ['PHENOL' , 6.0], ['BEPOMUC', 6.0], ['PHENOOH', 6.0],  ['C6H5OOH', 6.0],
                                        ['BENZOOH', 6.0], ['BIGALD4', 6.0],
                                        \
                                        ['TOLUENE', 7.0], ['CRESOL', 7.0],['TOLOOH', 7.0],['PBZNIT', 7.0],['TEPOMUC', 7.0],
                                        ['BZOOH'  , 7.0], ['BZALD' , 7.0],
                                        \
                                        ['XYLENES', 8.0], ['XYLOL', 8.0],['XYLOLOOH', 8.0], ['XYLENOOH', 8.0],
                                        \
                                        ['TERPOOH', 10.0]
                                    ],
                      \
                      'CO'       :  [
                                        ['CO', 1.0]
                                    ],
                      \
                      'TOLUENE'  :  [
                                        ['TOLUENE', 1.0]
                                    ],
                      \
                      'BENZENE'  :  [
                                        ['BENZENE', 1.0]
                                    ]
                    }

        for xratioTag in ratioTag.split('_'):
            if not xratioTag in SpecLists.keys():
                raise ValueError('unknown ratioTag :: {}'.format(ratioTag))

        return SpecLists[ratioTag.split('_')[0]], SpecLists[ratioTag.split('_')[1]]

    def ratio( conc_state, ratioTag ):

        numerator, denominator = getSpecList( ratioTag )

        numerator   = np.array( [conc_state[xnumerator  [0]] * xnumerator  [1] for xnumerator   in numerator  ] )
        denominator = np.array( [conc_state[xdenominator[0]] * xdenominator[1] for xdenominator in denominator] )

        return np.sum(numerator, axis=0) / np.sum(denominator, axis=0)

    head, time, concCR = GetComConcTS( runDir+'fcst_1/'+mechCR+'/output/0CR.conc' )
    concCR = {xhead:concCR[:,ihead] for ihead,xhead in enumerate(head)}

    TEND = time[-1]

    for ifcst in range( 2, nfcst+1 ):

        xhead, xtime, xconcCR = GetComConcTS( runDir+'fcst_{0:d}/{1:s}/output/0CR.conc'.format(ifcst,mechCR) )

        for xspec,xconc in concCR.iteritems():
            xind          = xhead.index( xspec )
            concCR[xspec] = np.append( xconc, xconcCR[1:,xind] )

        time = np.append( time, xtime[1:]+float(ifcst-1)*TEND )


    voc_nox = ratio( concCR, 'VOC_NOx'         )
    tol_ben = ratio( concCR, 'TOLUENE_BENZENE' )

    fig, ax = plt.subplots()

    ax.plot( time[:], voc_nox[:], color='blue' )

    ax2 = ax.twinx()
    ax2.plot( time[:], tol_ben[:], color='red' )

    ax.set_ylabel(r'VOC/NO$_{\mathrm{x}}$ ratio',color='blue')
    ax2.set_ylabel(r'toluene/benzene ratio', color='red')

    p1 = np.interp(4.0,voc_nox,time)
    p2 = np.interp(8.0,voc_nox,time)
    p3 = np.interp(15.0,voc_nox,time)

    ax.axvline(p1, c='black', ls='--')
    ax.axvline(p2, c='black', ls='-' )
    ax.axvline(p3, c='black', ls='--')

    ymin, ymax = ax.get_ylim()

    ax.text(15.0, 0.95*ymax, r'VOC-limited', ha='center', va='center',backgroundcolor='white')
    ax.text(36.0, 0.95*ymax, r'transition region', ha='center', va='center',backgroundcolor='white')
    ax.text(52.5, 0.95*ymax, r'NO$_{\mathrm{x}}$-limited', ha='center', va='center',backgroundcolor='white')
    ax.set_xlabel(r'Time in h')

    return fig

