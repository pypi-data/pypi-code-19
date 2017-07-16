#!/Anaconda3/python
# storytime

"""
description
"""

from copy import deepcopy

from .meta import equality_of
from .meta import prepare_ndarray
from .meta import prepare_object

#----------------------------------------------------------------------#

from .actors import Entity
class Location(Entity) :
    """
    Encapsulates game logic and data related to cells of a zone
    A zone is nested if its locations contain a zone inside them,
    such as a universe containing star systems and planets
    """

    def __init__( self,
                  index: int,
                  # coord: CoordR = None,
                  properties: dict = None,
                  ) :
        assert index is not None
        self.index = index
        self.properties = prepare_object(properties, dict)


#----------------------------------------------------------------------#

from .spatial.surfaces import Surface

class Zone:
    """
    Associate points on a surface with physical location data
    construct a connectedness network between cells
    """

    def __init__( self,
                  surface: Surface = None,
                  cells: list = None
                ):

        self._surface       = prepare_object( surface, Surface )
        self._cells         = prepare_object( cells, list )


    def __str__( self ) :
        string  = "<Zone"
        string += " " + str( type(self._surface).__name__ )
        string += " " + str( len(self._cells) )
        string += ">"
        return string

    @property
    def __dprint__( self ) :
        string = str( self )
        string += "\n " + self._surface.__dprint__
        for cell in self._cells:
            string += "\n " + str(cell)
        return string

    def construct( self ) :
        pass

    def neighbors( self, cell_index, distance=1 ) -> list :
        neighbors = self
        return NotImplemented

    def find_path(self, source:int, destination:int, search_depth=None) -> list:
        path = self
        return NotImplemented





#####################

from .spatial.surfaces import SurfacePlane

class ZoneMap( Zone ):

    def __init__( self,
                  surface: SurfacePlane = None,
                  cells: list = None
                  ) :
        super( ).__init__( surface, cells )


class Layers( Zone ) :
    pass





#####################

from .spatial.surfaces import SurfaceSphere2
from .spatial.projections import waterman
from .spatial.transformations import Transformer

class Planet( Zone ):
    """A planet with oceans and tectonic motion"""

    def __init__( self,
                  radius = None,
                  surface: SurfaceSphere2 = None,
                  cells: list = None,
                  transformer: Transformer = None
                ):
        super().__init__( surface, cells )


    @property
    def radius(self):
        return self._surface._extent

    def __str__( self ) :
        pass


    def construct( self ) :
        pass


#####################

class Orbit(Zone):
    pass


class StarSystem(Orbit):
    pass


class Galaxy(Orbit):
    pass


#----------------------------------------------------------------------#

#----------------------------------------------------------------------#

# ToDo: Perform search operations using SQLLite in :memory:

from .time import GameTurn
from .actors import Population
from .actors import Entity


class Universe :
    """Associate space with its content"""

    def __init__( self,
                  zone: Zone = None,
                  entities:list = None,
                  parameters:dict = None
                ) :

        self._zone          = prepare_object( zone, Zone )
        self._entities      = prepare_object( entities, list )
        self._parameters    = prepare_object( parameters, dict )
        self._created       = False


    #####################
    def create( self, now_time, start_time, physics ) :
        physics.initial_universe(self, now_time, start_time)
        self._created = True


    def tick( self, next_time ) :
        if not self._created:
            raise RuntimeError("Attempt to tick() Universe before create() was called")
        pass


    #####################
    @property
    def entities( self ) :
        for entity in self._entities :
            yield entity

    def find_entity( self, target_entity: Entity ) :
        for entity in self._entities :
            if entity == target_entity :
                return entity
        return None

    def add_entity( self, entity ) :
        self._entities.append( entity )
        # add to structured views


    #####################
    @property
    def __dprint__( self ) :
        string = self._zone.__dprint__
        return string

#----------------------------------------------------------------------#

from .time import GameTime
from collections import OrderedDict

class Spacetime:
    """
    data structure for representing space and time together
    1) state can be viewed either as a slice of space in time,
        or as a slice of time for a space
    """

    def __init__( self,
                  start_time:GameTime,
                  universe: Universe,

                 ):

        self._timeline = OrderedDict()
        self._timeline[start_time] = universe


    @property
    def now(self) -> (GameTime, Universe) :
        return list(self._timeline.items())[-1]

    def universe(self, gametime:GameTime) -> Universe:
        return self._timeline[gametime]

    def entityline( self, entity ) :
        """list of states of the entity over time"""

        line = OrderedDict( )
        for (gametime, universe) in self._timeline.items( ) :
            current_state = universe.find_entity(entity)
            if current_state is not None:
                line[gametime] = current_state
        return line

    def timeline(self):
        """list of gametime keys"""
        return sorted(self._timeline.keys())

    def tick( self, next_time, *args, **kwargs ):
        (gametime, universe) = self.now
        if gametime > next_time :
            raise ValueError("Gametime must be strictly increasing: "
                             + str(gametime) + " > " + str(next_time) )

        new_universe = deepcopy(universe)
        new_universe.tick( gametime )
        self._timeline[next_time] = new_universe


    def distance(self, source, destination):
        distance = self
        return NotImplemented


#----------------------------------------------------------------------#
class PhysicalLaws :
    """callbacks for physical process"""

    #####################
    def initial_universe( self, universe, now_time, start_time ) :
        pass

    def tick_universe( self, universe, now_time, next_time ) :
        pass


    #####################
    def initial_planet( self, planet, now_time, start_time ) :
        pass

    def tick_planet( self, planet, now_time, next_time ) :
        pass


    #####################
    def initial_zonemap( self, zonemap, now_time, start_time, projection_of=None ) :
        pass

    def tick_zonemap( self, zonemap, now_time, next_time ) :
        pass


    #####################
    def initial_entities( self, universe, now_time, start_time ) :
        pass

    def tick_entities( self, universe, now_time, next_time ) :
        pass


#----------------------------------------------------------------------#
