import numpy as np
import pandas as pd
import json
import matplotlib.pyplot as plt
import re 

from .parsers import *
from . import processing as proc
from . import elevation as ele
from . import hr
from . import hr2

import mplleaflet

class Track:
    def get_type(self):
        activities = pd.read_csv('../data/activities_00.csv', index_col='activity_id')
        return activities.ix[int(self.activity_id), 'activity_type']

    def get_sampling_info(self):
        time_diff = np.ediff1d(self.points.time_s)
        data = {'max': max(time_diff), 'min': min(time_diff), 'median': np.median(time_diff)}
        return data

    def __init__(self, filepath='tcx_folder', platform='garmin', athlete='unknown', activity_id='unknown', type='unkown'):
        try:
            with open('environment.json') as f:
                env = json.load(f)
        except:
            pass
        if filepath == 'tcx_folder':
            tcx_folder = env['tcx_folder']
            platform = 'garmin'
            filepath = '%s%s/%s.tcx' % (tcx_folder, athlete, activity_id)

        if filepath.endswith('.txt'):
            self.points = pd.read_csv(filepath, delim_whitespace=True,
                                      skiprows=3, header=None,
                                      names=['po', 'hr', 'cadence', 'speed', 'timestamp', 'i'])
            self.rideRun = 'ride'

        else:
            # to add ( csv produced by gc_tools.py ):
            # name, date,
            if 'formyfit' in filepath:
                self.athlete = re.split('/',filepath)[3]
                self.activity_id = re.split('/',filepath)[4]
                self.platform = 'formyfit'
            else:
            
                self.athlete = athlete
                self.activity_id = activity_id
                self.platform = platform
            
            self.points, data = parse(filepath)
            self.data = data
            self.sampling_info = self.get_sampling_info()
            self.activity_type = type
            self.rideRun = 'run'
            if (platform == 'garmin') and (type == 'unknown'):
                self.activity_type = self.get_type()
                self.rideRun = 'other'
                if self.activity_type in ['road_biking', 'cycling']:
                    self.rideRun = 'ride'
                if self.activity_type in ['running', 'trail_running', 'street_running']:
                    self.rideRun = 'run'

            if platform != 'fitfile':
                self.add_distances()
            else:
                self.rideRun = 'ride'


        self.hr_x = None


        #self.add_google_elevation()
        self.hr_rms_fit = 10000


    def add_google_elevation(self, use_the_key=True,new_google_key=''):
        ele.add_google_elevation(self.points, use_the_key,new_google_key)

    def add_srtm_elevation(self):
        ele.add_srtm_elevation(self.points)

    def print_url(self):
        # works for allowed activities

        if self.platform == 'garmin':
            print('https://connect.garmin.com/modern/activity/' + self.activity_id)

        if self.platform == 'movescount':
            print('http://www.movescount.com/moves/move' + self.activity_id)

    def add_distances(self):
        proc.add_distances(self.points)
        return
        
    def add_slope(self, sf, ele_name='googleElevation', plot=False, algo='lowess'):
        #proc.add_slope(self.points, sf, ele_name, plot)
        if algo == 'lowess':
            proc.add_slope(self.points, sf, ele_name, plot=plot)
        
        if algo == 'moving_average':    
            self.add_slope3(n=sf,ele_name=ele_name,plot=plot)
        
        #k = 4
        #n = sf*200
        #proc.add_slope2(self.points, n,k, ele_name, plot)


    def add_slope2(self, sf, ele_name='ele', plot=False):
        proc.add_slope2(self.points, sf, ele_name, plot)

    def add_slope3(self, n, ele_name='ele', plot=False):
        proc.add_slope3(self.points, n, ele_name, plot)


    def add_speed(self, sf, plot=False, algo='lowess'):
        
        if algo == 'moving_average':
            proc.add_speed3(self.points, n=sf, plot=plot, 
                                   name=self.athlete+'/'+str(self.activity_id))
            
        if algo == 'lowess':
            proc.add_speed(self.points, frac=sf, plot=plot, 
                                   name=self.athlete+'/'+str(self.activity_id))
        #k = 3
        #n = sf * 200
        #proc.add_speed2(self.points, n, k, plot)

    def has_x_consecutive_missing_values(signal, x):
        dt = np.array(signal.time_s)[1:] - np.array(signal.time_s)[0:-1]
        return sum(dt > x)

    def has_x_consecutive_missing_power_values(self, signal, x):
        return None

    def hr_fit(self, to_tune=None, x0=None, ele_name='ele'):
        self.hr_x = hr.fit(self, to_tune, x0, ele_name)
        return self.hr_x

    def hr_fit2(self, to_tune=None, x0=None):
        self.hr_x = hr2.fit(self, to_tune, x0)
        return self.hr_x

    def hr_fit_seg(self, to_tune=None, x0=None, seg_duration = 30):
        """
        duration in seconds
        """
        self.hr_x = hr.fit_seg(self, to_tune, x0, ele_name='ele', seg_duration=seg_duration)
        return self.hr_x

    def hr_sim(self, x = None,ele_name='googleElevation'):
        if not x:
            x = self.hr_x
        else:
            self.hr_x = x

        if x['slope_sf'] < 0:
            x['slope_sf'] = 0

        if x['speed_sf'] < 0:
            x['speed_sf'] = 0

        df = self.points

        if self.rideRun == 'run':
                #print(x)
                self.add_slope(ele_name=ele_name, sf=x['slope_sf'])
                self.add_speed(x['speed_sf'])
                df['EC'] = hr.nrgs(df['slopef'])
                df['runPO'] = df['EC'] * df['speedf']


        df = self.points
        df['hr_sim'] = hr.hr_sim(self, x)
        err = ((sum((df.hr_sim - df.hr) ** 2)) / len(df)) ** 0.5
        #print(err)

        self.hr_rms_fit = err
        return err
        
    def add_po(self):
        proc.add_po(self.points)

    def hr_sim2(self, x=None):
        if not x:
            x = self.hr_x
        else:
            self.hr_x = x

        df = self.points

        df = self.points
        df['hr_sim'] = hr2.hr_sim(self, x)
        err = ((sum((df.hr_sim - df.hr) ** 2)) / len(df)) ** 0.5
        print(err)

        self.hr_rms_fit = err
        return err

    def hr_plot(self):
        # to do : plot hr ride
        df = self.points

        t = pd.to_datetime(pd.to_datetime(df.timestamp)-pd.to_datetime(df.timestamp)[0])

        if self.rideRun == 'run2':
            plt.figure()
            ax1=plt.subplot(611)
            #plt.plot(t, df['googleElevation'], t, df['ele'])
            plt.plot(t, df['ele'])
            #plt.legend(['google', 'garmin'])
            plt.ylabel('elevation')
            plt.subplot(612,sharex=ax1)
            #plt.plot(t, df['slope'])
            plt.plot(t, df['slopef'])
            plt.ylabel('slope [m/m]')
            plt.legend(['as-is', 'filtred'])

            plt.subplot(613,sharex=ax1)
            plt.plot(t, df['EC'])
            plt.ylabel('slope energy cost [J/m]')

            plt.subplot(615,sharex=ax1)
            plt.plot(t, df['runPO'])
            plt.ylabel('running power')
            plt.ylim(0, 3000)

            ax4=plt.subplot(614,sharex=ax1)
            ax4.plot(t, df['speed'] * 3.6, t, df['speedf'] * 3.6)
            ax4.legend(['as-is', 'filtred'] )
            plt.ylim(0, 20)
            plt.ylabel('speed [km/h]')
            plt.subplot(616,sharex=ax1)
            plt.plot(t, df.hr, t, df.hr_sim)
            plt.legend(['record', 'simulation'],loc=4)
            plt.ylabel('heart rate')
            err = ((sum((df.hr_sim - df.hr) ** 2)) / len(df)) ** 0.5
            print(err)
            plt.show()

        if self.rideRun == 'run':
            import matplotlib.dates as mdates

            plt.figure(num=None, figsize=(16, 10), dpi=80, facecolor='w', edgecolor='k')
            ax1 = plt.subplot(511)
            ax1.set_axis_bgcolor('white')
            plt.plot(t, df['ele']/3)
            plt.ylabel('Elevation [m]')
            
            ax_sl = plt.subplot(512, sharex=ax1)
            ax_sl.set_axis_bgcolor('white')
            plt.plot(t, df.slopef)
            plt.ylabel('Slope [m/m]')
            
            
            ax2 = plt.subplot(513, sharex=ax1)
            ax2.set_axis_bgcolor('white')
            plt.plot(t, df.speedf*3.6)
            plt.plot(t, df['runPO'])
            plt.ylabel('Speed [km/h]')
            plt.legend(['as-is', 'flat eq'],loc='lower right')
            

            ax3 = plt.subplot(514, sharex=ax1)
            ax3.set_axis_bgcolor('white')
            plt.plot(t, df['runPO']*65)
            plt.ylabel('PO [W]')
            
            
            ax4 = plt.subplot(515, sharex=ax1)
            ax4.set_axis_bgcolor('white')
            plt.plot(t, df.hr, t, df.hr_sim)
            plt.legend(['Record', 'Simulation'],loc='lower right')
            plt.ylabel('Heart Rate [bpm]')
            
            
            

            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.gcf().autofmt_xdate()
            plt.xlabel('Time [HH:MM]')
            plt.show()

        if self.rideRun == 'ride' :
            #plt.figure()
            #plt.subplot(121)
            #plt.plot(t, df['googleElevation'], t, df['ele'])
            #plt.plot(t, df['ele'])
            #plt.ylabel('elevation [m]')
            #plt.legend(['google', 'garmin'])
            #plt.subplot(512)
            #plt.plot(t, df['slope'], t, df['slopef'])
            #plt.ylabel('slope [m/m]')
            #plt.legend(['as-is', 'filtred'])

            import matplotlib.dates as mdates

            fig = plt.figure(num=None, figsize=(16, 10), dpi=80, facecolor='w', edgecolor='k')
            ax1 = plt.subplot(211)
            ax1.set_axis_bgcolor('white')
            plt.plot(t, df['po'])
            plt.ylabel('Power Output [W]')
            ax2 = plt.subplot(212,sharex=ax1,)
            ax2.set_axis_bgcolor('white')
            plt.plot(t, df.hr, t, df.hr_sim)
            plt.legend(['Record', 'Simulation'])
            plt.ylabel('Heart Rate [bpm]')

            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            #plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.gcf().autofmt_xdate()
            plt.xlabel('Time [HH:MM]')
            plt.show()

    def plot(self):
        # to do : plot hr ride
        df = self.points

        t = pd.to_datetime(pd.to_datetime(df.timestamp) - pd.to_datetime(df.timestamp)[0])

        if self.rideRun == 'run2':
            plt.figure()
            ax1 = plt.subplot(611)
            # plt.plot(t, df['googleElevation'], t, df['ele'])
            plt.plot(t, df['ele'])
            # plt.legend(['google', 'garmin'])
            plt.ylabel('elevation')
            plt.subplot(612, sharex=ax1)
            # plt.plot(t, df['slope'])
            plt.plot(t, df['slopef'])
            plt.ylabel('slope [m/m]')
            plt.legend(['as-is', 'filtred'])

            plt.subplot(613, sharex=ax1)
            plt.plot(t, df['EC'])
            plt.ylabel('slope energy cost [J/m]')

            plt.subplot(615, sharex=ax1)
            plt.plot(t, df['runPO'])
            plt.ylabel('running power')
            plt.ylim(0, 3000)

            ax4 = plt.subplot(614, sharex=ax1)
            ax4.plot(t, df['speed'] * 3.6, t, df['speedf'] * 3.6)
            ax4.legend(['as-is', 'filtred'])
            plt.ylim(0, 20)
            plt.ylabel('speed [km/h]')
            plt.subplot(616, sharex=ax1)
            plt.plot(t, df.hr, t, df.hr_sim)
            plt.legend(['record', 'simulation'], loc=4)
            plt.ylabel('heart rate')
            err = ((sum((df.hr_sim - df.hr) ** 2)) / len(df)) ** 0.5
            print(err)
            plt.show()

        if self.rideRun == 'run':
            import matplotlib.dates as mdates

            plt.figure(num=None, figsize=(16, 10), dpi=80, facecolor='w', edgecolor='k')
            ax1 = plt.subplot(411)
            ax1.set_axis_bgcolor('white')
            plt.plot(t, df['ele'] / 3)
            plt.ylabel('Elevation [m]')
            ax2 = plt.subplot(412, sharex=ax1)
            ax2.set_axis_bgcolor('white')
            plt.plot(t, df.speedf * 3.6)
            plt.ylabel('Speed [km/h]')

            ax3 = plt.subplot(413, sharex=ax1)
            ax3.set_axis_bgcolor('white')
            plt.plot(t, df['runPO'] / 3)
            plt.ylabel('PO [W]')
            ax4 = plt.subplot(414, sharex=ax1)
            ax4.set_axis_bgcolor('white')
            plt.plot(t, df.hr, t, df.hr_sim)
            plt.legend(['Record', 'Simulation'], loc='lower right')
            plt.ylabel('Heart Rate [bpm]')

            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.gcf().autofmt_xdate()
            plt.xlabel('Time [HH:MM]')
            plt.show()

        if self.rideRun == 'ride':
            # plt.figure()
            # plt.subplot(121)
            # plt.plot(t, df['googleElevation'], t, df['ele'])
            # plt.plot(t, df['ele'])
            # plt.ylabel('elevation [m]')
            # plt.legend(['google', 'garmin'])
            # plt.subplot(512)
            # plt.plot(t, df['slope'], t, df['slopef'])
            # plt.ylabel('slope [m/m]')
            # plt.legend(['as-is', 'filtred'])

            import matplotlib.dates as mdates

            fig = plt.figure(num=None, figsize=(16, 10), dpi=80, facecolor='w', edgecolor='k')

            ax1 = plt.subplot(411)
            ax1.set_axis_bgcolor('white')
            plt.plot(t, df['googleElevation'])
            plt.ylabel('Altitude [m]')

            ax2 = plt.subplot(412, sharex=ax1)
            ax2.set_axis_bgcolor('white')
            plt.plot(t, df['speedf']*3.6)
            plt.ylabel('Speed [km/h]')

            ax3 = plt.subplot(413, sharex=ax1)
            ax3.set_axis_bgcolor('white')
            plt.plot(t, df['po'])
            plt.ylabel('Power Output [W]')

            ax4 = plt.subplot(414, sharex=ax1, )
            ax4.set_axis_bgcolor('white')
            plt.plot(t, df.hr)
            plt.ylabel('Heart Rate [bpm]')



            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            # plt.gca().xaxis.set_major_locator(mdates.DayLocator())
            plt.gcf().autofmt_xdate()
            plt.xlabel('Time [HH:MM]')
            plt.show()


    def hr_plot_seg(self):
        # to do : plot hr ride
        df = self.points
        x = self.hr_x
        t = pd.to_datetime(pd.to_datetime(df.timestamp) - pd.to_datetime(df.timestamp)[0])

        import matplotlib.dates as mdates

        # sim per segment
        for i,x_i in x.iterrows():
            indexes = (df.time_s < (i+1)*30 ) | (df.time_s >= i*30 )
            df_seg = df.ix[indexes]
            sim_seg = hr.hr_sim()


            
    def plot_map(self, dists=[]):
        points = self.points
        plt.figure()
        df = points.ix[~np.isnan(points.lat),]
        plt.plot(df.lon,df.lat,'b',linewidth=4.0)
        plt.plot(df.lon,df.lat,'ws',ms=5, mec='k',mew=1)
        if dists:
            for dist in dists:
                loc = abs(df.computedDist - dist*1000).argmin()
                
                plt.plot(df.lon[loc],df.lat[loc],'ws',ms=15, mec='k',mew=1)
                print("{},{}".format(df.lat[loc],df.lon[loc]) )
                
        mplleaflet.show()

# -------------------------
#fig, ax_po = plt.subplots()
#hr_rest = self.hr_x['hr_rest']
#hr_slope = self.hr_x['hr_slope']
#ax_po.plot(t, df['po'], 'firebrick')

#ax_po.set_ylabel('Power [Watts]')

#ax_hr = ax_po.twinx()


#ax_hr.plot(t, df.hr, t, df.hr_sim)
#ax_hr.set_ylabel('HR [bpm]')
#ax_hr.set_ylim(hr_rest, 140)
#ax_po.set_ylim(0, (140 - hr_rest) / hr_slope)
#ax_hr.grid(b=False)
#ax_po.grid(b=False)

#err = ((sum((df.hr_sim - df.hr) ** 2)) / len(df)) ** 0.5
#print(err)
#plt.show()
