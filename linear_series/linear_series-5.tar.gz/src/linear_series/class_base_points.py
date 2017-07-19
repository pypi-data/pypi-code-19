'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Aug 4, 2016
@author: Niels Lubbes

This file declares 2 classes: "BasePointTree" and "BasePoint".
'''

class BasePointTree():
    '''
    This class represents a tree of base points of a linear series of 
    curves.
    '''

    # If True than the string representation of this object is short.
    short = True

    def __init__( self, chart_lst = ['z', 'x', 'y'] ):
        '''
        Constructor.
        '''

        # Linear series whose base points
        # are represented by this object.
        #
        self.ls = None

        # A list of charts where a chart is denoted by a String.
        # See documentation of "get_base_point_tree.in_previous_chart()"
        # for specification of chart strings.
        #
        self.chart_lst = chart_lst

        # Dictionary where a key is a chart
        # and a value is a list of BasePoint objects.
        # "self.chart_lst" is an ordered list of keys of this
        # dictionary.
        #
        self.chart_tree_dct = {}


    def add( self, chart, sol, mult ):
        '''
        INPUT:
            - "self"  -- BasePointTree object.
            - "chart" -- A String denoting a chart.
            - "sol"   -- A 2-tuple of elements in "PolyRing.num_field" 
                         representing a base point in a chart.     
            - "mult"  -- An integer representing the multiplicity of the base point.        
        OUTPUT:
            - Adds a base point to "self[chart]"
            - Return the added base point.
        '''

        bp = BasePoint( 0, chart, None )
        bp.sol = sol
        bp.mult = mult
        self[chart] += [bp]

        return bp


    # operator overloading for []
    def __getitem__( self, chart ):
        if chart not in self.chart_lst:
            raise ValueError( 'The chart key should be an element in:', self.chart_lst )

        if chart not in self.chart_tree_dct:
            self.chart_tree_dct[chart] = []

        return self.chart_tree_dct[chart]


    # operator overloading for []
    def __setitem__( self, chart, item ):
        if chart not in self.chart_lst:
            raise ValueError( 'The chart key should be an element in:', self.chart_lst )

        self.chart_tree_dct[chart] = item


    # overloads str(): human readable string representation of object
    def __str__( self ):
        '''                
        OUTPUT:
          - Human readable string representation of object. 
            The String consists of lines with the following format
                
                chart=[C], depth=[Integer], mult=[Integer], sol=[P], [LinearSeries]
 
            where 
                * C = An element of "self.chart_lst".
                * P = A 2-tuple: ( [PolyRing.num_field], [PolyRing.num_field] )
            and where 
                * sol  : A point P in the zeroset of the linear series.
                * chart: The current chart of the the point P.
                * mult : The multiplicity of P as a root.
                * depth: The depth when considering P as an infinitely near point
                         in a tree structure.
                * For each blowup chart we also depict the corresponding [LinearSeries]. 
            
            Note that the lines represent a tree structure.                     
            Below we see an example.
                
        EXAMPLE:
          - sage: ls = LinearSeries( ['x^2+y^2', 'x*z+y^2'], PolyRing( 'x,y,z', True ) )
            sage: print( ls.get_bp_tree() )  
            out :            
                { 2, <<x^2 + y^2, y^2 + x*z>>, QQ( <a0|t^2 + 1> )[x, y, z] }
                chart=z, depth=0, mult=1, sol=(0, 0), { 2, <<x^2 + y^2, y^2 + x>>, QQ( <a0|t^2 + 1> )[x, y] }
                    chart=t, depth=1, mult=1, sol=(0, 0), { 2, <<x^2*y + y, x + y>>, QQ( <a0|t^2 + 1> )[x, y] }
                chart=z, depth=0, mult=1, sol=(1, (-a0)), { 2, <<x^2 + y^2, y^2 + x>>, QQ( <a0|t^2 + 1> )[x, y] }
                chart=z, depth=0, mult=1, sol=(1, (a0)), { 2, <<x^2 + y^2, y^2 + x>>, QQ( <a0|t^2 + 1> )[x, y] }                                                      
        '''

        tree_str = ''
        if self.ls != None:
            tree_str += '\n' + str( self.ls )
        for chart in self.chart_lst:
            for bp in self[chart]:
                tree_str += str( bp )
        return tree_str.replace( '\n', '\n\t' )


    def alt_str( self ):
        ''' 
        This method can be useful for testing.
        
        OUTPUT:
          - A string representation without the linear series. 
        '''
        tree_str = ''
        for chart in self.chart_lst:
            for bp in self[chart]:
                tree_str += bp.alt_str()
        return tree_str.replace( '\n', '\n\t' )


class BasePoint():
    '''
    This class represents a binary tree of base points.
    If a base point has an infinitely near base point then 
    its 2 leaves represent two charts 's' and 't' of the blowup at these 
    base points.
    '''

    def __init__( self , depth, chart, ls ):
        '''
        Constructor.
        '''

        # Depth of base point tree.
        #
        self.depth = int( depth )

        # Chart denoted by a string.
        # See docs of "get_base_point_tree.in_previous_chart()"
        #
        self.chart = chart

        # LinearSeries
        #
        self.ls = ls

        # Base point represented as a 2-tuple of
        # elements in a number field.
        #
        self.sol = None

        # Multiplicity of a solution
        # (0=no solution, -1=overlapping chart)
        #
        self.mult = 0

        # lists of base points
        #
        self.bp_lst_t = []
        self.bp_lst_s = []


    def add( self, chart_st, sol, mult ):
        '''
        INPUT:
            - "self"     --
            - "chart_st" -- 's' or 't'
            - "sol"      -- A 2-tuple of elements in "PolyRing.num_field" 
                            representing an infinitely near base point in a blowup chart. 
            - "mult"     -- An integer representing the multiplicity of the base point. 
        OUTPUT:
            - Adds a base point to either "self.bp_lst_s" or "self.bp_lst_t".
            - Return the added infinitely near base point.
        '''

        if chart_st not in ['s', 't']:
            raise ValueError( 'Expecting "chart_st" to be either "s" or "t":', chart_st )

        bp = BasePoint( self.depth + 1, chart_st, None )
        bp.sol = sol
        bp.mult = mult

        dct = {'s':self.bp_lst_s, 't':self.bp_lst_t}
        dct[chart_st] += [bp]

        return bp

    def __str__( self ):
        '''
        OUTPUT:
          - Human readable string representation of object.
            See "BasePointTree.__str__()".
        '''

        if BasePointTree.short == True and self.mult in [0, -1]:
            return ''

        bp_str = ''
        bp_str += '\n' + 4 * self.depth * ' ' + 'chart=' + self.chart + ', '
        if self.mult == -1:
            bp_str += '(overlapping chart)' + ', '
        if self.mult == 0:
            bp_str += '(no solution)' + ', '
        bp_str += 'depth=' + str( self.depth ) + ', '
        bp_str += 'mult=' + str( self.mult ) + ', '
        bp_str += 'sol=' + str( self.sol ) + ', '
        bp_str += str( self.ls )

        for bp in self.bp_lst_t:
            bp_str += str( bp )

        for bp in self.bp_lst_s:
            bp_str += str( bp )

        return bp_str


    def alt_str( self ):
        ''' 
        This method can be useful for testing.
        
        OUTPUT:
          - A string representation without the linear series. 
        '''

        if self.mult in [0, -1]:
            return ''

        bp_str = ''
        bp_str += '\n' + 4 * self.depth * ' '
        bp_str += 'chart=' + self.chart + ', '
        bp_str += 'depth=' + str( self.depth ) + ', '
        bp_str += 'mult=' + str( self.mult ) + ', '
        bp_str += 'sol=' + str( self.sol ) + ', '

        for bp in self.bp_lst_t:
            bp_str += bp.alt_str()

        for bp in self.bp_lst_s:
            bp_str += bp.alt_str()

        return bp_str

