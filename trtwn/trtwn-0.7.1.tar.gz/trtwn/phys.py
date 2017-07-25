import numpy as np
import scipy.constants as sc

def spp_dispersion_relation_from_w(w, e_1, e_2):
    return w/sc.c * np.sqrt(e_1 * e_2/(e_1 + e_2))

def bulk_plasmon_dispersion_relation_from_w(w, w_p):
    return np.sqrt((w**2-w_p**2)/sc.c**2)

def bulk_plasmon_dispersion_relation_from_k(k, w_p):
    return np.sqrt(w_p**2 + k**2 * sc.c**2)

def nm_to_eV(nm):
    return sc.h*sc.c/(nm * sc.e * sc.nano)

def eV_to_nm(eV):
    return sc.h*sc.c/(eV * sc.e * sc.nano)

def k_beat_to_k_spp(k_beat, wavelength, wavelength_error, angle_in_deg=65):
    angle = np.sin(angle_in_deg/180 * np.pi)
    k_spp = k_beat + 2 * np.pi/wavelength * angle
    delta_k_spp = np.abs(2 * np.pi / wavelength**2 * angle * wavelength_error)
    return k_spp, delta_k_spp

def k_spp_to_n_eff(k_spp, laser_wavelength):
    return k_spp/(2 * np.pi/laser_wavelength)