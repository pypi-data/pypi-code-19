from haversine import haversine as simpleDist2d
import numpy as np
import statsmodels.api as sm
import scipy.optimize
import matplotlib.pyplot as plt
from scipy.interpolate import splrep, splev
import seaborn
import matplotlib.dates as mdates
import pandas as pd

def add_distances(points):
    """
    Compute point to point distances using haversine formula
    """

    valid_positions= ~( np.isnan(points.lat) | np.isnan(points.lon) )
    df=points.ix[valid_positions,].copy()
    
    df['prevLat']=df.lat.shift(1)
    df['prevLon']=df.lon.shift(1)
    df.ix[df.index[0],'prevLat']=df.lat[df.index[0]]
    df.ix[df.index[0],'prevLon']=df.lon[df.index[0]]

    points['pp_dist']=df.apply(lambda row: simpleDist2d((row['lat'],row['lon']),(row['prevLat'],row['prevLon'])),axis=1)*1000
    points['computedDist']=points.pp_dist.cumsum()   


def resample(points, dist):
    pass


def add_slope2(points, n,k, ele_name='ele', plot=False):
    # take valid elevation points
    valid_ele = ~(np.isnan(points[ele_name]))
    df = points.ix[valid_ele,].copy()
    f = splrep(df.computedDist, df[ele_name], k=k, s=n)
    df['slopef'] = splev(df.computedDist,f, der=1)
    df['ele_f'] = splev(df.computedDist, f)

    points.ix[valid_ele, 'slopef'] = df['slopef']
    points.ix[valid_ele, 'ele_f'] = df['ele_f']


    points.ix[points.slopef > 0.5, 'slopef'] = 0.5
    points.ix[points.slopef < -0.5, 'slopef'] = -0.5

    if plot:
        plt.figure()
        ax1=plt.subplot(211)
        plt.plot(df.computedDist, df[ele_name], df.computedDist, df.ele_f)
        # plt.legend(['ele', ele_name, 'resampling'])
        plt.subplot(212,sharex=ax1)
        plt.plot(df.computedDist, df.slopef)
        plt.xlabel('distance [m]')
        plt.show()


def add_speed2(points, n,k,  plot=False):
    valid_points = ~(np.isnan(points.lat) | np.isnan(points.lon) | \
                     np.isnan(points.pp_dist) | np.isnan(points.time_s))

    df = points.ix[valid_points,].copy()

    f = splrep(df.time_s, df.computedDist, k=k, s=n)
    df['speedf'] = splev(df.time_s,f, der=1)
    points.ix[valid_points, 'speedf'] = df['speedf']

    if plot:
        plt.plot(df.time_s, df.speedf)
        plt.xlabel('time [s]')

        
