"""Handle measurement of RMSD (root mean square distance).


"""
import numpy as np
from scipy.spatial.distance import cdist, pdist, squareform


def rmsd(x, y):
    delta = x - y
    N = len(delta)
    np.multiply(delta, delta, delta)
    return np.sqrt((delta.sum() / N))


def fitted_rmsd(x, y, centered=False):
    """ Return rotation matrix and fitted rmsd for two numpy arrays.

    Fitted RMSD calculated using KABSCH Algorithm.
    """

    if centered is False:
        x_center = np.mean(x, axis=0)
        y_center = np.mean(y, axis=0)
        np.subtract(x, x_center, x)
        np.subtract(y, y_center, y)

    cov_mat = np.dot(x.T, y)
    V, S, Wt = np.linalg.svd(cov_mat, full_matrices=True)
    d = np.sign(np.linalg.det(np.dot(Wt.T, V.T)))*1
    idd_mat = np.array([[1, 0, 0], [0, 1, 0], [0, 0, d]])
    U = np.dot(np.dot(Wt.T, idd_mat), V.T)
    rmsd_fit = rmsd(x, np.dot(y, U))
    return rmsd_fit, U


def interface(rec_coords, lig_coords, interface_d):
    dists = cdist(rec_coords, lig_coords, 'sqeuclidean')
    indices = np.any(dists < (interface_d * interface_d), axis=0).nonzero()[0]
    return indices


def calc_rmsd(ag, ref, interface=None):
    ag_coords = ag.getCoordsets()
    ref_coords = ref.getCoords()
    if interface is not None:
        ag_coords = ag_coords[:, interface, :]
        ref_coords = ref_coords[interface, :]

    delta = ag_coords - ref_coords
    delta_sq = delta * delta

    return np.sqrt(delta_sq.sum(axis=(1, 2))/len(ref_coords))


def calc_fitted_rmsd(ag, ref, centered=False):
    """ Return rotation matrix and fitted rmsd for atom groups.

    Assumes ag has multiple coordinate sets. Calculates fitted
    RMSD using KABSCH Algorithm between each coordinate set and
    provided reference structure.
    """
    ag_coords = ag.getCoordsets()
    ref_coords = ref.getCoords()

    if centered is False:
        ag_ctr = np.mean(ag_coords, axis=1)
        ref_ctr = np.mean(ref_coords, axis=0)
        ag_ctr = np.reshape(ag_ctr, (len(ag_coords), 1, 3))
        np.subtract(ag_coords, ag_ctr, ag_coords)
        np.subtract(ref_coords, ref_ctr, ref_coords)

    rmsds = []
    Us = []
    for coords in ag_coords:
        cov_mat = np.dot(ref_coords.T, coords)
        V, S, Wt = np.linalg.svd(cov_mat, full_matrices=True)
        d = np.sign(np.linalg.det(np.dot(Wt.T, V.T)))*1
        idd_mat = np.array([[1, 0, 0], [0, 1, 0], [0, 0, d]])
        U = np.dot(np.dot(Wt.T, idd_mat), V.T)
        rmsds.append(rmsd(ref_coords, np.dot(coords, U)))
        Us.append(U)

    return rmsds, Us


def interface_pwrmsd(rec, lig, interface_d=10.0, condensed=False):
    """Return matrix of interface pairwise RMSDs for lig.

    Assumes lig has multiple coordinate sets, such as is the case when lig was
    produced by apply_ftresults_atom_group.
    """
    transformed = lig.getCoordsets()
    N = lig.numCoordsets()

    interfaces = [interface(rec.getCoords(), coords, interface_d)
                  for coords in transformed]

    dists = np.zeros((N, N), dtype=np.float64)
    for i in range(N):
        for j in range(i, N):
            combined_interface = np.union1d(interfaces[i], interfaces[j])
            if len(combined_interface) == 0:
                d = -1
            else:
                d = rmsd(transformed[i][combined_interface],
                         transformed[j][combined_interface])
            dists[i, j] = dists[j, i] = d

    if condensed:
        return squareform(dists)
    return dists


def pwrmsd(lig, condensed=False):
    """Return matrix of pairwise RMSDs lig.

    Assumes lig has multiple coordinate sets, such as is the case when lig was
    produced by apply_ftresults_atom_group.
    """
    N = lig.numCoordsets()

    condensed_dists = pdist(lig._getCoordsets().reshape(N, -1), 'sqeuclidean')
    np.divide(condensed_dists, lig.numAtoms(), condensed_dists)
    np.sqrt(condensed_dists, condensed_dists)
    if not condensed:
        return squareform(condensed_dists)
    return condensed_dists


def srmsd(crys, pdbs, only_ca=False, only_backbone=False, only_interface=False,
          interface_radius=10.0, rec=None):
    """Return list of RMSDs for each structure in the ``pdbs`` list.
    """
    if only_interface and rec is None:
        raise ValueError("only_interface requires rec")

    if only_ca:
        crys = crys.select('name CA')
        pdbs = tuple(map(lambda p: p.select('name CA'), pdbs))
    elif only_backbone:
        crys = crys.select('backbone')
        pdbs = tuple(map(lambda p: p.select('backbone'), pdbs))

    crys_coords = crys.getCoords()
    pdb_coords = (p.getCoords() for p in pdbs)

    if only_interface:
        i = interface(rec.getCoords(), crys.getCoords(), interface_radius)

        crys_coords = crys_coords[i]
        pdb_coords = (c[i] for c in pdb_coords)

    return [rmsd(crys_coords, coords) for coords in pdb_coords]
