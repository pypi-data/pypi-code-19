#!/Anaconda3/python
# storytime

"""
description
"""

import numpy as np

from scipy.spatial.distance import pdist
from scipy.spatial import Voronoi
from scipy.spatial import SphericalVoronoi


from ..meta import equality_of
from ..meta import prepare_ndarray
from ..meta import prepare_object
from ..meta import Cache

#----------------------------------------------------------------------#
# Continuous spatial data


#----------------------------------------------------------------------#

class Coord :
    """interface for spatial coordinates"""

    voronoi_class = NotImplemented

    @classmethod
    def metric( cls, source, destination ) :
        """All points exist in the same place"""
        return 0


    def __init__( self,
                  vector=None,
                  shape: int = 2,
                  index=None
                  ) :

        self.index = index
        self.vector = prepare_ndarray( vector, dim=shape )
        # ToDo: validate components of vector as floats
        (self.shape,) = self.vector.shape


    def __sub__( self, other ) :
        return self.metric( self, other )


#---------------------------------------------------------------------#

def metric_euclidean( coordinates_array ) :
    return pdist( coordinates_array )

class CoordR( Coord ) :
    """rectangular coordinate"""

    voronoi_class = Voronoi

    @classmethod
    def metric( cls, source, destination ) :
        """euclidean"""
        positions = np.array( [source.vector, destination.vector] )
        mindist = np.min( pdist( positions ) )
        return mindist


    def __str__( self ) :
        return "<r" + str( self.shape ) + " " + str( self.vector ) + ">"

    def to_spherical(self, origin):
        coord = None

        return coord


#---------------------------------------------------------------------#
from .units import degrees_to_radians

def metric_sphere2( coordinates_array, radius=1, units=degrees_to_radians ) :
    """
    2 dimensions only
    Compute a distance matrix of the coordinates using a spherical metric.
    source: http://codereview.stackexchange.com/questions/98275/compute-spherical-distance-matrix-from-list-of-geographical-coordinates
    :param coordinates_array: np.ndarray with shape (n,2); latitude is in 1st col, longitude in 2nd.
    :param radius: convert arclength to distance units
    :param units: function that converts array of (phi,theta)->(radians,radians)
    :returns distance_mat: np.ndarray with shape (n, n) containing distance in km between coords.
    """

    print( coordinates_array )

    # Unpacking coordinates
    latitudes = coordinates_array[:, 0]
    longitudes = coordinates_array[:, 1]
    n_pts = coordinates_array.shape[0]

    #convert coordinates to radians.
    (phi_values, theta_values) = units( latitudes, longitudes )

    # Expand phi_values and theta_values into grids
    theta_1, theta_2 = np.meshgrid( theta_values, theta_values )
    theta_diff_mat = theta_1 - theta_2

    phi_1, phi_2 = np.meshgrid( phi_values, phi_values )

    # Compute spherical distance from spherical coordinates
    angle = (np.sin( phi_1 ) * np.sin( phi_2 ) * np.cos( theta_diff_mat ) +
             np.cos( phi_1 ) * np.cos( phi_2 ))
    arc = np.arccos( angle )

    # Multiply by earth's radius to obtain distance in km
    return arc * radius

#####################

class CoordS2( Coord ) :
    """spherical coordinate with radius and recursive center"""

    voronoi_class = SphericalVoronoi

    @classmethod
    def metric( cls, source, destination ) :
        assert source.radius == destination.radius
        coordinates_dict = { 'SOURCE' : source.vector
                           , 'DESTINATION' : destination.vector
                           }
        coordinates_array = np.array( [(val[0], val[1]) for key, val in coordinates_dict.items( )] )
        return metric_sphere2( coordinates_array, source.radius )


    def __init__( self,
                  vector=None,
                  radius: float = 1,
                  center=None,
                  shape: int = 2,
                  index=None
                  ) :

        super( ).__init__( vector, shape, index )
        self.radius     = radius
        self.center_id  = None
        self.center     = None

        if center is None or isinstance( center, Coord ):
            self.center = center
        elif isinstance( center, int ) :
            self.center_id = center
        else :
            raise TypeError( "CoordS2 center must be int, Coord, or None : " + str( vector ) )
        # ToDo: validate edges of the vector as floats


    def __str__( self ) :

        string = "<s"
        string += str( self.shape ) + " "

        string += "[" # print vector
        string += str( self.vector[0] )
        for d in range( 1, self.shape ) :
            string += " " + str( self.vector[d] )
        string += "]"

        if self.radius != 1 : # radius
            string += " r=" + str( self.radius )
        if isinstance( self.center, CoordR ) : # print center rectangular
            string += "| " + str( self.center )
        elif isinstance( self.center, CoordS2 ) : # print center spherical
            string += "| [S" + str( self.center.shape ) + " " + str( self.center.index ) + "]"
        elif self.center_id is not None : # print center index
            string += "| " + str( self.center_id )

        string += ">"
        return string


    def to_rectangular(self):
        x = self.radius * np.sin( self.vector[0] ) * np.cos( self.vector[1] )
        y = self.radius * np.sin( self.vector[0] ) * np.sin( self.vector[1] )
        z = self.radius * np.cos( self.vector[0] )
        coord = CoordR([x,y,z])
        return coord


