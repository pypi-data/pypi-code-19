"""
psychro_display.py
=====
plot psychrometric diagram from TMY data

developed with Python3.5, tested with Python2.7

read a TMY3 file in .csv format, plot all points as humidity ratio
vs dry bulb temperature, show psychrometric diagram on background

plot RH vs Tdry values as scattered points, mark comfort zone on the
psychrometric diagram, count values falling into the comfort zone, 
for other clusters as defined by temperature limits

input:
- directory, file for TMY dataset that contains temperature,
relative humidity values
- temperature limits for ranges T_freeze, T_cold, T_cool, T_warm, T_hot
(all degree Celsius)
- relative humidity limits (%) for the comfort zone in the 'warm'
temperature range

output:
- psychrometric diagram with scattered temperature, humidity values
for the 8760 hours of the tmy year


'solprimer' Python Solar Energy Calculation Primer
Copyright (C) 2017 by Gianguido Piani
contact information : <solarprimer@mailbox.org>

This program is free software: you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.

For a full copy of the GNU General Public License see 
<http://www.gnu.org/licenses/>.

"""
# ===== ensure backward compatibility with Python2.7
from __future__ import division



# ===== Script parameters, insert manually =====
#

# ===== input file

#tmy_filename = 'TMY-EPW_ITA_Rome162420_CONVERT.csv'
#tmy_filename = 'TMY-EPW_DEU_Berlin103840_CONVERT.csv'     # Berlin
#tmy_filename = 'TMY-EPW_RUS_Moscow276120_CONVERT.csv'
#tmy_filename = 'TMY-EPW_RUS_SaintPetersburg260630_CONVERT.csv'
#tmy_filename = 'TMY-EPW_RUS_Yakutsk249590_CONVERT.csv'  # Yakutsk
#tmy_filename = 'TMY-EPW_CHN_TibetLhasa555910_CONVERT.csv'   # Lhasa

#tmy_filename = 'TMY_USA_AZ_Phoenix722780_(TYA)_CONVERT.csv'     # Phoenix
#tmy_filename = 'TMY_USA_HI_HonoluluIntlAP911820_(TYA)_CONVERT.csv'     # Honolulu
tmy_filename = 'TMY_USA_NY-NewYork_JFK744860_(TYA)_CONVERT.csv'     # New York
#tmy_filename = 'TMY_CAN_NU_Resolute719240_(EPW).csv'
#tmy_filename = 'TMY-EPW_SGP_Singapore486980_CONVERT.csv'


# ===== input directory
tmy_directory = 'data-TMY/'


# ===== comfort zone limit parameters
#
# limit parameters for the different temperature and RH clusters
# the number of data points falling into each cluster is counted
# comfort zone is between T_cool and T_warm and RH_low and RH_high

T_freeze=0
T_cold=12
T_cool=20
T_warm=24
T_hot=30
RH_low=40
RH_high=60

# ===== end of manual data input ===============


# =================================
# ========== main script ==========
# =================================
#

import matplotlib.pyplot as plt

import solprim.tmyutility as tmy
import solprim.solartimeposition as stp




