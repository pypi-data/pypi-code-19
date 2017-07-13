import numpy as np
import pandas as pd
import seaborn
import matplotlib.pyplot as plt
import scipy.optimize
import scipy.interpolate


def hr_ss(po, hrmin = 60,coef = 0.26,hrmax = 200):
    """
    heart rate steady state
    po : power output
    hrmin : hr at rest
    coef : [bpm/watt]
    """
    hr = hrmin+coef*po
    
    if np.isscalar(po):
        return min(hr, hrmax)
    else:
        hr[hr > hrmax]=hrmax
        return hr
    
 
def hr_tp1(hrt, hr_ss, kr=0.04, kf=0.03):
    """
    = HR( t + 1 )
    hr(t+1)=hr(t)+k*(hr_ss(po(t))-hr(t))
    """
    if hr_ss>hrt:
        return hrt + kr * (hr_ss - hrt)

    else:
        return hrt + kf * (hr_ss - hrt)


def hr_sim(track, x):

    all_names = ['hr_rest', 'hr_slope', 'hr_max', 'k_r', 'k_f', 'k_e', 'slope_sf', 'speed_sf', 'delay']
    hr_rest, hr_slope, hr_max, k_r, k_f, k_e, slope_sf, speed_sf, delay = [x[name] for name in all_names]

    df = track.points
    #print(track.rideRun)
    if track.rideRun == 'ride':
        po = df.po

    if track.rideRun == 'run':
        po = df.runPO

    # 1 second resampling
    # time_re = np.arange(0, df.time_s.values[-1], 1)
    # po = scipy.interpoltate.interp1d(df.time_s, df.po, fill_value='extrapolate')(time_re)

    hr = po.copy()
    po_cumsum = np.cumsum(po)
    po_m=po.copy()
    n=10
    if n:
        po_m[n:] = (po_cumsum[n:].values - po_cumsum[0:-n].values)/n



    i=0
    hr[0] = hr_ss(0, hr_rest, hr_slope, hr_max)
    for i in range(0,len(po)-1):
        hr_ss_t = hr_ss(po_m[i] + k_e * po_cumsum[i], hr_rest, hr_slope, hr_max)
        hr[i+1]=hr_tp1(hr[i], hr_ss_t, k_r, k_f)

    if int(delay):
        hr = shift(hr,int(delay),hr_rest)

    return hr


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


    #print(x)
    #x = de_scale_param(x)

    if x['slope_sf'] < 0:
        x['slope_sf'] = 0

    if x['speed_sf'] < 0:
        x['speed_sf'] = 0

    #print(to_minimize.n)
    to_minimize.n+=1
    speed_or_slope_changed = 0
    if "slope_sf" in to_tune:
        if to_minimize.prev_slope_sf != x['slope_sf']:
            track.add_slope(ele_name=ele_name, sf=x['slope_sf'])
            to_minimize.prev_slope_sf = x['slope_sf']
            print('filtering slope')
            speed_or_slope_changed = 1

    if "speed_sf" in to_tune:
        if to_minimize.prev_speed_sf != x['speed_sf']:
            track.add_speed(x['speed_sf'])
            to_minimize.prev_speed_sf = x['speed_sf']
            print('filtering speed')
            speed_or_slope_changed = 1        
    
    if speed_or_slope_changed:
        df['EC'] = nrgs(df['slopef'])
        df['runPO'] = df['EC']*df['speedf']

        nans = np.isnan(df.runPO)
        df.ix[nans, 'runPO'] = np.interp(df.time_s[nans], df.time_s[~nans], df.runPO[~nans] )

    sim = hr_sim(track, x)

    #df.ix[:,'hr_sim']=hr_sim
    #df.ix[:,'po2']=df.po/5+150
    #df[['hr_sim','hr','po2']].plot()
    #plt.show

    err_q = ((sum((sim - df.hr) ** 2))/len(df))**0.5
    errM = sum(abs(sim - df.hr)) / len(df)
    #print(err_q)
    return err_q




to_minimize.n = 0
to_minimize.prev_slope_sf = 0
to_minimize.prev_speed_sf = 0


def nrgs(s):
        """
        energy cost per meter on a slope s
        :param s:
        :return:
        """
        return 155.4 * s ** 5 - 30.4 * s ** 4 - 43.3 * s ** 3 + 46.3 * s ** 2 + 19.5 * s + 3.6


# [min, max]
scaling = {'delay': [0, 10],
           'hr_max': [150, 250],
           'hr_rest': [30, 100],
           'hr_slope': [0.05, 0.5],
           'k_e': [1e-5, 10e-5],
           'k_f': [0.01, 0.05],
           'k_r': [0.02, 0.1],
           'slope_sf': [1e-5, 1e-3],
           'speed_sf': [1e-5, 1e-3]}