#---------------------------------------------------------------------#

#---------------------------------------------------------------------#
class TilePolygon:
    """Provide geometric information relevant to rendering and UI."""

    def __init__(self, position, vertices):
        self.position = position
        self.vertices = []


    def intesects(self, line) -> bool:
        """
        A line intersects a polygon if it intesects any of its sides
        a side is a linear function with a domain of [x1,x2]
        """

        if len(self.vertices) > 0:
            return False
        return NotImplemented

    def contains( self, point ) -> bool :
        """
        hypothesis: a convex polygon contains a point if
        any line containing the point intersects the polygon in both directions.
        On a sphere, need to constrain the line to arclength < pi
        """

        if len( self.vertices ) > 0 :
            return False
        return NotImplemented

    def area(self) -> float :
        """
        Calculate the area of the polygon
        General Case: area of triangles
        Voronoi case: http://www.personal.kent.edu/~rmuhamma/Compgeometry/MyCG/CG-Applets/VoroArea/voroarcli.htm
        """

        if len( self.vertices ) > 0 :
            return 0
        return NotImplemented


#---------------------------------------------------------------------#
class Surface:
    """Sparse surface equiped with voronoi tiling"""

    def __init__(self
                ,extent = None
                ,points:list = None
                ,voronoi_class = Coord.voronoi_class
                ):

        self._extent = extent
        self._sites = prepare_object( points, list )


        self._voronoi_class = voronoi_class
        self._voronoi       = None
        self._cell_vertices = None
        self._cell_areas    = Cache()
        self._calculate_voronoi()



        self._distance_matrix = Cache()
        self._adjacency_matrix = Cache()

    def __str__( self ) :
        string = "<S "
        string += "[" + str( self._extent ) + "]"
        string += ": " + str( len( self._sites ) )
        string += ">"
        return string

    @property
    def __dprint__(self):
        string = str(self)
        for point in self._sites:
            string += "\n" + str(point)
        return string


    #####################
    def site_add( self, *points ) :
        for point in points:
            if hasattr(point, 'index'):
                point.index = len( self._sites )
            self._sites.append( point )
        self._calculate_voronoi()

    def site_containing( self, point ):
        closest_site = self._sites.pop(0)
        closest_distance = point - closest_site
        for site in self._sites:
            distance = site - closest_site
            if distance == closest_distance:
                raise ValueError("Non-unique solution. Point is equidistant between two regions")
                # ToDo: return both sites
            if  distance < closest_distance:
                closest_distance = distance
                closest_site = site
        return closest_site

    def _calculate_voronoi( self ) :
        if self._voronoi_class is None :
            raise RuntimeError( "Unable to calculate voronoi regions without specifying voronoi_class:", self )

        elif len( self._sites ) == 0 :
            self._voronoi = None

        else :
            self._voronoi = self._voronoi_class( self._sites )

    def site_area(self, site_index):
        site = self._sites[site_index]
        # cell area is the sum of the areas of all ridge vertex triangles
        return NotImplemented

    def _cell_add( self, site_index ) :
        cell = self
        return NotImplemented

    def tiles( self ) :
        tiles = self
        yield NotImplemented

    def sites_array(self):
        return []



    #####################
    def distance_matrix(self):
        raise NotImplementedError



#---------------------------------------------------------------------#
class SurfacePlane( Surface ) :
    """Sparse grid equiped with a network of voronoi regions"""

    def __init__( self
                , size_x: int = 0
                , size_y: int = 0
                , sites: list = None
                ):
        super( ).__init__( (size_x, size_y)
                         , sites
                         , voronoi_class=CoordR.voronoi_class
                         )

    def __str__( self ) :
        string = "<Sp "
        string += str(list(self._extent))
        string += ": " + str( len( self._sites ) )
        string += ">"
        return string


    @property
    def size_x( self ) :
        return self._extent[0]

    @property
    def size_y( self ) :
        return self._extent[1]

    def sites_array( self ) :
        coord_list = None
        for site in self._sites :
            pass

    def distance_matrix( self ) :
        return NotImplemented


#---------------------------------------------------------------------#
class SurfaceSphere2( Surface ) :
    """Voronoi-equiped sparse spherical grid"""

    def __init__( self
                , radius:int=0
                , sites:list = None
                ):
        super().__init__( radius
                        , sites
                        , voronoi_class=CoordS2.voronoi_class
                        )

    def __str__( self ) :
        string = "<Ss "
        string += "[r = " + str( self._extent ) + "]"
        string += ": " + str( len( self._sites ) )
        string += ">"
        return string


    @property
    def radius(self):
        return self._extent

    def sites_array( self ) :
        coord_list = None
        for site in self._sites :
            coord = site.to_rectangular()


        return np.array(coord_list)

    def distance_matrix( self ) :
        return NotImplemented


#----------------------------------------------------------------------#