def saturation_pressure (temp):

    """
    return the saturation pressure (when RH=100%) of moist air
    as function of input temperature

    input:
    - temperature in range -40..+50 degC, float

    return:
    - saturation pressure of H2O in air in kPa, float
    
    the function is defined on the basis of tabulated values of vapor
    equilibrium pressure at fixed temperature points, intermediate 
    values are interpolated
    
    for temp values <0.01C the tabulated data refers to the ice-gas
    equilibrium

    Gianguido Piani on 2017-02-15, 2017-04-28, 2017-06-07
    
    """
    
    # list of temp/pressure saturation values
    # tp_sat is built as tuple of two lists, one list for temperature
    # (deg C) and one list for the saturation vapor pressure (kPa)

    tp_sat = [(-40,-35,-30,-25,-20,-15,-14,-13,-12,-11,-10,
               -9,-8,-7,-6,-5,-4,-3,-2,-1,0,
               0.01,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,
               18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,
               34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50),
              (0.01284, 0.02235, 0.03801, 0.06329, 0.10326, 0.16530,
               0.18122, 0.19852, 0.21732, 0.23774, 0.25990, 0.28394,
               0.30998, 0.33819, 0.36873, 0.40176, 0.43747, 0.47606,
               0.51772,0.56267,0.61115,0.61165,0.65709,0.70599,
               0.75808,0.81355,0.87258,0.93536,1.00210,1.07300,
               1.14830,1.22820,1.31300,1.40280,1.49810,1.59900,
               1.70580,1.81880,1.93840,2.06470,2.19830,2.33930,
               2.48820,2.64530,2.81110,2.98580,3.16990,3.36390,
               3.56810,3.78310,4.00920,4.24700,4.49690,4.75960,
               5.03540,5.32510,5.62900,5.94790,6.28230,6.63280,
               7.00020,7.38490,7.78780,8.20960,8.65080,9.11240,
               9.59500,10.09900,10.62700,11.17700,11.75200,12.35200)]

    # set limit input min, max values so that index for function
    # 'enumerate' in tp_sat remains within range of defined values
    if temp <= -40.0: temp = -39.9
    if temp > 50.0: temp = 50.0 

    # find index in tp_sat for the value directly higher than the
    # temperature input 
    for i in (i for i, x in enumerate(tp_sat[0]) if x<temp):
        idx = i

    # extrapolate the saturation pressure (linear relation)
    sat_p1 = tp_sat[1][idx]
    sat_p2 = tp_sat[1][idx+1]
    t1 = tp_sat[0][idx]
    t2 = tp_sat[0][idx+1]
    sat_pres = sat_p1 + (sat_p2-sat_p1)*(temp-t1)/(t2-t1)

    return sat_pres



def x_from_rh (temp=25, rh=50, pres=1013.25):

    """
    calculate water content (humidity ratio) x in g H2O
    per kg dry air for given temperature (deg C), relative humidity
    RH%, and air pressure (mbar)

    input:
    - temperature (deg C) [-40..50], float, default =25 C
    - relative humidity RH% [0..100], float, default =50%
    - pres, air pressure in mbar, float, (default is atmospheric
    pressure at STD conditions =1013.25 mbar)
    
    output:
    - water content x in g H2O per kg dry air
    
    Gianguido Piani on 2017-02-17, 2017-04-28, 2017-06-07
    
    """

    p_kPa = pres/10.0       # pressure, convert mbar to kPa
                      
    phi = rh/100.0          # phi = rel.humidity scaled to 0..1
    
    sat_p = saturation_pressure(temp)       # sat_p in kPa
    x = 622*phi*sat_p/(p_kPa-phi*sat_p)     # 622 is 1000*0.622,
                                            # convert kg to g

    return x



def psychro_diagram (t_min=-20, t_max=50, pres=1013.25):

    """
    draw background psychrometric diagram with basic information 
    
    input:
    - t_min, minimum temperature for the x axis, integer, default =-20
    - t_max, maximum temperature for the x axix, integer, default =50
    - pres, air pressure in mbar, float, (default is atmospheric
    pressure at STD conditions =1013.25 mbar)
    
    the pressure is converted to kPa for the thermodynamic
    calculation, pressure(kPa) = pressure(mbar)/10

    """

    r_air = 0.287     # gas constant of air (kJ/kg*K)

    curve_pts = 80   # number of points to build each curve
    t_step = (t_max - t_min)/(curve_pts-1)  # temperature interval step

    # calculate and plot specific humidity x (g vap/ kg dry air)
    # at relative humidity values RH= 10,20,30,40,60,80%

    rh_plot = (10,20,30,40,60,80)   # RH curves to plot

    for i in range (0, len(rh_plot)):
        
        temp_plot = []      # T values to plot curves for RH=const
        x_g = []            # calculated x (g_water per kg_air)
    
        for j in range (0, curve_pts+1):
            temp = t_min + j*t_step     # temp values to plot the curve
            if temp > 0:                # plot only for temp > 0
                temp_plot.append(temp)
                x_g.append(x_from_rh(temp,rh_plot[i],pres))


        plt.plot(temp_plot, x_g, color='#d2693e') # RGB color given in hex

   
    # plot the absolute humidity value curve 
    temp_plot = []
    x_g = []
    for j in range (0, curve_pts+1):
        temp = t_min + j*t_step     # temp values to plot the curve
        temp_plot.append(temp)
        x_g.append(x_from_rh(temp,100,pres))

    plt.plot(temp_plot, x_g, 'k-')     # plot t_pg, x_g for RH=100%


    # write texts on drawing canvas
    #
    plt.axis([t_min,t_max,0,40])   # chart range
    plt.tick_params(axis='y', which='both', labelleft='off',
                    labelright='on')
    plt.xlabel('dry bulb temperature (deg C)')
    
    # ylabel cannot be positioned on right margin,
    # place text directly on figure canvas instead
    #
    yaxis_text = 'humidity ratio (g H2O / kg dry air)'
    plt.figtext(0.95, 0.50, yaxis_text, family='sans-serif', fontsize=10,
                verticalalignment='center', rotation=90)

    # print text with RH% value near upper termination of the curve
    # the position coordinates can be changed for a better placement
    #
    plt.text(27.2, 38.3, 'RH=100%', color='#555555', size=10)
    plt.text(35.5, 36.5, '80%', color='#d2693e', size=10)
    plt.text(36, 28, '60%', color='#d2693e', size=10)
    plt.text(36, 18.5, '40%', color='#d2693e', size=10)
    plt.text(36, 13.5, '30%', color='#d2693e', size=10)
    plt.text(36, 9.2, '20%', color='#d2693e', size=10)
    plt.text(32.5, 1.8, 'RH=10%', color='#d2693e', size=10)


    return



