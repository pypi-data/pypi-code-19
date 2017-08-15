"""
Utilities for dealing with weighted point matrices.
"""
import numpy as np


def get_points(weighted_points):
    """Retrieve the points from a weighted points matrix.

    Parameters
    ----------
    weighted_points: numpy array (:obj:`numpy.array`)
        A 4xN matrix of 'N' points with a weight as the first item, and the
        x, y and z coordinates and the second through fourth items.

    Returns
    -------
    points: numpy array (:obj:`numpy.array`)
        A 3xN matrix of 'N' points with the x, y and z coordinates of the 
        points.

    Examples
    --------
    >>> import numpy as np
    >>> weighted_points = np.array([[1.0, 1, 2, 3],
    ...                             [1.0, 4, 5, 6],
    ...                             [1.0, 7, 8, 9],
    ...                             [1.0, 10, 11, 12]])
    >>> get_points(weighted_points)
    array([[  1.,   2.,   3.],
           [  4.,   5.,   6.],
           [  7.,   8.,   9.],
           [ 10.,  11.,  12.]])
    """
    return weighted_points[:, 1:4]


def get_weights(weighted_points):
    """Retrieve the weights from a weighted points matrix.

    Parameters
    ----------
    weighted_points: numpy array (:obj:`numpy.array`)
        A 4xN matrix of 'N' points with a weight as the first item, and the
        x, y and z coordinates and the second through fourth items.

    Returns
    -------
    weights: numpy array (:obj:`numpy.array`)
        A Nx1 matrix of 'N' points with the weights of each point.

    Examples
    --------
    >>> import numpy as np
    >>> weighted_points = np.array([[1.0, 1, 2, 3],
    ...                             [1.0, 4, 5, 6],
    ...                             [1.0, 7, 8, 9],
    ...                             [1.0, 10, 11, 12]])
    >>> get_weights(weighted_points)
    array([ 1.,  1.,  1.,  1.])
    """
    return weighted_points[:, 0:1].T[0]


def exclude_points(weighted_points, rows):
    """Remove the given rows from the weighted points.

    Parameters
    ----------
    weighted_points: numpy array (:obj:`numpy.array`)
        A 4xN matrix of 'N' points with a weight as the first item, and the
        x, y and z coordinates and the second through fourth items.
    rows: list or set
        A list or set of row numbers (starting from 0) to remove.

    Returns
    -------
    weighted_points: numpy array (:obj:`numpy.array`)
        A 4xM matrix of 'M' points with the rows removed such that M <= N.

    Examples
    --------
    >>> import numpy as np
    >>> weighted_points = np.array([[1.0, 1, 2, 3],
    ...                             [1.0, 4, 5, 6],
    ...                             [1.0, 7, 8, 9],
    ...                             [1.0, 10, 11, 12]])
    >>> exclude_points(weighted_points, rows=[0, 2])  # delete first & third rows
    array([[  1.,   4.,   5.,   6.],
           [  1.,  10.,  11.,  12.]])
    """
    rows = set(rows)  # Isolate the unique row numbers
    rows = sorted(rows)  # sort the row number indices
    return np.delete(weighted_points, rows, 0)


def reweigh_points(weighted_points, rows, weight):
    """Reweigh the given rows of the weighted_points.
    
    Parameters
    ----------
    weighted_points: numpy array (:obj:`numpy.array`)
        A 4xN matrix of 'N' points with a weight as the first item, and the
        x, y and z coordinates and the second through fourth items.
    rows: list or set
        A list or set of row numbers (starting from 0) to reweigh.
    weight: float
        The new weight.
    
    Returns
    -------
    weighted_points: numpy array (:obj:`numpy.array`)
        A copy 4xN matrix of 'N' points with the specified rows reweighed.
    
    Examples
    --------
    >>> import numpy as np
    >>> weighted_points = np.array([[1.0, 1, 2, 3],
    ...                             [1.0, 4, 5, 6],
    ...                             [1.0, 7, 8, 9],
    ...                             [1.0, 10, 11, 12]])
    >>> reweigh_points(weighted_points, rows=[0, 2], weight=2.0)
    array([[  2.,   1.,   2.,   3.],
           [  1.,   4.,   5.,   6.],
           [  2.,   7.,   8.,   9.],
           [  1.,  10.,  11.,  12.]])
    """
    copy = np.copy(weighted_points)

    # Reset the weights
    for row in rows:
        copy[row][0] = weight
    return copy
