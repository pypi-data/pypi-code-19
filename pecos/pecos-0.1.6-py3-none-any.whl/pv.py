"""
The pv module contains custom methods for PV applications.
"""
import pandas as pd
from pecos.metrics import time_integral
import logging

logger = logging.getLogger(__name__)

def insolation(G, tfilter=None, per_day=True):
    """
    Compute insolation defined as:
    
    :math:`H=\int{Gdt}`
    
    where 
    :math:`G` is irradiance and 
    :math:`dt` is the time step between observations.
    The time integral is computed using the trapezoidal rule.
    Results are given in [irradiance units]*seconds.
    
     Parameters
    -----------
    G : pd.DataFrame
        Irradiance time series
        
    tfilter : pd.Series (optional)
        Time filter containing boolean values for each time index
        
    per_day : boolean (optional)
        Flag indicating if the results should be computed per day, default = True
    
    Returns
    -------
    H : pd.DataFrame
        Insolation
    """
    if type(G) is pd.core.series.Series:
        G = G.to_frame('Irradiance')
        
    H = time_integral(G,  tfilter=tfilter, per_day=per_day)
    
    return H
    
def energy(P, tfilter=None, per_day=True):
    """
    Convert energy defined as:
    
    :math:`E=\int{Pdt}`
    
    where 
    :math:`P` is power and 
    :math:`dt` is the time step between observations.
    The time integral is computed using the trapezoidal rule.
    Results are given in [power units]*seconds.
    
    Parameters
    -----------
    P : pd.DataFrame
        Power time series
         
    tfilter : pd.Series (optional)
        Time filter containing boolean values for each time index
        
    per_day : boolean (optional)
        Flag indicating if the results should be computed per day, default = True
    
    Returns
    -------
    E : pd.DataFrame
        Energy
    """
    if type(P) is pd.core.series.Series:
        P = P.to_frame('Power')
        
    E = time_integral(P, tfilter=tfilter, per_day=per_day)
    
    return E

def performance_ratio(E, H_poa, P_ref, G_ref=1000):
    """
    Compute performance ratio defined as:

    :math:`PR=\dfrac{Y_{f}}{Yr} = \dfrac{\dfrac{E}{P_{ref}}}{\dfrac{H_{poa}}{G_{ref}}}`
    
    where 
    :math:`Y_f` is the observed energy (AC or DC) produced by the PV system (kWh) 
    divided by the DC power rating at STC conditions.
    :math:`Y_r` is the plane-of-array insolation (kWh/m2) divided 
    by the reference irradiance (1000 W/m2).
    
    Parameters
    -----------
    E : pd.DataFrame with a single column or pd.Series
        Energy (AC or DC) 
        
    H_poa : pd.DataFrame with a single column or pd.Series
         Plane of array insolation
         
    P_ref : float
        DC power rating at STC conditions
        
    G_ref : float (optional)
        Reference irradiance, default = 1000
        
    Returns
    -------
    PR : pd.DataFrame
        Performance ratio
    """
    logger.info("Compute Performance Ratio")
    
    if type(E) is pd.core.frame.DataFrame:
        E = pd.Series(E.values[:,0], index=E.index)
    if type(H_poa) is pd.core.frame.DataFrame:
        H_poa = pd.Series(H_poa.values[:,0], index=H_poa.index)
        
    Yf = E/P_ref
    Yr = H_poa/G_ref
    PR = Yf/Yr
    
    PR = PR.to_frame('Performance Ratio')
    
    return PR

def normalized_current(I, G_poa, I_sco, G_ref=1000):
    """
    Compute normalized current defined as:

    :math:`NI = \dfrac{\dfrac{I}{I_{sco}}}{\dfrac{G_{poa}}{G_{ref}}}`
    
    where 
    :math:`I` is current, 
    :math:`I_{sco}` is the short circuit current at STC conditions, 
    :math:`G_{poa}` is the plane-of-array irradiance, and 
    :math:`G_{ref}` is the reference irradiance.
    
    Parameters
    -----------
    I : pd.DataFrame with a single column or pd.Series
        Current
        
    G_poa : pd.DataFrame with a single column or pd.Series
         Plane of array irradiance
         
    I_sco : float
        Short circuit current at STC conditions
        
    G_ref : float (optional)
        Reference irradiance, default = 1000
        
    Returns
    -------
    NI : pd.DataFrame
        Normalized current
    """
    logger.info("Compute Normalized Current")
    
    if type(I) is pd.core.frame.DataFrame:
        I = pd.Series(I.values[:,0], index=I.index)
    if type(G_poa) is pd.core.frame.DataFrame:
        G_poa = pd.Series(G_poa.values[:,0], index=G_poa.index)
        
    N = I/I_sco
    D = G_poa/G_ref
    NI = N/D
    
    NI = NI.to_frame('Normalized Current')
    
    return NI
    