# ===== main procedure =====
#

# ===== read data
tmy_data = tmy.tmy_readcsv(tmy_directory + tmy_filename)

# show location metadata on terminal output
print (tmy_data[0])
print ('')

latitude = tmy_data[0]['Latitude']
longitude = tmy_data[0]['Longitude']
country = tmy_data[0]['Country']
city = tmy_data[0]['City']



# get data for Tdry, relative himidity from the input dataset
Tdry_list = tmy_data[1]['Tdry']
rh_list = tmy_data[1]['RH']
pres_list = tmy_data[1]['Pres']

patm = 101.325 # standard atmospheric pressure in kPa

# input data is 8760 hourly values for temperature, RH, pressure
# the data is attached to different lists (i.e., put in different
# clusters) depending on temperature 'T' and water content 'w' values.
# cluster (1) : T<T_freeze
# cluster (2) : T_freeze < T < T_cold
# cluster (3) : T_cold < T < T_cool
# cluster (4) : T_cool < T < T_warm and # RH_low < RH < RH_high
# cluster (5) : T_cool T < T_hot or outside RH_low-RH_high range
# cluster (6) : T > T_hot
#
# cluster (5) contains points for all T_cool < T < T_warm
# outside the RH comfort range and T_warm < T < T_hot

data_T1      = []
data_w1      = []
data_T2      = []
data_w2      = []
data_T3      = []
data_w3      = []
data_T4      = []
data_w4      = []
data_T5      = []
data_w5      = []
data_T6      = []
data_w6      = []

# iterate over all TMY hours [0..8760]
# for each hour calculate water content x from temp, RH, pressure
# add temp, x to cluster in relation to temp, RH
#

for i in range(0, 8760):
    T_i = Tdry_list[i]
    RH_i = rh_list[i]
    pres_i = pres_list[i]
    
    # get absolute water content "w" (g per kg dry air)
    w_i = x_from_rh (T_i, RH_i, pres_i)

    # assign T, RH values to the appropriate cluster depending on T:
    # freeze, cold, cool, comfort, warm, hot

    if (T_i < T_freeze):
        data_T1.append(T_i)
        data_w1.append(w_i)
    
    elif (T_i < T_cold):
        data_T2.append(T_i)
        data_w2.append(w_i)
    
    elif (T_i < T_cool):
        data_T3.append(T_i)
        data_w3.append(w_i)

    elif (T_i < T_warm):        # T, RH in comfort range
        if (RH_i >= RH_low and RH_i <= RH_high):
            data_T4.append(T_i)
            data_w4.append(w_i)
        else:                   # T, RH outside comfort range
            data_T5.append(T_i)
            data_w5.append(w_i)

    elif (T_i < T_hot):
        data_T5.append(T_i)
        data_w5.append(w_i)

    else:
        data_T6.append(T_i)
        data_w6.append(w_i)



# ===== plot the psychrometric chart 
#

plt.figure()
ax = plt.subplot(111)