def add_speed3_bk(points, n,  plot=False, name=''):
    # take valid  points
    valid_points = (~(np.isnan(points['lat']))) &( ~(np.isnan(points['time_s'])))

    df = points.ix[valid_points,]

    if(n<1):
        n = 1

    # resample 1s
    times = range(0, int(df.time_s[len(df) - 1]), 1)
    dists_re = scipy.interpolate.interp1d(df.time_s, df.computedDist, fill_value='extrapolate')(times)


    speedf = np.empty_like(dists_re)
    for i in range(n,len(speedf)):
        speedf[i] = (dists_re[i] - dists_re[i-n])/(times[i]-times[i-n])
    
    speedf[0:n] = 0
        
    speed = np.empty_like(dists_re)
    for i in range(1,len(speed)):
        speed[i] = (dists_re[i] - dists_re[i-1])/(times[i]-times[i-1])

    
    speed[0] = 0

    points.ix[valid_points, 'speedf'] = scipy.interpolate.interp1d(times, speedf, fill_value='extrapolate')(df.time_s)
    points.ix[valid_points, 'speed'] = scipy.interpolate.interp1d(times, speed, fill_value='extrapolate')(df.time_s)

    

    #points.ix[points.slopef > 0.5, 'slopef'] = 0.5
    #points.ix[points.slopef < -0.5, 'slopef'] = -0.5

    if plot==True:
        df = points
        t = pd.to_datetime(pd.to_datetime(df.timestamp) - pd.to_datetime(df.timestamp)[0])
        plt.figure()
        
        ax1=plt.subplot(211)
        plt.title(name)
        plt.plot(t, df.hr)
        plt.ylabel('hr')
        
        
        plt.subplot(212,sharex=ax1)
        plt.xlabel('temps [s]')
        plt.plot(t, df['speed']*3.6,t, df['speedf']*3.6)
        plt.ylabel('speed [km/h]')
        #plt.ylim([0, 20])
        plt.legend(['as is','filtered ({:d}s)'.format(n)])
        
        
        
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gcf().autofmt_xdate()
        plt.xlabel('Time [HH:MM]')

        plt.show()
        
    if plot=='m':
        t = pd.to_datetime(pd.to_datetime(df.timestamp) - pd.to_datetime(df.timestamp)[0])
        plt.figure()
        
        ax1=plt.subplot(311)
        plt.title(name)
        plt.plot(t, df.hr)
        plt.ylabel('FC')
        
        ax1=plt.subplot(312,sharex=ax1)
        plt.plot(t, df.ele,t,df.googleElevation)
        plt.ylabel('elevation')
        plt.legend(['formyfit','google maps api'])
        
        plt.subplot(313,sharex=ax1)
        plt.xlabel('temps [s]')
        plt.plot(t, df['speed']*3.6,
                 t, df['speedf5']*3.6,
                 t, df['speedf10']*3.6,
                 t, df['speedf15']*3.6,
                 t, df['speedf20']*3.6)
        plt.ylabel('vitesse [km/h]')
        #plt.ylim([0, 20])
        plt.legend(['tel quel',
                    'filtre ({:d}s)'.format(5),
                    'filtre ({:d}s)'.format(10),
                    'filtre ({:d}s)'.format(15),
                    'filtre ({:d}s)'.format(20)])
        
        
        
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M'%S"))
        # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gcf().autofmt_xdate()
        plt.xlabel("Temps [HH:MM'SS]")

        plt.show()
        

    

    #points.ix[points.slopef > 0.5, 'slopef'] = 0.5
    #points.ix[points.slopef < -0.5, 'slopef'] = -0.5

    if plot==True:
        df = points
        t = pd.to_datetime(pd.to_datetime(df.timestamp) - pd.to_datetime(df.timestamp)[0])
        plt.figure()
        
        ax1=plt.subplot(211)
        plt.title(name)
        plt.plot(t, df.hr)
        plt.ylabel('hr')
        
        
        plt.subplot(212,sharex=ax1)
        plt.xlabel('temps [s]')
        plt.plot(t, df['speed']*3.6,t, df['speedf']*3.6)
        plt.ylabel('speed [km/h]')
        #plt.ylim([0, 20])
        plt.legend(['as is','filtered ({:d}s)'.format(n)])
        
        
        
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gcf().autofmt_xdate()
        plt.xlabel('Time [HH:MM]')

        plt.show()
        
    if plot=='m':
        t = pd.to_datetime(pd.to_datetime(df.timestamp) - pd.to_datetime(df.timestamp)[0])
        plt.figure()
        
        ax1=plt.subplot(311)
        plt.title(name)
        plt.plot(t, df.hr)
        plt.ylabel('FC')
        
        ax1=plt.subplot(312,sharex=ax1)
        plt.plot(t, df.ele,t,df.googleElevation)
        plt.ylabel('elevation')
        plt.legend(['formyfit','google maps api'])
        
        plt.subplot(313,sharex=ax1)
        plt.xlabel('temps [s]')
        plt.plot(t, df['speed']*3.6,
                 t, df['speedf5']*3.6,
                 t, df['speedf10']*3.6,
                 t, df['speedf15']*3.6,
                 t, df['speedf20']*3.6)
        plt.ylabel('vitesse [km/h]')
        #plt.ylim([0, 20])
        plt.legend(['tel quel',
                    'filtre ({:d}s)'.format(5),
                    'filtre ({:d}s)'.format(10),
                    'filtre ({:d}s)'.format(15),
                    'filtre ({:d}s)'.format(20)])
        
        
        
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%H:%M'%S"))
        # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gcf().autofmt_xdate()
        plt.xlabel("Temps [HH:MM'SS]")

        plt.show()
        

def add_slope3(points, n, ele_name='ele', plot=False):
    # take valid elevation points
    valid_ele = ~(np.isnan(points[ele_name]))
    df = points.ix[valid_ele,].copy()

    if(n<1):
        n = 1

    # resample every meter
    dists = range(0, int(df.computedDist[len(df) - 1]), 1)
    ele_re = scipy.interpolate.interp1d(df.computedDist, df[ele_name], fill_value='extrapolate')(dists)

    
    slope = np.empty_like(ele_re)
    for i in range(n,len(slope)-n):
        slope[i] = ( sum(ele_re[i:i+n]) - sum(ele_re[i-n:i]) )/(n*n)
    

    slope[0:n] = 0
    slope[-n:] = 0

    points.ix[valid_ele, 'slopef'] = scipy.interpolate.interp1d(dists, slope, fill_value='extrapolate')(df.computedDist)


    #points.ix[points.slopef > 0.5, 'slopef'] = 0.5
    #points.ix[points.slopef < -0.5, 'slopef'] = -0.5

    if plot:
        
        df = points
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(211)
        ax1.plot(df.computedDist, df["ele"])
        if "googleElevation" in df.columns:
            ax1.plot(df.computedDist, df['googleElevation'])
            ax1.legend(['recorder','google'])

            
            
        plt.ylabel('Elevation [m]')
        
        # plt.legend(['ele', ele_name, 'resampling'])
        ax2 = fig1.add_subplot(212,sharex=ax1)
        ax2.plot(df.computedDist, df.slopef)
        ax2.set_ylabel('slope [m/m]')
        plt.title(ele_name)