def normalized_efficiency(P, G_poa, P_ref, G_ref=1000):
    """
    Compute normalized efficiency defined as:

    :math:`NE = \dfrac{\dfrac{P}{P_{ref}}}{\dfrac{G_{poa}}{G_{ref}}}`
    
    where 
    :math:`P` is the observed power (AC or DC), 
    :math:`P_{ref}` is the DC power rating at STC conditions, 
    :math:`G_{poa}` is the plane-of-array irradiance, and 
    :math:`G_{ref}` is the reference irradiance.
    
    Parameters
    -----------
    P : pd.DataFrame with a single column or pd.Series
        Power (AC or DC) 
        
    G_poa : pd.DataFrame with a single column or pd.Series
         Plane of array irradiance
         
    P_ref : float
        DC power rating at STC conditions
        
    G_ref : float (optional)
        Reference irradiance, default = 1000
        
    Returns
    -------
    NE : pd.DataFrame
        Normalized efficiency
    """
    logger.info("Compute Normalized Efficiency")
    
    if type(P) is pd.core.frame.DataFrame:
        P = pd.Series(P.values[:,0], index=P.index)
    if type(G_poa) is pd.core.frame.DataFrame:
        G_poa = pd.Series(G_poa.values[:,0], index=G_poa.index)
        
    Yf = P/P_ref
    Yr = G_poa/G_ref
    NE = Yf/Yr
    
    NE = NE.to_frame('Normalized Efficiency')
    
    return NE
    
def performance_index(E, E_predicted):
    """
    Compute performance index defined as:
    
    :math:`PI=\dfrac{E}{\hat{E}}`
    
    where 
    :math:`E` is the observed energy from a PV system and  
    :math:`\hat{E}` is the predicted energy over the same time frame.
    :math:`\hat{E}` can be computed using methods in ``pvlib.pvsystem`` 
    and then convert power to energy using ``pecos.pv.enery``.
    
    Unlike with the performance ratio, the performance index should be very 
    close to 1 for a well functioning PV system and should not vary by 
    season due to temperature variations.
    
    Parameters
    -----------
    E : pd.DataFrame with a single column or pd.Series
        Observed energy
    
    E_predicted : pd.DataFrame with a single column or pd.Series
        Predicted energy
        
    Returns
    ---------
    PI : pd.DataFrame
        Performance index 
    """
    logger.info("Compute Performance Index")
    
    if type(E) is pd.core.frame.DataFrame:
        E = pd.Series(E.values[:,0], index=E.index)
    if type(E_predicted) is pd.core.frame.DataFrame:
        E_predicted = pd.Series(E_predicted.values[:,0], index=E_predicted.index)
        
    PI = E/E_predicted
    
    PI = PI.to_frame('Performance Index')
    
    return PI

def energy_yield(E, P_ref):
    """
    Compute energy yield is defined as:
    
    :math:`EY=\dfrac{E}{P_{ref}}`
    
    where 
    :math:`E` is the observed energy from a PV system and  
    :math:`P_{ref}` is the DC power rating of the system at STC conditions.
    
    Parameters
    -----------
    E : pd.DataFrame with a single column or pd.Series
        Observed energy
    
    P_ref : float
        DC power rating at STC conditions
        
    Returns
    ---------
    EY : pd.DataFrame
        Energy yield  
    """
    logger.info("Compute Energy Yield")
    
    if type(E) is pd.core.frame.DataFrame:
        E = pd.Series(E.values[:,0], index=E.index)

    EY = E/P_ref
    
    EY = EY.to_frame('Energy Yield')
    
    return EY
    
def clearness_index(H_dn, H_ea):
    """
    Compute clearness index defined as:
    
    :math:`Kt=\dfrac{H_{dn}}{H_{ea}}`
    
    where 
    :math:`H_{dn}` is the direct-normal insolation (kWh/m2)
    :math:`H_{ea}` is the extraterrestrial insolation (kWh/m2)
    over the same time frame.
    Extraterrestrial irradiation can be computed using ``pvlib.irradiance.extraradiation``.  
    Irradiation can be converted to insolation using ``pecos.pv.insolation``.
    
    Parameters
    -----------
    H_dn : pd.DataFrame with a single column or pd.Series
        Direct normal insolation
    
    H_ea : pd.DataFrame with a single column or pd.Series
        Extraterrestrial insolation
        
    Returns
    -------
    Kt : pd.DataFrame
        Clearness index
    """
    logger.info("Compute Clearness Index")
    
    if type(H_dn) is pd.core.frame.DataFrame:
        H_dn = pd.Series(H_dn.values[:,0], index=H_dn.index)
    if type(H_ea) is pd.core.frame.DataFrame:
        H_ea = pd.Series(H_ea.values[:,0], index=H_ea.index)
        
    Kt = H_dn/H_ea
        
    Kt = Kt.to_frame('Clearness Index')
    
    return Kt