plt.grid(True)


# plot diagram on background
# find temperature range for psychrometric diagram depending
# on min, max values of Tdry temperature
# min T value for plot is -40 C, max is +50 C, cap limits

Tmin = min(Tdry_list)
Tmax = max(Tdry_list)

if (Tmin > 0):
    Tplot_min = 0
else:
    Tplot_min = -(int(-Tmin/10)+1)*10

if (Tmin < -40):
    Tplot_min = -40

if (Tmax > 40):
    Tplot_max = 50
else:
    Tplot_max = 40


# average pressure at selected location
P_plot = round((sum(pres_list)/8760), 3)    

# plot background diagram at selected pressure
psychro_diagram(Tplot_min, Tplot_max, P_plot)

# plot data from each group as scatter with different colour
mrk = '.'   # define marker in plot
plt.scatter(data_T1, data_w1, marker = mrk, color='#2080ff')
plt.scatter(data_T2, data_w2, marker = mrk, color='#9999ff')
plt.scatter(data_T3, data_w3, marker = mrk, color='#777000')
plt.scatter(data_T4, data_w4, marker = mrk, color='#009936')
plt.scatter(data_T5, data_w5, marker = mrk, color='#ffb000')
plt.scatter(data_T6, data_w6, marker = mrk, color='#ff3000')

# plot texts
header_text = ('psychrometric chart at ' + str(round(P_plot, 2)) +
               ' mbar (' + str(round(P_plot/1013.25, 2))+' atm)')

plt.title(header_text, family='sans-serif', size=10)
 

# prepare boxed texts in the psychrometric diagram 

# heating and cooling degree days information
deg_days = tmy.tmy_hdd_cdd (Tdry_list)

geo_coord = stp.geo_coordinates(longitude, latitude)

loc_text = ('Location: '+ country + '_' + city +
            ' (' + geo_coord + ')')

box_text1 = (loc_text + '\n' +
             'average pressure (mbar) = ' + str(P_plot) + '\n' +
             'heating degree days (HDD) = ' + str(deg_days[0]) + '\n' +
             'cooling degree days (CDD) = ' + str(deg_days[1]))

# temperature range information
T_bin = (data_T1, data_T2, data_T3, data_T5, data_T6)
T_ref = (T_freeze, T_cold, T_cool, T_hot, int(max(Tdry_list))+1)

for i in range (0, len(T_bin)):
    if (len(T_bin[i]) > 0):
        box_text1 = (box_text1 + '\n' + 
                     'hours in T range [' +
                     str(int(min(T_bin[i]))) + '..' +
                     str(T_ref[i]) + ']: ' +
                     str(len(T_bin[i])) + ' (' +
                     str((round((len(T_bin[i])/87.60),1))) +
                     '%),  T_avg=' +
                     str(round(sum(T_bin[i])/len(T_bin[i]),1)))


# comfort zone information

if (len(data_T4) > 0):
    box_text2 = ('hours in T range [' + str(T_cool) + '..' +
                 str(T_warm) + '] with comfort RH%\n' +
                 'hours: ' + str(len(data_T4)) + ' (' +
                 str((round((len(data_T4)/87.60),1))) +
                 '%),   T_avg=' +
                 str(round(sum(data_T4)/len(data_T4),1)))
else:
    box_text2 = 'no points in T, RH comfort range'


# print on output display
print (box_text1 + '\n')
print (box_text2)


# get scaled y coordinates (scaling is automatic, it depends on
# values for x, y), which result from the selected temperatures.
# compute new relative coordinates to place text boxes in plot.
xlim = plt.gca().get_xlim()     # get x coordinates after scaling 
xpos = xlim[0] + (xlim[1]-xlim[0])*0.02

ylim = plt.gca().get_ylim()     # get y coordinates after scaling 
ypos_1 = ylim[1] * 0.55
ypos_2 = ylim[1] * 0.40

ax.text(xpos, ypos_1, box_text1, family='sans-serif', size=10,
        bbox={'facecolor':'white', 'alpha':0.5, 'pad':5})

ax.text(xpos, ypos_2, box_text2, family='sans-serif', size=11, color='b',
        bbox={'facecolor':'white', 'edgecolor':'blue',
              'alpha':1.0, 'pad':5})


# display result
plt.show()
plt.close()





