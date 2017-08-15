"""
Functions to render volumes for molecular viewers.
"""
from .weighted_points import get_points

_grid_header = """
Grid 
80 64     tiles in x,y
 8  8     pixels (x,y) per tile
4         anti-aliasing 3x3 into 2x2 pixels
0 0 0     black background
F         no, ribbons cast funny shadows
25        Phong power
0.15      secondary light contribution
0.05      ambient light contribution
0.25      specular reflection component
4.0       eye position
1 1 1     main light source position
1 0 0 0   input co-ordinate + radius transformation
0 1 0 0
0 0 1 0
"""


def write_r3d_grid(filename, weighted_points):
    """Render a grid using spheres in the r3d format.
    
    Parameters
    ----------
    weighted_points

    Returns
    -------
    """
    # Initialize parameters
    points = get_points(weighted_points)
    global _grid_header

    contents = _grid_header

    contents += '\n'.join('2\n{:.3f} {:.3f} {:.3f} '
                          '0.2 1.0 0.0 0.0'.format(p[0], p[1], p[2])
                          for p in points)
    contents += '\n0'

    with open(filename, 'w') as f:
        f.write(contents)


def write_r3d_prolate(center, theta, phi, long, short):
    """
    
    Parameters
    ----------
    center
    theta
    phi
    long
    short

    Returns
    -------

    """