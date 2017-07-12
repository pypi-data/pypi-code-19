"""
solprim_solartimeposition.py
=====
functions related to solar time and position

developed with Python3.5, tested with Python2.7

call package with 'import solprim_pckg.solartimeposition as stp'

functions included
    - day_of_year (localdate)
    - timeoffset_tz (localdate)
    - equation_of_time (d)
    - true_solar_time (localtime, longitude)
    - local_time_from_solar (solartime, localtime, longitude)
    - solar_time_HHMM (solartime)
    - hour_angle_decimal (solartime, eot, longitude, timezone)
    - hour_angle_localtime (localtime)
    - solar_declination (d)
    - sunrise_hour (sol_decl, latitude)
    - solar_azim_elev (sol_decl_rad, hour_angle_rad, latitude_rad)
    - clearsky_radiation (latitude, height)
    - incidence_factor (sol_elev_sin, sol_elev_cos, srf_tilt_sin,
                        srf_tilt_cos, sol_azim_rad, srf_azim_rad)
    - geo_coordinates (longitude, latitude)
    

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


import datetime as dt
import math


def day_of_year (localdate):
    
    """
    returns the day of year [1..365 or 366] for a particular date and time

    input:
    - date and time in Python datetime format including timezone
    (time and timezone may be omitted)

    returns:
    - day of year 'd', integer
    the returned day of year is for the UTC date and time corresponding
    to a local date, time, and timezone. If time or timezone are omitted,
    the day od year 'd' refers to the local date.

    """
    
    d = localdate.utctimetuple().tm_yday

    return d



def timeoffset_tz (localdate):
    
    """
    returns the timezone from utc_offset in a Python datetime object

    input:
    local (official) date and time in Python datetime format with timezone
    
    returns:
    the timezone as float with one decimal

    the timezone is returned from the datetime object as utcoffset
    timedelta in days and seconds

    """

    # 'try' to detect when utcoffest days, seconds is undefined 
    try:
        offset_day = localdate.utcoffset().days
    except:
        offset_day = 0

    try:
        offset_sec = localdate.utcoffset().seconds
    except:
        offset_sec = 0

    # 1 hour is equal 3600 seconds
    offset_tz = round((offset_day*86400 + offset_sec)/3600, 1)    

    return (offset_tz)



def equation_of_time (d):
    
    """
    returns the Equation Of Time for given day of year

    input:
    - day of year (day=1 is January 1), integer [1..365]

    output:
    correction factor in minutes (decimal with fraction part) for
    the given day, float

    The Equation Of Time is computed with the approximate relation
    from C.Julian Chen, Physics of Solar Energy, John Wiley & Sons,
    2011, Eq.4.75 p.101

    """

    eot = round(9.85*math.sin(4*math.pi*(d-80)/365.2422) -
                7.65*math.sin(2*math.pi*(d-3)/365.2422), 2)

    return eot



def true_solar_time (localtime, longitude=0):
    
    """
    returns the true solar time from the local time

    input:
    - local (official) date and time in Python datetime format with
    timezone
    - longitude, decimal degrees (positive values East of Greenwich),
    float

    output:
    - solar true time as decimal hour with two decimals, float
    
    The true solar time is computed from the local (official) time by
    adding correction factors for timezone, longitude, Equation of Time
    (which depends on the day of year)

    at 12.00 true solar time the sun has maximum elevation,
    sunrise and sunset time are equally distant from/to noon

    """

    tst_hour = localtime.timetuple().tm_hour

    tst_min = round((localtime.timetuple().tm_min/60), 2)

    tst_lon = round((longitude/15), 2)

    tst_tz = timeoffset_tz(localtime)
    
    tst_eot = round((equation_of_time(localtime)/60), 2)
    
    # add up the separate components expressed as decimal hours
    # round up the result
    solar_time = tst_hour + tst_min + tst_lon - tst_tz + tst_eot 

    # correct for hour outside the range [0..23]
    if (solar_time > 23):
        solar_time = solar_time - 24

    if (solar_time < 0):
        solar_time = solar_time + 24

    # round up and truncate with two decimals
    solar_time = int(solar_time * 100) / 100
    
    
    return solar_time



def local_time_from_solar (sun_time, localtime, longitude=0):
    
    """
    returns the local time from the true solar time

    input:
    - sun_time, solar true time as hour with two decimals, float
    - localtime, local (official) date in Python datetime format with
    timezone
    - longitude, decimal degrees (positive values East of Greenwich),
    float

    output:
    - local time as datetime object


    This is the inverse function to 'true_solar_time'
    The local time is computed from the true solar time by adding
    correction factors for timezone, longitude, Equation of Time
    (EoT depends on the day of year)
    EoT correction is not passed as argument to the function, but it
    is calculated from the date of the 'localtime' variable
    
    """

    tst_lon = round((longitude/15), 2)

    tst_tz = timeoffset_tz(localtime)
    
    tst_eot = round((equation_of_time(day_of_year(localtime))/60), 2)

    # add up the separate components, get local hour in decimal format
    localhour_dec = sun_time - tst_lon + tst_tz - tst_eot
    
    # check and correct change of day for calculated local time
    # the change of day is not corrected in the datetime object because
    # the solar time does not contain date information

    if (localhour_dec >= 24):
        localhour_dec = localhour_dec - 24

    if (localhour_dec < 0):
        localhour_dec = localhour_dec + 24

    loc_hr = int(localhour_dec)
    loc_min = int(round((localhour_dec-loc_hr)*60, 2))

    localtime = localtime.replace(hour=loc_hr, minute=loc_min)

    return localtime



def solar_time_HHMM (sun_time):
    
    """
    converts the true solar time in decimal form into the string format
    'hh:mm' with minutes in range [0..59]
    
    Use output for graphical representations, tables, plots.
    
    input:
    - true solar time as hour with two decimals, float
    
    output:
    - string with hh:mm (24h) representation

    """

    hour = int(sun_time)

    minute = int((sun_time-hour)*60)

    # date and time constructor
    localtime = dt.time(hour, minute)   # class builder

  
    return localtime.strftime('%H:%M')




def hour_angle_decimal (sun_time, eot=0, longitude=0, timezone=0):
    
    """
    returns the hour angle from solar time in decimal format

    correction factors for equation of time, longitude, timezone
    may be passed here, though they are not required

    input:
    - local (solar) time in decimal format, float
    - eot, equation of time, minues with decimal fraction, float
    - longitude at the location, degrees, float
    - timezone of the location (positive East of Greenwich),
    integer/float
    
    output:
    - the hour angle in decimal degrees [-180..+180], float

    """

    solar_time = sun_time + eot/60 + longitude/15 - timezone
                   
    hra = round ((solar_time-12)*15, 3)
    
    return hra




def hour_angle_localtime (localtime):
    
    """
    returns the hour angle from time in Python datetime format
    no corrections for equation of time, longitude, timezone
    
    this function is used for the generation of solar path plots,
    where the time input is already in naive format and no eot
    correction is necessary

    input:
    - localtime, local (solar) time in Python datetime format
    
    output:
    - hour angle in decimal degrees [-180..+180], float

    """

    hour = localtime.hour
    minute = localtime.minute

    hra = round ((hour-12)*15 + minute/4, 3)
    
    return hra




def solar_declination (d):
    
    """
    calculate the solar declination angle for given day of year

    input:
    - day of year (day=1 is January 1), integer [1..365]

    output:
    - solar declination angle for the given day, decimal degrees, float

    The solar declination is computed with the approximate relation
    from C.Julian Chen, Physics of Solar Energy, John Wiley & Sons,
    2011, Eq.4.27 p.85

    the error can be up to 1.60 degrees

    the function does not return a value =0 but a slightly different
    one in order to avoid inconsistencies in the calculation of solar
    azimuth, elevation

    """

    ecl = 23.45     # obliquity of the ecliptic, 23.45 degrees

    sol_decl = round(ecl*math.sin(2*math.pi*(d-80)/365.2422)+0.01, 2)

    return sol_decl



def sunrise_hour (sol_decl=0, latitude=0):
    
    """
    calculate the sunrise hour from solar declination, latitude
    
    input:
    - solar declination, decimal degrees, float 
    - latitude, decimal degrees (positive North of equator), float

    output:
    tuple with
    - sunrise hour angle from 12noon (half day length) in decimal
    degrees, float, absolute value
    - sunrise time (apparent solar time) in decimal hours, float
    - sunset time (apparent solar time) in decimal hours, float
    - flag sr_correct=True means that the calculation is correct,
    sunrise/sunset time is in correct range, day length is >0 hours
    and <24 hours
    - flag sunup_flag=True indicates polar day, otherwise polar night
    when the flag sr_correct=True, sunup_flag is meaningless 

    the sunrise and sunset time are equally distant from/to noon

    sunrise time is 12 - sunrise hour
    sunset time is 12 + sunrise hour

    """

    # tan function is undefined for +-90 deg, limit the latitude value 
    if (latitude > 89.999):
        latitude = 89.999
    elif (latitude < -89.999):
        latitude = -89.999

    # convert input angles to radians
    sol_decl_rad = math.radians(sol_decl)   
    latitude_rad = math.radians(latitude)
    
    
    # sunrise angle argument
    sr_arg = - (math.tan(sol_decl_rad) * math.tan(latitude_rad))

    # verify argument range, whether result will be correct
    sr_correct = False
    sunup_flag = False

    if (sr_arg <= -1):
        sunup_flag = True     # sun is up 24h, polar day
        sr_hour_deg = 0.0  
        sr_time = 0.0  
        ss_time = 0.0  
       
    elif (sr_arg < 1):      # argument in range [-1..1]
        sr_correct = True          # result is acceptable
        sr_hour_rad = math.acos(sr_arg)     

    else:       # in case sr_arg >= +1
        sr_hour_deg = 0.0    # sun is down 24h, polar night
        sr_time = 0.0  
        ss_time = 0.0  

    # if the argument is in correct range, calculate sunrise angle
    if (sr_correct):
        sr_hour_deg = abs(math.degrees(sr_hour_rad))

        sr_time = 12 - sr_hour_deg/15   # sunrise time in decimal hours
        ss_time = 12 + sr_hour_deg/15   # sunset time in decimal hours


    return sr_hour_deg, sr_time, ss_time, sr_correct, sunup_flag




def solar_azim_elev (sol_decl_rad=0, hour_angle_rad=0, latitude_rad=0):
    
    """
    calculate the solar azimuth and elevation
    
    returns a tuple with sun azimuth and elevation angles
    in both decimal degrees and radians as well as their
    trigonometric values for given declination, hour angle, latitude

    input:
    - solar declination, radians, float
    - hour_angle, radians [-pi..+pi] (noon is zero, morning negative),
    float
    - latitude, radians (positive North of equator), float

    output:
    tuple:
    - elevation angle in degrees [0..+90]
    - azimuth angle in degrees [-180..+180]
    - elevation angle in radians [0..+pi/2]
    - azimuth angle in radians [-pi..+pi]
    - elevation angle sine [-1..1]
    - elevation angle cosine [-1..1]
    - azimuth angle cosine [-1..1]


    the equations are based on M. Iqbal "An Introduction to Solar
    Radiation", Academic Press, 1983, Chapter 1.5 "Position of the Sun
    Relative to Horizontal Surfaces", with adjustments

    if the calculated elevation angle is <= 0, then the sun is below
    the horizon, all output values are set =0
    
    the variables names have the suffixes:
    _rad - angle in radians
    _deg - angle in degrees
    _sin - sin(angle)
    _cos - cos(angle)

    """

    # angular trigonometric functions
    sol_decl_sin = math.sin(sol_decl_rad)
    sol_decl_cos = math.cos(sol_decl_rad)
    hour_angle_cos = math.cos(hour_angle_rad)

    latitude_sin = math.sin(latitude_rad)
    latitude_cos = math.cos(latitude_rad)

    elev_sin = (sol_decl_sin * latitude_sin +
                sol_decl_cos * latitude_cos * hour_angle_cos)

    elev_rad = math.asin(elev_sin)
    elev_cos = math.cos(elev_rad)

    azim_cos = (((elev_sin * latitude_sin) - sol_decl_sin)/
                (elev_cos * latitude_cos))

    # by numerical approximation cos may become >1 and lead to error
    # limit value to [-1.0..-1.0]
    if (azim_cos > 1.0):  
        azim_cos = 1.0    
    elif (azim_cos < -1.0):
        azim_cos = -1.0

    # compute azimuth with same sign as hour angle
    azim_rad = math.acos(azim_cos) * math.copysign(1, hour_angle_rad)

    # correction for compass direction due North=0 or South =180
    azim_rad = math.pi+azim_rad

    # convert azimuth, elevation to decimal degrees
    azim_deg = round(math.degrees(azim_rad), 2)
    elev_deg = round(math.degrees(elev_rad), 2)


    return (elev_deg, azim_deg, elev_rad, azim_rad,
            elev_sin, elev_cos, azim_cos)



def clearsky_radiation (latitude=0, elevation=0):

    """
    generate hourly clear-sky solar irradiation [0..8759] for one year

    generate hourly solar irradiation data values [0..8759] for the
    whole year in the components global horizontal irradiation (ghi),
    direct / beam normal irradiation (dni), diffuse horizontal
    irradiation (dhi) under the assumption of a perfectly clear sky
    and simplified physical relations

    input
    - latitude in decimal degrees (positive North of equator), float
    - elevation over sea level in m, float

    output
    - list with ghi values [0..8759] in W/m2, integer
    - list with dni values [0..8759] in W/m2, integer
    - list with dhi values [0..8759] in W/m2, integer

    """

    # initial constants
    sol_const = 1367   # solar extraterrestrial radiation W/m2

    atm_factor = 0.67    # approx one atmosphere filtering factor 
    dhi_factor = 0.10    # approx relation dhi over dni

    # coefficients for air_mass_factor equation by E.G.Laue
    height_factor = 0.14    # for the air_mass_factor equation
    ch = height_factor * elevation/1000

    # other coefficients
    latitude_rad = math.radians(latitude)


    # lists for ghi, dni, dhi

    ghi_list = []
    dni_list = []
    dhi_list = []


    # lists for intermediate variables, for testing purposes of
    # the hourly value of intermediate variables.
    # These lists are not necessary for regular operation of the 
    # 'clearsky_radiation' function.

    hra_time_list = []
    sol_azim_list = []
    sol_elev_list = []
    etr_list = []
    air_mass_list = []
    am_fact_list = []
                      

    for d in range (0, 365):    # day of year

        # solar declination
        sol_decl = solar_declination(d)
        sol_decl_rad = math.radians(sol_decl)

        # solar extraterrestrial radiation (ETR) as function of day 
        # of year. equation from D.Yogi Goswami, Principles of Solar
        # Engineering, 3rd Ed, CRC Press, 2015, Eq 2.35, p.62
        etr_day = (sol_const *
                   (1 + 0.034 * math.cos(2*math.pi*d/365.25)))
        
        # if 24h has regular day/night cycle, calculate the ETR fractional
        # part for the first and last hour of the day
        # this is necessary because approximate values for ghi/dni
        # in the first and last daylight hour calculated with the same
        # equation as for the other hours lead to incorrect results
        sr_hour = sunrise_hour (sol_decl, latitude)

        if (sr_hour[3]):    # when flag=True sunrise hour is correct
            h_sunrise = int(sr_hour[1])  # full sunrise hour
            h_sunset = int(sr_hour[2])  # full sunset hour
            etr_sunr = etr_day * (sr_hour[2]-h_sunset)  # sunrise hour ETR
        else:
            h_sunrise = -1   # polar day
            h_sunset = 24

        for h in range (0, 24):

            # calculate hour angle, convert to radians
            hra = hour_angle_decimal(h)
            hra_rad = math.radians(hra)

            # the function solar_azim_elev returns the solar position
            # as tuple
            sol_pos = solar_azim_elev(sol_decl_rad, hra_rad,
                                      latitude_rad)
            air_mass = 0

            # if daytime or polar day assign etr_day = extraterr.radiation
            # at sunrise, sunset hours etr_day is reduced in proportion
            # to daylight
            # calculate air mass factor from solar elevation
            # solar position calculated at the mid of the hour
            # to better approximate the full hour period
            #
            # air mass equation by F. Kasten and A. T. Young, quoted in
            # D.Yogi Goswami, Principles of Solar Engineering, 3rd Ed.,
            # CRC Press, 2015, Chap.2.5
            #
            # air mass factor equation by E. G. Laue (1970)
            

            if (((h > h_sunrise) and (h < h_sunset) and (sr_hour[3]))
                or (sr_hour[4])):

                hour_ref = hour_angle_decimal(h + 0.5)
                hra_rad = math.radians(hour_ref)
                
                sol_pos = solar_azim_elev(sol_decl_rad, hra_rad,
                                          latitude_rad)
                sol_elev = sol_pos[0]
                sol_elev_sin = sol_pos[4]

                # avoid calculation errors if elevation angle <0
                if (sol_elev < 0): sol_elev = 0
                if (sol_elev_sin < 0): sol_elev_sin = 0
                
                air_mass = (1 /
                            (sol_elev_sin + 0.50572 *
                             pow((6.07995+sol_elev),-1.6364)))
                air_mass_factor = (ch + (1-ch) *
                                   pow(0.7, pow(air_mass, 0.678)))
                
                etr_fact = etr_day  # full value for ETR factor

            elif ((h == h_sunrise) or (h == h_sunset)):

                am_fact = 0

                for i in range (0, 20):
                    hour_ref = hour_angle_decimal(h + i*0.05)
                    hra_rad = math.radians(hour_ref)
                    sol_pos = solar_azim_elev(sol_decl_rad, hra_rad,
                                              latitude_rad)
                    sol_elev = sol_pos[0]
                    sol_elev_sin = sol_pos[4]

                    if (sol_elev > 0):
                        air_mass = (1 /
                                    (sol_elev_sin + 0.50572 *
                                     pow((6.07995+sol_elev),-1.6364)))
                        am_fact = (am_fact + 0.05 *
                                   (ch + (1-ch) *
                                    pow(0.7, pow(air_mass, 0.678))))

                air_mass_factor = am_fact

                etr_fact = etr_sunr  # ETR fraction at sunrise, sunset hr

            else:
                air_mass = 0
                air_mass_factor = 0
                sol_elev = 0
                sol_elev_sin = 0
                etr_fact = 0

            dni = etr_day * air_mass_factor
            dhi = dni * dhi_factor
            ghi = (dni * sol_elev_sin) + dhi

            ghi_list.append(int(ghi))
            dni_list.append(int(dni))
            dhi_list.append(int(dhi))

            hra_time_list.append(hra)
            sol_azim_list.append(sol_pos[1])
            sol_elev_list.append(sol_pos[0])
            etr_list.append(etr_fact)
            air_mass_list.append(air_mass)
            am_fact_list.append(air_mass_factor)


    return (ghi_list, dni_list, dhi_list,
            hra_time_list, sol_azim_list, sol_elev_list,
            etr_list, air_mass_list, am_fact_list)




def incidence_factor (sol_elev_sin, sol_elev_cos, srf_tilt_sin,
                      srf_tilt_cos, sol_azim_rad, srf_azim_rad):

    """
    return the cos of the angle of incidence of a beam on a flat plane

    returns the cosine of the angle theta of a solar radiation beam
    indicated by the solar position azimuth and elevation angles
    over a flat surface described with tilt over ground, azimuth.

    This function accepts solar position angles calculated via
    'solar_azim_elev'. In order to avoid chains of calculations followed
    by their inverses, the calculated trigonometric values sin, cos
    for the solar position and the flat surface orientation are passed
    as function arguments instead of their angle values. The function
    'solar-azim_elev' returns calculated trigonometric values together
    with the angle values.

    input:
    - sol_elev_sin : sin of solar elevation angle, float [0..1]
    - sol_elev_cos : cos of solar elevation angle, float [0..1]
    - srf_tilt_sin : sin of flat surface tilt angle, float [0..1]
    - srf_tilt_cos : cos of flat surface tilt angle, float [0..1]
    - sol_azim_rad : solar azimuth angle in rad, float 
    - srf_azim_rad : flat surface azimuth angle in rad, float
    
    output:
    - cosine of the angle theta between the solar beam and the normal
    to the oriented panel
    
    """

    # transformation equation as shown in pveducation.org
    # http://pveducation.org/pvcdrom/arbitrary-orientation-and-tilt 
    cos_theta = (sol_elev_cos * srf_tilt_sin *
                 math.cos(sol_azim_rad - srf_azim_rad) +
                 sol_elev_sin * srf_tilt_cos)

    # cos_theta may yield a result <0, for example at the full hour
    # before dawn or after sunset. cos_theta < 0 is set to 0

    if (cos_theta < 0):
        cos_theta = 0

    return cos_theta



def geo_coordinates (longitude=0, latitude=0):
    
    """
    transform geographical coordinates given as longitude [-180..+180]
    and latitude [-90..+90] in a string with absolute indications and
    'N', 'S', 'E', 'W' 

    input:
    - longitude, decimal degrees, float
    - latitude, decimal degrees, float
    
    output:
    - string in format '27.34N 14.82E'

    """

    if (latitude >= 0):
        lat_dir = 'N'
        lat_val = str(round (latitude, 2))
    else:
        lat_dir = 'S'
        lat_val = str(round (-latitude, 2))

    if (longitude >= 0):
        lon_dir = 'E'
        lon_val = str(round (longitude, 2))
    else:
        lon_dir = 'W'
        lon_val = str(round (-longitude, 2))
        
    coord = lat_val + '' + lat_dir + ' ' + lon_val + '' + lon_dir
    
    return (coord)



