import numpy as np
from scipy.spatial.distance import cdist

from mollib.utils.iteration import wrapit
from mollib.utils.interactions import interaction_atoms
from .data_types import PRE
from .weighted_points import get_weights, get_points


def pre_integrator(weighted_points, data, molecules):
    """Integrate the PRE values from weighted_points for the PREs list in data.
    
    Parameters
    ----------
    weighted_points: 4xN matrix (:obj:`numpy.array`)
        A matrix of 'N' points with the (weight, x, y, z) coordinates. 
        This function will remove points from this matrix.
    data: dict
        A dict with the experimental data. 
        - **key**: interaction labels (str). ex: '14N-H'
        - **value**: Datum objects (:obj:`mollib.paramagnetic.PRE`)
    molecules: molecule or list of molecule objects (:obj:`mollib.Molecule`)
        Molecule(s) to exclude from the weighted_point matrix.

    Returns
    -------
    calculated: dict
        A dict with the data. 
        - **key**: interaction labels (str). ex: '14N-H'
        - **value**: Calculated values (`mollib.paramagnetic.PRE`)
    """
    # Initial parameters
    points = get_points(weighted_points)  # These are just the point positions
    weights = get_weights(weighted_points)  # These are the point weights

    # Wrap molecules in a list if needed
    molecules = wrapit(molecules, exclude_iterators=[dict, ])

    # Prepare the calculated data return value
    calc_values = {}

    # Go through each experimental data point in 'data' and calculate the
    # corresponding observable value
    for label, pre in data.items():
        # The following calculations only work for PREs
        if not isinstance(pre, PRE):
            continue

        # Retrieve the atom related to this PRE
        for molecule in molecules:
            # Get the atom. For a PRE measurement, it should only be one atom.
            atom = interaction_atoms(label, molecule)
            if len(atom) != 1 or len(atom[0]) != 1 or atom is None:
                continue
            atom = atom[0][0]

            # Calculate the r^-6 distances between the atom an all points in
            # the grid.

            # The atom vector must first be converted to a 2d array
            atom_pos = np.array([atom.pos])

            # The cdist return matrix corresponds to the distance for all points
            dists = cdist(atom_pos, points, 'euclidean')

            # Calculate the weighted r^-6 dependence
            dists_6 = np.dot(dists**-6, weights)

            # Calculate the distance between the atom and all points over the
            # weighted_points grid
            calc_value = calc_values.get(label, 0.0)
            calc_value += sum(dists_6)
            calc_values[label] = calc_value

    return calc_values


