"""
Functions to build weighted_point matrices.
"""

import numpy as np

from mollib.utils.iteration import wrapit
from . import settings


def generate_box(molecules, offset=None, max_length=None, density=None):
    """Generates the points for the box of weighted points around the
    given molecules.
    
    Parameters
    ----------
    molecules: molecule or list of molecule objects (:obj:`mollib.Molecule`)
        Molecule(s) to generate the box around
    offset: 3x1 vector (:obj:`numpy.array`), optional
        The offset vector for the grid positions. If left to None, there is no
        offset.
    max_length: float, optional
        The distance (in Angstroms) to extend the box past the molecule in
        each dimension.
    density: float, optional
        The density of points in Angstroms/point.
    
    Returns
    -------
    weighted_points: 4xN matrix (:obj:`numpy.array`)
        A matrix of 'N' points with the (weight, x, y, z) coordinates for the
        box. The weight of each point is 1.0 by default.
    """
    # Initialize parameters
    max_length = (max_length if isinstance(max_length, float) else
                  settings.box_max_length)
    density = (density if isinstance(density, float) else
               settings.box_density)
    offset = offset if offset is not None else np.array((0.0, 0.0, 0.0))

    # Wrap molecules in a list if needed
    molecules = wrapit(molecules, exclude_iterators=[dict, ])

    # Prepare a list of weighted points
    weighted_points = []

    # Find the smallest and largest x, y and z coordinates
    min_x, max_x = None, None
    min_y, max_y = None, None
    min_z, max_z = None, None

    for molecule in molecules:
        for atom in molecule.atoms:
            point = atom.pos
            if min_x is None or point[0] < min_x:
                min_x = point[0] + offset[0]
            if max_x is None or point[0] > max_x:
                max_x = point[0] + offset[0]
            if min_y is None or point[1] < min_y:
                min_y = point[1] + offset[1]
            if max_y is None or point[1] > max_y:
                max_y = point[1] + offset[1]
            if min_z is None or point[2] < min_z:
                min_z = point[2] + offset[2]
            if max_z is None or point[2] > max_z:
                max_z = point[2] + offset[2]

    # Find the dimensions of the box based on the smallest and largest
    # points
    dim_x = (min_x - max_length / 2., max_x + max_length / 2.)
    dim_y = (min_y - max_length / 2., max_y + max_length / 2.)
    dim_z = (min_z - max_length / 2., max_z + max_length / 2.)

    # Create the box
    x = dim_x[0]
    while x <= dim_x[1]:
        y = dim_y[0]
        while y <= dim_y[1]:
            z = dim_z[0]
            while z <= dim_z[1]:
                weighted_points.append((1.0, x, y, z))  # weight, x, y, z
                z += density
            y += density
        x += density

    return np.array(weighted_points)
