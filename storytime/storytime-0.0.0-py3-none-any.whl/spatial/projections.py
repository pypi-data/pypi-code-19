#!/Anaconda3/python
# storytime

'''
Functions that map Surface -> Surface
'''


from .surfaces import Surface
from .surfaces import SurfaceSphere2
from .surfaces import SurfacePlane


#----------------------------------------------------------------------#

def waterman( globe: SurfaceSphere2 ) -> SurfacePlane :
    plane = SurfacePlane( )
    return plane


#----------------------------------------------------------------------#

class Projection:
    """abstract polymorphic function for mapping different surface types"""

    @classmethod
    def __call__( cls, surface:Surface ) -> Surface:
        """Check type and dispatch to appropriate method"""

        if issubclass( type(surface), SurfaceSphere2 ):
            return cls.sphere_to_plane( surface )

        elif issubclass( type( surface ), SurfacePlane ):
            return cls.plane_to_sphere( surface )

        else:
            raise NotImplementedError( type(surface) )


    @classmethod
    def sphere_to_plane(cls, surface) -> SurfacePlane :
        raise NotImplementedError

    @classmethod
    def plane_to_sphere( cls, surface ) -> SurfaceSphere2 :
        raise NotImplementedError


#----------------------------------------------------------------------#

class GallPeters( Projection ):
    @classmethod
    def sphere_to_plane( cls, surface ) -> SurfacePlane :
        return SurfacePlane()

    @classmethod
    def plane_to_sphere( cls, surface ) -> SurfaceSphere2 :
        return SurfaceSphere2

#----------------------------------------------------------------------#
