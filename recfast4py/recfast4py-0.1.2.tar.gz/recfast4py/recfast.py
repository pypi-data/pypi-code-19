

from ._recfast import recombination


def Xe_frac(Yp, T0, Om, Ob, OL, Ok, h100, Nnu, F, fDM,
            switch=0, npz=1000, zstart=10000, zend=0.001):
    """
    perform the normal Recfast computation

    :param Yp: Temperature of CMB at z=0
    :param Omega: matter
    :param Omega: Baryons
    :param Omega: Lambda
    :param Omega: Curvature
    :param h100:
    :param Nnu: effective number of neutrinos
    :param F: fudge-factor; normally F=1.14
            fDM [eV/s] which gives annihilation efficiency;
             typical value fDM=2.0e-24 eV/s (see Chluba 2010 for definitions)
    :param switch: (optional) on/off recombination corrections
                              (Chluba & Thomas 2010)
    :param npz: (optional) number of point in z
    :param zstart: (optional) starting point of z
    :param zend: (optional) end point of z

    :returns: zarr, Xe_H, Xe_He, Xe ,TM
    """
    return recombination(Yp, T0, Om, Ob, OL, Ok, h100, Nnu, F, fDM, switch,
                         npz, zstart, zend)
