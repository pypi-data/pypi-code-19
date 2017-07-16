#!/Anaconda3/python
# storytime

'''
Functions that map Surface -> Surface
'''



from ..meta import prepare_object



#----------------------------------------------------------------------#
from .surfaces import Surface

class Transformer:
    """
    Abstract base class - implement callbacks for performing a suite of transformations on a surface
    """

    def __init__( self, parameters=None ) :
        self.parameters = prepare_object(parameters, dict)

    def create( self, surface: Surface, seed ) -> Surface:
        raise NotImplementedError

    def dilate( self, surface, new_extent, seed ) -> Surface:
        raise NotImplementedError

    def translate(self, surface, vector, seed) -> Surface:
        raise NotImplementedError

    def rotate( self, surface, arcvector, seed ) -> Surface :
        raise NotImplementedError

    def update( self, old_surface, new_surface, seed ) -> Surface :
        raise NotImplementedError

#----------------------------------------------------------------------#
from .surfaces import SurfaceSphere2
from .surfaces import SurfacePlane

class Globe_TectonicPlates( Transformer ):

    def create( self, surface: SurfaceSphere2, seed ) -> SurfaceSphere2:
        """construct continental edges"""
        pass

    def dilate( self, surface: SurfaceSphere2, new_radius, seed ) -> SurfaceSphere2:
        """Continents stay together"""
        pass

    def translate( self, surface, vector, seed ) -> SurfaceSphere2 :
        raise NotImplementedError

    def rotate( self, surface, arcvector, seed ) -> SurfaceSphere2 :
        raise NotImplementedError

    def update( self, old_surface, new_surface, seed ) -> Surface :
        raise NotImplementedError


#----------------------------------------------------------------------#

def waterman( globe: SurfaceSphere2 ) -> SurfacePlane :
    plane = SurfacePlane( )
    return plane

#----------------------------------------------------------------------#
