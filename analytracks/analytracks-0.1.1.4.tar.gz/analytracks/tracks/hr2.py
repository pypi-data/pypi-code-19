import numpy as np
import pandas as pd
import seaborn
import matplotlib.pyplot as plt
import scipy.optimize
import scipy.interpolate

all_names = ['hr_rest', 'hr_slope', 'hr_max', 'A', 'a', 'b', 'B']




 
def hr_sim(track, x):


    df = track.points
    if track.rideRun == 'ride':
        po = df.po

    if track.rideRun == 'run':
        po = df.runPO

    # 1 second resampling
    # time_re = np.arange(0, df.time_s.values[-1], 1)
    # po = scipy.interpoltate.interp1d(df.time_s, df.po, fill_value='extrapolate')(time_re)

    hr = hr_sim.hr_sim
    d = hr_sim.hr_sim
    #po_cumsum = np.cumsum(po)
    #po_m=po.copy()
    #n=10
    #if n:
    #    po_m[n:] = (po_cumsum[n:].values - po_cumsum[0:-n].values)/n

    hr[0] = df.hr[0]
    d[0] = hr_rest
    for i in range(0,len(po)-1):

        # Mazzoleni 2016 works quite ok with
        # {'hr_slope': 0.29508620693416909, 'hr_max': 185, 'b': 3.8779670918068119, 'A': 1.6891887058493307e-10,'a': 1.6252820412231253, 'hr_rest': 79.123321349610109, 'B': 0.026893893307773739}
        # 7.24 (Tom Dernies)
        # fd = (d[i]-hr[i])
        # fmin = ( hr[i]-hr_rest)**a
        # fmax = ( -hr[i]+hr_max)**b
        # hr[i+1] = hr[i]+ A*fmin*fmax*fd

        # also works with fmin = fmax = 1 adding
        # if(hr[i+1]>hr_max):
        #   hr[i + 1] = hr_max

        # if (hr[i + 1] < hr_rest):
        #   hr[i + 1] = hr_rest
        # then x becomes {'B': 0.041726670942218193, 'hr_slope': 0.25417647965301232, 'a': 1.6252820412231253, 'A': 0.092569002744056494, 'hr_max': 185, 'b': 3.877967091806812, 'hr_rest': 88.246514037647671}

        # Zekynthinaki 2015
        d[i+1] = d[i] + B*(hr_rest+hr_slope*po[i]-d[i])
        #print('d   :{}'.format(d[i]))
        fd = (d[i]-hr[i])
        fmin=1
        fmax=1
        #fmin = 1-np.exp(-( (hr[i]-hr_rest)/10)**2 )
        #fmax =   np.exp(-( (hr[i]-hr_max )/10)**2 )-1
        hr[i+1] = hr[i]+ A*fmin*fmax*fd + hrl[i]
        hrl[i+1] = hrl[i] + b*(hrl[i] - a)
        if(hr[i+1]>hr_max):
            hr[i+1] = hr_max

        if (hr[i + 1] < hr_rest):
            hr[i + 1] = hr_rest

        #print('hr   :{}'.format(hr[i]))
        #print('hr   :{}'.format(hr[i]))


    return hr

hr_sim.d = 0
hr_sim.hr_sim = 0

def to_minimize(nx, args):
    """
    nx : current cardiac parameters
    args[0] : current track
    args[1] : parameters to tune. Example ['hr_rest', 'hr_slope', 'hr_max']
    args[2] : default parameters [hr_rest, hr_slope, hr_max, k_r, k_f, k_e, slope_sf, speed_sf]
    args[3] : track type : 'ride' or 'run'
    args[4] : elevation source : 'garmin' or 'google'

    return : rms error for the current track
    """
    track = args[0]
    df = track.points

    to_tune = args[1]
    x_default = args[2]
    track_type = args[3]
    ele_name = args[4]

    x = x_default.copy()
    for name, value in zip(to_tune, nx):
        x[name] = value


    print(x)
    #x = de_scale_param(x)


    print(to_minimize.n)
    to_minimize.n+=1


    sim = hr_sim(track, x)

    #df.ix[:,'hr_sim']=hr_sim
    #df.ix[:,'po2']=df.po/5+150
    #df[['hr_sim','hr','po2']].plot()
    #plt.show

    err_q = ((sum((sim - df.hr) ** 2))/len(df))**0.5
    errM = sum(abs(sim - df.hr)) / len(df)
    print(err_q)
    return err_q

to_minimize.n = 0

def fit(activity, to_tune=None, x0=None):
    if not to_tune:
        to_tune = ['hr_rest', 'hr_slope', 'hr_max', 'A', 'a', 'b', 'B']

    if not x0:
        x0 = {
            'hr_rest':65, 'hr_slope': 0.0915, 'hr_max': 185,
            'A': 0.001, 'a': 1, 'b': 1,
            'B': 0.001
        }

    #x0 = scale_param(x0)

    df = activity.points


    if activity.rideRun == 'ride':
        type='ride'

    if activity.rideRun in ['ride','run']:
        to_minimize.n = 0
        hr_sim.d = df.hr.copy()
        hr_sim.hr_sim = df.hr.copy()
        args = [activity, to_tune, x0, type, 'ele']
        x = [x0[name] for name in to_tune]  # initial value of the tuning parameter
        #x = [x0[name] for name in to_tune]
        fit = scipy.optimize.minimize(fun=to_minimize, x0=x, args=args, method='Nelder-Mead')
    else:
        return None

    nx = fit.get('x')
    x = x0.copy()
    for name, value in zip(to_tune, nx):
        x[name] = value

    return x #de_scale_param(x)


