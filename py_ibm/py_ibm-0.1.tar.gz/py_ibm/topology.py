import numpy as np
from math import floor,atan2,degrees,sin,cos,radians, isnan
from operator import methodcaller

class Rectangular_Grid(object):
    """ Provides a rectangular topology based on square cells.

        The grid can be 3-dimensional and store different layers of data in the z axis.

    Args:
        x_max (int): number of cells on horizontal axis.
        y_max (int): number of cells on vertical axis.
        ndim (int): number of dimensions
        dim_names (list): list os strings. Each element must be the name for one dimension.


    Attributes:
        x_max (int): number of cells on horizontal axis.
        y_max (int): number of cells on vertical axis.
        ndim (int): number of dimensions
        dim_names (list): list os strings. Each element must be the name for one dimension.
        surface (nparray): a x_max by y_max by ndim array to keep data for the different dimensions.

    """

    def __init__(self,x_max,y_max,ndim=1,dim_names=None):
        self.surface=np.zeros((ndim,x_max, y_max))
        self.x_max=x_max
        self.y_max=y_max
        self.dim_names={}
        for i in range(0,ndim): self.dim_names[dim_names[i]]=i


    def load_surface(self,surface,dim_names):
        """ Load the surface from a nparray.

            This could have been read from a file or passed by another program.

        Args:
            surface (nparray): nparray with values to be loaded as layers in the surface. Minimum of 2 dimensions required, in which case only one layer of information is represented. The x and y dimensions of the grid will be determined by the x and y length of this argument.
            dim_names (list): a list of names for the layers in the 3d dimesnion of the surface argument. If 'surface' is a 2d array, this argument will be ignored.

        Returns:
            None.

        """
        self.surface=surface
        if len(surface.shape)>=3:
            ndim=surface.shape[0]
            self.x_max=surface.shape[1]
            self.y_max=surface.shape[2]
            self.dim_names={}
            for i in range(0,ndim): self.dim_names[dim_names[i]]=i

        else:
            self.x_max=surface.shape[0]
            self.y_max=surface.shape[1]


    def value(self,dim,cell):
        """Verify the value in the 'dim' layer (dimension) of information in the grid's surface for the 'cell'.

        Args:
            dim (str): name of dimension.
            cell (tuple): (x,y), patch coordinates.

        Returns:
            (float): the value of 'cell' in 'dim'


        """
        return self.surface[self.dim_names[dim]][cell]

    def change_value(self,dim,cell,new_value):
        """ Change the value of 'cell' in the 'dim' layer (dimension) of information in the grid's surface.

        Args:
            dim (str): name of dimension.
            cell (tuple): (x,y), patch coordinates.
            new_value (float): new value for cell.

        Returns:
            None.


        """
        self.surface[self.dim_names[dim]][cell]=new_value


    def hood(self,cell,radius=1,remove_center=True):
        """ Return the cells that comprise the neighborhood of 'cell'.

            Note: with radius=1 and remove_center=False, the result is the Moore neighborhood of 'cell' (i.e. 'cell' itself and the 8 adjacent cells). With radius=>2, the result is an extended Moore neighborhood with the numer of cells=(2*radius+1)^2 (subtract 1 if remove_center=True)

        Args:
            cell (tuple): (x,y), patch coordinates of the center cell.
            radius (int): how many grid cells (Tchebychev distance) any cell needs to be from the center to be included in the neighborhood.
            remove_center (bool): If True 'cell' is not included in the final list of cells.

        Returns:
            (list) of tuples with the coordinates '(x,y)' of cells comprising the neighborhood of 'cell'.

        """
        hood=[self.in_bounds((x,y)) for x in range(cell[0]-radius,cell[0]+radius+1) for y in range(cell[1]-radius,cell[1]+radius+1)]
        if remove_center: hood.remove(cell)
        return hood

    def circle(self,center,radius):
        """ Returns the cells that are included within a circle centered in 'center'

        Args:
            center (tupple): (x,y) coordinates of cell in the center of circle.
            radius (float): radius of circle.

        Returns:
            (list) of tuples (x,y) with coodinates of cells included in the circle.
        """

        xmax=center[0]+radius+1
        if xmax>self.x_max: xmax=self.x_max
        ymax=center[1]+radius+1
        if ymax>self.y_max: ymax=self.y_max
        xmin=center[0]-radius-1
        if xmin<0: xmin=0
        ymin=center[1]-radius-1
        if ymin<0: ymin=0



        pixels_in_circle=[(x,y) for x in range(xmin,xmax) for y in range(ymin,ymax) if self.euclid_dist(x0=x,x1=center[0],y0=y,y1=center[1])<radius ]

        return pixels_in_circle



    def angle_cells(self,point0,point1):
        """ Return the angle between the points (x0,y0) and (x1,y1).

            Note: angle is in degrees.

        Args:
            point0 (tuple): (x,y) coodinates of point 0.
            point1 (tuple): (x,y) coodinates of point 1.

        Returns:
            (float): The angle of a straight line from point0 to point1 in relation to the bottom edge of the grid.
        """
        x0,y0=point0
        x1,y1=point1

        deltax=x0-x1
        deltay=y0-y1

        return degrees(atan2(deltay,deltax))



    def agents_within_patches(self,patches,agent_type):
        """Return a list of tuples (agent_id,agent_position) of 'agent_type' within the area.
         """

        pass


    def in_bounds(self,pos):
        """ Adjust point to grid.

            Check if 'pos' is withn the grid boundaries. If so returns 'pos'.
            If not adjust 'pos' to fall within boundaries. This method implements adjustment considering the grid as a Torus (i.e. extremities are adjacent).

            Args:
                pos (tuple): (x,y) coordinates pair.

            Returns:
                (tuple): adjusted (if necessary) (x,y) coordinates pair.
        """
        x,y=pos

        xmax=self.x_max-1
        ymax=self.y_max-1

        if x<0:
            x=xmax-(abs(x)%xmax)
        elif x>xmax:
            x=0+(x%xmax)

        if y<0:
            y=ymax-(abs(y)%ymax)
        elif y>ymax:
            y=0+(y%ymax)

        return (x,y)



    def cell_with_value(self,cells,value,dim):
        """ Check which cells in a list of 'cells' match a 'value' for given 'dim'.

        Args:
            cells (list): list of tuples (x,y).
            value (float): value to be matched.
            dim (str): surface dimension (layer) name.

        Returns:
            [list] of cells (x,y) that match value in the specified dimension.
        """
        return [c for c in cells if self.surface[self.dim_names[dim]][c]==value]


    def euclidean_distance(self,x1,y1,x2,y2):
        """ Calculate the euclidean distance between two points.

        Args:
            x1 (float): x coordinate for point 1.
            y1 (float): y coordinate for point 1.
            x2 (float): x coordinate for point 2.
            y2 (float): y coordinate for point 2.

        Returns:
            (float): euclidean distance.
        """
        return np.sqrt((x1-x2)**2+(y1-y2)**2)

    def scaled_distance(self,x1,y1,x2,y2,scale=20):
        """ Calculate the euclidean distance between two points and scales it.

            Note:Since each cell can represent any distance, this method can be used to calculate the distance in meter, kilometer, etc instead of grid cells.

        Args:
            x1 (float): x coordinate for point 1.
            y1 (float): y coordinate for point 1.
            x2 (float): x coordinate for point 2.
            y2 (float): y coordinate for point 2.
            scale (float): scaling factor.

        Returns:
            (float): euclidean distance multiplied by 'scale'.
        """

        return self.euclidean_distance(x1,y1,x2,y2)*scale


    def point_within_circle(self,x1,y1,r1,x2,y2,
    distance_func,**kwargs):
        """Check if a point is within a circle.

        Args:
            x1 (float): x coordinate for point.
            y1 (float): y coordinate for point.
            r1 (float): radius.
            x2 (float): x coordinate for the center of the circle.
            y2 (float): y coordinate for the center of the circle..

        Returns:
            (bool): True if point is withn circle.
        """
        return distance_func(x1,y1,x2,y2,**kwargs)<r1


    def line_overlap_circle(self,cx,cy,r,x1,y1,x2,y2):
        """ Check if the straight line connecting two point overlaps a circle.

        Args:
            x1 (float): x coordinate for point 1.
            y1 (float): y coordinate for point 1.
            x2 (float): x coordinate for point 2.
            y2 (float): y coordinate for point 2.
            cx (float): x coordinate for the center of the circle.
            cy (float): y coordinate for the center of the circle.
            r (float): radius for circle.

        Returns:
            (bool): True if line and circle overlap.

        """

        return self.pDist(cx,cy,x1,y1,x2,y2)<r

    def circle_overlap_circle(self,x1,y1,r1,x2,y2,r2):
        """ Check if two circles overlap.

        Args:
            x1 (float): x coordinate for center 1.
            y1 (float): y coordinate for center 1.
            x2 (float): x coordinate for center 2.
            x2 (float): y coordinate for center 2.
            r1 (float): radius for circle 1.
            r2 (float): radius for circle 2.

        Returns:
            (bool): True if circles overlap.

        """

        return self.euclidean_distance(x1,x2,y1,y2)<=r1+r2



    def rectangle_overlap_circle(self,cx,cy,r, x1,y1,x2,y2,x3,y3,x4,y4):
        """ Check a rectangle and a circle overlap.

        Args:
            cx (float): x coordinate for circle center.
            cy (float): y coordinate for circle center.
            r1 (float): radius for circle.
            x1 (float): x coordinate for 1st rectangle vertice.
            y1 (float): y coordinate for 1st rectangle vertice.
            x2 (float): x coordinate for 2nd rectangle vertice.
            x2 (float): y coordinate for 2nd rectangle vertice.
            x3 (float): x coordinate for 3rd rectangle vertice.
            y3 (float): y coordinate for 3rd rectangle vertice.
            x4 (float): x coordinate for 4th rectangle vertice.
            x4 (float): y coordinate for 4th rectangle vertice.


        Returns:
            (bool): True if circle and rectangle overlap.

        """

        vertices=[(x1,y1),(x2,y2),(x3,y3),(x4,y4)]
        vertices_within=[self.point_within_circle(cx,cy,r,x,y,distance_func=self.euclidean_distance) for x,y in vertices]

        if any(vertices_within):
            return True

        overlapping_sides=[]
        for v1 in vertices:
            for v2 in vertices:
                if v1!=v2: overlapping_sides.append(self.pDist(cx,cy,v1[0],v1[1],v2[0],v2[1])<r)

        return any(overlapping_sides)




    def pDist(self,px,py,sx1,sy1,sx2,sy2):
        """ Calculate the minimum euclidean distance between a point and a line segment.

        Args:
            px (float): x coordinate for point.
            py (float): y coordinate for point.
            sx1 (float): x coordinate for point 1 in line segment.
            sy1 (float): y coordinate for point 1 in line segment.
            sx2 (float): x coordinate for point 2 in line segment.
            sy2 (float): y coordinate for point 2 in line segment.


        Returns:
            (float): minimum euclidean distance between point and line segment.

        """
        #d=abs((sy2-sy1)*px-(sx2-sx1)*py + sx2*sy1-sy2*sx1)

        #return d/euclidean_distance(sx1,sy1,sx2,sy2)

        A=px-sx1
        B=py-sy1
        C=sx2-sx1
        D=sy2-sy1

        dot=A*C+B*D
        len_sq=C*C+D*D
        param=-1
        if len_sq!=0:
            param=dot/len_sq

        xx=0
        yy=0

        if param<0:
            xx=sx1
            yy=sy1
        elif param>1:
            xx=sx2
            yy=sy2
        else:
            xx=sx1+param*C
            yy=sy1+param*D

        dx=px-xx
        dy=py-yy

        return np.sqrt(dx*dx+dy*dy)
