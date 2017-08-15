"""
Functions to exclude points from weighted_point matrices.
"""
from scipy import spatial

from mollib.utils.iteration import wrapit
from .selectors import select_sphere, select_prolate, select_difference
from .weighted_points import get_points, exclude_points
from . import settings


def exclude_molecules(weighted_points, molecules, exclusion_cutoff=None):
    """Remove the volume of the molecule from a weighted points matrix.
    
    Parameters
    ----------
    weighted_points: 4xN matrix (:obj:`numpy.array`)
        A matrix of 'N' points with the (weight, x, y, z) coordinates. 
        This function will remove points from this matrix.
    molecules: molecule or list of molecule objects (:obj:`mollib.Molecule`)
        Molecule(s) to exclude from the weighted_point matrix.
    exclusion_cutoff: float, optional
        The cutoff distance (in Angstroms) from atoms in a molecule to remove 
        weighted points.
    
    Returns
    -------
    weighted_points: 4xM matrix (:obj:`numpy.array`)
        A matrix of 'M' points with the (weight, x, y, z) coordinates, such that
        M <= N. This is the new weighted_points matrix with the molecule volume
        excluded.
    """
    # Wrap molecules in a list if needed
    molecules = wrapit(molecules, exclude_iterators=[dict, ])

    # Initialize parameters
    points = get_points(weighted_points)
    tree = spatial.cKDTree(points)

    # The cutoff distance from atoms to exclude points from the grid
    cutoff = (exclusion_cutoff if exclusion_cutoff is not None else
              settings.exclusion_cutoff)

    # The index number of the box points to exclude
    excluded_rows = []

    # Go through all of the points and remove points that are within the
    # cutoff of points.
    for molecule in molecules:
        for atom in molecule.atoms:
            point = atom.pos
            excluded_list = tree.query_ball_point(point, cutoff)
            excluded_rows += excluded_list

    # Return the new weighted_points matrix with the rows removed
    return exclude_points(weighted_points, excluded_rows)


def exclude_sphere(weighted_points, center, radius):
    """Remove the volume of a sphere from a weighted points matrix.
    
    Parameters
    ----------
    weighted_points: 4xN matrix (:obj:`numpy.array`)
        A matrix of 'N' points with the (weight, x, y, z) coordinates. 
        This function will remove points from this matrix.
    center: 3x1 matrix (:obj:`numpy.array`)
        The x, y and z coordinates for the center of the sphere (in Angstroms).
    radius: float
        The radius of the sphere (in Angstroms).
    
    Returns
    -------
    weighted_points: 4xM matrix (:obj:`numpy.array`)
        A matrix of 'M' points with the (weight, x, y, z) coordinates, such 
        that M <= N. This is the new weighted_points matrix with the sphere 
        volume excluded.
    """
    excluded_rows = select_sphere(weighted_points, center, radius)
    return exclude_points(weighted_points, excluded_rows)


def exclude_prolate(weighted_points, center, theta, phi, long, short):
    """Remove the volume of a prolate from a weighted points matrix.
    
    Parameters
    ----------
    weighted_points: 4xN matrix (:obj:`numpy.array`)
        A matrix of 'N' points with the (weight, x, y, z) coordinates. 
        This function will remove points from this matrix.
    center: 3x1 matrix (:obj:`numpy.array`)
        The x, y and z coordinates for the center of the sphere (in Angstroms).
    theta: float
        The polar angle (in degrees) of the prolate long axis with respect to
        the weighted_point matrix. The rotation is conducted about the x-axis
    phi: float
        The azimuthal angle (in degrees) of the prolate long axis with respect
        to the weighted_point matrix.
    long: float
        The long axis length (in Angstroms) of the prolate to select.
    short: float
        The short axis length (in Angstroms) of the prolate to select.

    Returns
    -------
    weighted_points: 4xM matrix (:obj:`numpy.array`)
        A matrix of 'M' points with the (weight, x, y, z) coordinates, such 
        that M <= N. This is the new weighted_points matrix with the prolate 
        volume excluded.
    """
    excluded_rows = select_prolate(weighted_points, center, theta, phi,
                                   long, short)
    return exclude_points(weighted_points, excluded_rows)


def difference(weighted_points1, weighted_points2, threshold=0.1):
    """Return the weighted_points grid of points for the difference between
    weighted_points1 and weighted_points2. 
    
    i.e. points in weighted_points1 but not weighted points2.)
    
    Parameters
    ----------
    weighted_points1: 4xN matrix (:obj:`numpy.array`)
        A matrix of 'N' points with the (weight, x, y, z) coordinates.
    weighted_points2: 4xN matrix (:obj:`numpy.array`)
        A matrix of 'N' points with the (weight, x, y, z) coordinates.
    threshold: float, optional
        If a point in weighted_points2 is within 'threshold' to a point in 
        weighted_points1, then it will not be included as a difference.
    
    Returns
    -------
    difference_weighted_points: 4xM matrix (:obj:`numpy.array`)
        A matrix of 'M' points with the (weight, x, y, z) coordinates for points
        in weighted_points1 but not in weighted_points2.
        
    Examples
    --------
    >>> import numpy as np
    >>> weighted_points1 = np.array([[1.0, 1, 2, 3],
    ...                              [1.0, 4, 5, 6],
    ...                              [1.0, 7, 8, 9],
    ...                              [1.0, 10, 11, 12]])
    >>> weighted_points2 = np.array([[1.0, 1, 2, 3],
    ...                              [1.0, 10, 11, 12]])  # Missing row 1, 2
    >>> difference(weighted_points1, weighted_points2)  # Returns rows 1, 2
    array([[ 1.,  4.,  5.,  6.],
           [ 1.,  7.,  8.,  9.]])
    """
    selected_rows = select_difference(weighted_points1, weighted_points2,
                                      threshold)
    return weighted_points1[selected_rows,:]