def add_slope(points, frac, ele_name='ele', plot=False):
    """
    frac should depend on the distance between consecutive points
    points need to have elevation and distance from start
    frac : fraction of the points used per 10 km
    """
    # take valid elevation points
    valid_ele = ~(np.isnan(points[ele_name]))
    df = points.ix[valid_ele,].copy()

    # normalize frac parameter
    fracn = frac * 10000 / df.computedDist[len(df) - 1]

    # resample every meter
    dists = range(0, int(df.computedDist[len(df) - 1]), 1)
    ele_re = scipy.interpolate.interp1d(df.computedDist, df[ele_name], fill_value='extrapolate')(dists)

    dele = np.ediff1d(ele_re, to_begin=0)  # difference between consecutive elevations

    x = sm.nonparametric.lowess(dele, dists, frac=fracn)

    df['slopef'] = scipy.interpolate.interp1d(x[:, 0], x[:, 1], fill_value='extrapolate')(df.computedDist)
    df['slope'] = scipy.interpolate.interp1d(dists, dele, fill_value='extrapolate')(df.computedDist)

    points.ix[valid_ele, 'slopef'] = df['slopef']
    points.ix[valid_ele, 'slope'] = df['slope']

    points.ix[points.slopef > 0.5, 'slopef'] = 0.5
    points.ix[points.slopef < -0.5, 'slopef'] = -0.5

    if plot:
        #print(fracn)
        plt.figure()
        ax1 = plt.subplot(211)
        #plt.plot(df.computedDist, df['ele'], df.computedDist, df[ele_name], '-o', dists, ele_re, 'o')
        plt.plot(df.computedDist, df['ele'], df.computedDist, df[ele_name])
        plt.legend(['ele', ele_name])
        plt.subplot(212,sharex=ax1)
        plt.plot(points.computedDist, points.slopef)
        plt.xlabel('distance [m]')

        plt.show()
    
    print('couc')


def add_speed(points, frac, plot=False, name=''):
    """
    frac :fraction of points used per hour of track
    """
    valid_points = ~( np.isnan(points.lat) | np.isnan(points.lon) | \
                    np.isnan(points.pp_dist) | np.isnan(points.time_s) )

    df=points.ix[valid_points,].copy()
    fracn=frac*3600/df.time_s[len(df)-1] # normalized for 1-hour activity

    # resample every 1s
    time_re = range(0, int(df.time_s[len(df) - 1]), 1)
    dist_re = scipy.interpolate.interp1d(df.time_s, df.computedDist, \
                                         fill_value='extrapolate')(time_re)
    # as dists are distances every 1s, consecutive differences are speed in [m/s]
    computed_speed = np.ediff1d(dist_re, to_begin=0)  # difference between consecutive distances


    x=sm.nonparametric.lowess(computed_speed, time_re, frac=fracn)
    speedf=scipy.interpolate.interp1d(x[:,0],x[:,1],fill_value='extrapolate')(df.time_s)
    speed=scipy.interpolate.interp1d(time_re,computed_speed,fill_value='extrapolate')(df.time_s)

    points.ix[valid_points, 'speedf'] = speedf
    points.ix[valid_points, 'speed'] = speed
    
    if plot==True:
        plt.figure()
        df = points
        t = pd.to_datetime(pd.to_datetime(df.timestamp) - pd.to_datetime(df.timestamp)[0])
       
        
        ax1=plt.subplot(211)
        plt.title(name)
        plt.plot(t, df.hr)
        plt.ylabel('hr')
        
        
        plt.subplot(212,sharex=ax1)
        plt.xlabel('temps [s]')
        plt.plot(t, df['speed']*3.6,t, df['speedf']*3.6)
        plt.ylabel('speed [km/h]')
        #plt.ylim([0, 20])
        plt.legend(['as is','filtered ({:.2f})'.format(frac)])
        
        
        
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gcf().autofmt_xdate()
        plt.xlabel('Time [HH:MM]')

        plt.show()




def nrgs(s):
        """
        energy cost per meter on a slope s
        :param s:
        :return:
        """
        return 155.4 * s ** 5 - 30.4 * s ** 4 - 43.3 * s ** 3 + 46.3 * s ** 2 + 19.5 * s + 3.6





        
def add_po(points, plot=False):
   
    valid_points = ~(np.isnan(points.lat)     | np.isnan(points.lon)    |   \
                     np.isnan(points.pp_dist) | np.isnan(points.time_s) |   \
                     np.isnan(points.speedf)  | np.isnan(points.slopef) )
    df = points.ix[valid_points,].copy()
    df['EC'] = nrgs(df['slopef'])
    df['runPO'] = df['EC']*df['speedf']
    
    
    points.ix[valid_points,'runPO'] = df.runPO

def addPower(points):
    pass