def scale_param(x):
    x_s = x.copy()
    for k_i in x.keys():
        x_s[k_i] = (x[k_i]-scaling[k_i][0])/(scaling[k_i][1]-scaling[k_i][0])

    return x_s


def de_scale_param(x):
    x_s = x.copy()
    for k_i in x.keys():
        x_s[k_i] = x[k_i] * ( scaling[k_i][1]-scaling[k_i][0] ) + scaling[k_i][0]

    return x_s


def fit(activity, to_tune=None, x0=None, ele_name='ele'):
    if not to_tune:
        to_tune = ['hr_slope', 'k_r', 'k_f', 'k_e','hr_rest']

    if not x0:
        x0 = {
            'hr_rest':65, 'hr_slope': 5, 'hr_max': 185,
            'k_r': 0.06, 'k_f': 0.015, 'k_e': 7.2509411294502206e-05,
            'slope_sf': 0.002, 'speed_sf': 0.0085,
            'delay':0
        }

    #x0 = scale_param(x0)

    df = activity.points
    if activity.rideRun == 'run':
        type = 'run'
        #activity.add_slope(x0['slope_sf'],ele_name)
        #print(ele_name)
        #activity.add_speed(x0['speed_sf'])
        df['EC'] = nrgs(df['slopef'])
        df['runPO'] = df['EC'] * df['speedf']

    if activity.rideRun == 'ride':
        type='ride'

    if activity.rideRun in ['ride','run']:
        to_minimize.n = 0
        args = [activity, to_tune, x0, type, ele_name]
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


def fit_seg(activity, to_tune=None, x0=None, ele_name='ele', seg_duration=60*5):
    if not to_tune:
        to_tune = ['hr_slope', 'k_r', 'k_f', 'k_e','hr_rest']
        to_tune = ['hr_slope', 'k_r', 'k_f']

    if not x0:
        x0 = {
            'hr_rest':70, 'hr_slope': 0.0915, 'hr_max': 185,
            'k_r': 0.06, 'k_f': 0.015, 'k_e': 0,
            'slope_sf': 0.002, 'speed_sf': 0.0085,
            'delay':0
        }

    #x0 = scale_param(x0)

    df = activity.points
    if activity.rideRun == 'run':
        type = 'run'
        activity.add_slope(x0['slope_sf'],ele_name)
        print(ele_name)
        activity.add_speed(x0['speed_sf'])
        df['EC'] = nrgs(df['slopef'])
        df['runPO'] = df['EC'] * df['speedf']

    if activity.rideRun == 'ride':
        type='ride'

    if activity.rideRun in ['ride','run']:
        to_minimize.n = 0
        points = activity.points.copy()
        tot_duration = activity.points['time_s'][activity.points.index[-1]]
        seg_num = int(tot_duration/seg_duration)
        x = list(range(0,seg_num))
        x0_list = [x0[name] for name in to_tune]  # initial value of the tuning parameter
        for seg in range(0,seg_num):

            seg_start = seg*seg_duration
            seg_end = (seg+1)*seg_duration-1 # no overlap
            seg_points = points.ix[(points.time_s <= seg_end ) & (points.time_s >= seg_start ),].copy()
            activity.points = seg_points
            activity.points.index = range(0,len(seg_points))
            args = [activity, to_tune, x0, type, ele_name]

        #x = [x0[name] for name in to_tune]
            print(x0_list)
            try:
                fit = scipy.optimize.minimize(fun=to_minimize, x0=x0_list, args=args, method='Nelder-Mead')
                print(seg_start,seg_end)
                nx = fit.get('x')
                x[seg] = x0.copy() # copy the inital value just to get a dictionnary with corret keys
                for name, value in zip(to_tune, nx):
                    x[seg][name] = value
            except:
                x[seg] = {}

            x[seg]['index'] = seg
        activity.points = points.copy()# re-assign activity points with all the points
    else:
        return None



    return pd.DataFrame(x) #de_scale_param(x)


"""
nx : current cardiac parameters
args[0] : current track
args[1] : parameters to tune. Example ['hr_rest', 'hr_slope', 'hr_max']
args[2] : default parameters (dictionnary)
args[3] : track type : 'ride' or 'run'
args[4] : elevation source : 'garmin' or 'google'

return : rms error for the current track
"""


def shift(xs, n, default):
    e = np.empty_like(xs)
    if n >= 0:
        e[:n] = default
        e[n:] = xs[:-n]
    else:
        e[n:] = default
        e[:n] = xs[-n:]
    return e