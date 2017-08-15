"""
Functions to select points in a weighted_points matrix based on different 
shapes and geometries.
"""
from math import cos, sin, pi

import numpy as np
from scipy import spatial

from .weighted_points import get_points
from mollib.core.geometry import cross, vector_length


def select_sphere(weighted_points, center, radius):
    """Select the points in weighted_points that fall within the volume of the
    specified sphere.

    Parameters
    ----------
    weighted_points: 4xN matrix (:obj:`numpy.array`)
        A matrix of 'N' points with the (weight, x, y, z) coordinates. 
    center: 3x1 matrix (:obj:`numpy.array`)
        The x, y and z coordinates for the center of the sphere (in Angstroms).
    radius: float
        The radius of the sphere (in Angstroms).

    Returns
    -------
    rows: list of int
        The point index numbers in weighted_points that fall within the 
        sphere's volume.
    """
    # Initialize parameters
    selected_points = []  # points to select
    points = get_points(weighted_points)
    radius_2 = radius ** 2

    # Find all of the points in weighted_points that should be excluded
    for row, point in enumerate(points):
        x = point[0] - center[0]
        y = point[1] - center[1]
        z = point[2] - center[2]

        if x ** 2 + y ** 2 + z ** 2 < radius_2:
            selected_points.append(row)

    return selected_points


def select_prolate(weighted_points, center, theta, phi, long, short):
    """Select the volume of a prolate from a weighted points matrix.

    Prolates have a long axis, two short axes and a theta/phi angle for the
    long axis with respect to the weighted_points matrix.

    Parameters
    ----------
    weighted_points: 4xN matrix (:obj:`numpy.array`)
        A matrix of 'N' points with the (weight, x, y, z) coordinates.
        This function will remove points from this matrix.
    center: 3x1 matrix (:obj:`numpy.array`)
        The x, y and z coordinates for the center of the sphere (in Angstroms).
    theta: float
        The polar angle (in degrees) of the prolate long axis with respect to
        the weighted_point matrix. The rotation is conducted about the y-axis.
    phi: float
        The azimuthal angle (in degrees) of the prolate long axis with respect
        to the weighted_point matrix. The rotation is conducted about the 
        z-axis.
    long: float
        The long axis length (in Angstroms) of the prolate to select.
    short: float
        The short axis length (in Angstroms) of the prolate to select.

    Returns
    -------
    rows: list of int
        The point index numbers in weighted_points that fall within the 
        prolate's volume.
    """
    # Initialize parameters
    selected_points = []  # points to select
    points = get_points(weighted_points)
    long, short = max(long, short), min(long, short)

    # Determine the unit vector of the long axis for the prolate
    long_vector = (sin(theta * pi / 180.) * cos(phi * pi / 180.),
                   sin(theta * pi / 180.) * sin(phi * pi / 180.),
                   cos(theta * pi / 180.))
    long_vector = np.array(long_vector)

    # Determine an orthogonal unit vector to use as one of the short axes.
    # If the length of the short_vector is 0.0, then it is colinear with the
    # long vector
    short_vector1 = cross(long_vector, np.array((0.0, 0.0, 1.0)))
    length = vector_length(short_vector1)
    if length <= 0.01:
        short_vector1 = cross(long_vector, np.array((1.0, 0.0, 0.0)))
        length = vector_length(short_vector1)
    short_vector1 /= length
    short_vector2 = cross(long_vector, short_vector1)
    length = vector_length(short_vector2)
    short_vector2 /= length

    # Find all of the points in weighted_points that should be excluded
    for row, point in enumerate(points):
        # Determine the location of the point
        ref_point = point - np.array(center)

        # Project the point's vector to the prolate's coordinate system,
        # u, v, w
        u = np.dot(ref_point, short_vector1)
        v = np.dot(ref_point, short_vector2)
        w = np.dot(ref_point, long_vector)

        if ((u ** 2 + v ** 2) / short ** 2 +
            w ** 2 / long ** 2 < 1.0):
            selected_points.append(row)

    return selected_points


def select_difference(weighted_points1, weighted_points2, threshold=0.1):
    """Select the volume of points in weighted_points1 but not in
    weighted_points2.
    
    difference = weighted_points1 - weighted_points2
    
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
    rows: list of int
        The point index numbers in weighted_points1 that are not in 
        weighted_points2.
        
    Examples
    --------
    >>> import numpy as np
    >>> weighted_points1 = np.array([[1.0, 1, 2, 3],
    ...                              [1.0, 4, 5, 6],
    ...                              [1.0, 7, 8, 9],
    ...                              [1.0, 10, 11, 12]])
    >>> weighted_points2 = np.array([[1.0, 1, 2, 3],
    ...                              [1.0, 10, 11, 12]])  # missing rows 1,2
    >>> select_difference(weighted_points1, weighted_points2)
    [1, 2]
    >>> # Excluded all points based on a large threshold
    >>> select_difference(weighted_points1, weighted_points2, threshold=50.)
    []
    """
    # Initialize parameters
    points1 = get_points(weighted_points1)
    points2 = get_points(weighted_points2)
    tree2 = spatial.cKDTree(points2)

    # Go through points in weighted_points1 to see if there are an points in
    # weighted_points2 that match within 'threshold'.
    selected_rows = []

    for count, point in enumerate(points1):
        matching_rows = tree2.query_ball_point(point, threshold)

        # If there are no matching_rows, then point is in weighted_points1, but
        # not in weighted_points2
        if not matching_rows:
            selected_rows.append(count)

    return selected_rows


