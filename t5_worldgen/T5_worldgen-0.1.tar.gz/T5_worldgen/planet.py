'''planet module'''

import logging
import json

import T5_worldgen.upp as uwp

from T5_worldgen.util import Die, Table, Flux
from T5_worldgen.trade_codes import TradeCodes

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.ERROR)

D6 = Die(6)
D3 = Die(3)
FLUX = Flux()


class Planet(object):
    '''Planet object'''
    starport_table = Table()
    starport_table.add_row((2, 4), 'A')
    starport_table.add_row((5, 6), 'B')
    starport_table.add_row((7, 8), 'C')
    starport_table.add_row((9), 'D')
    starport_table.add_row((10, 11), 'E')
    starport_table.add_row(12, 'X')
    starport_table.dice = 2

    spaceport_table = Table()
    spaceport_table.add_row((0), 'Y')
    spaceport_table.add_row((1, 2), 'H')
    spaceport_table.add_row(3, 'G')
    spaceport_table.add_row((4, 6), 'F')

    mw_type_flux_table = Table()
    mw_type_flux_table.add_row((-5, -4), 'Far Satellite')
    mw_type_flux_table.add_row(-3, 'Close Satellite')
    mw_type_flux_table.add_row((-2, 5), 'Planet')

    parent_type_flux_table = Table()
    parent_type_flux_table.add_row((-5, 0), 'Gas Giant')
    parent_type_flux_table.add_row((1, 5), 'BigWorld')

    def __init__(self, system=None):
        self.starport = '?'
        self.size = uwp.Size()
        self.atmosphere = uwp.Atmosphere()
        self.hydrographics = uwp.Hydrographics()
        self.biosphere = uwp.Biosphere()
        self.population = uwp.Population()
        self.government = uwp.Government()
        self.law_level = uwp.LawLevel()
        self.tech_level = uwp.TechLevel()

        self.trade_codes = []
        self.travel_code = ''
        self.bases = ''
        self.is_mainworld = True
        self.orbit = ''
        self.system = system
        self.mainworld_type = None
        self.parent_type = None
        self.orbit_around_parent = None

        self.determine_starport()
        self.determine_size()
        self.determine_atmosphere()
        self.determine_hydrographics()
        self.determine_population()
        self.determine_government()
        self.determine_law()
        self.determine_tech()
        # self.determine_trade_codes()
        self.determine_mainworld_type()

    def __str__(self):
        return self.uwp()

    def uwp(self):
        '''UPP'''
        return '{}{}{}{}{}{}{}-{}'.format(
            self.starport,
            str(self.size),
            str(self.atmosphere),
            str(self.hydrographics),
            str(self.population),
            str(self.government),
            str(self.law_level),
            str(self.tech_level),
        )

    def display_trade_codes(self):
        '''Display method - UPP + other stuff'''
        return '{}'.format(
            ' '.join(self.trade_codes),
        )

    def determine_starport(self):
        '''Set starport'''
        self.starport = self.starport_table.roll()

    def determine_size(self):
        '''Set size'''
        roll = D6.roll(2, -2)
        if roll >= 10:
            roll = D6.roll(1, 9)
        self.size = uwp.Size(roll)

    def determine_atmosphere(self):
        '''Set atmosphere'''
        roll = FLUX.flux() + int(self.size)
        if roll < 0 or int(self.size) == 0:
            roll = 0
        if roll > 15:
            roll = 15
        self.atmosphere = uwp.Atmosphere(roll)

    def determine_hydrographics(self):
        '''Set hydrographics'''
        mods = 0
        if int(self.atmosphere) < 2 or int(self.atmosphere) > 9:
            mods -= 4
        roll = FLUX.flux() + int(self.atmosphere) + mods
        if int(self.size) < 2:
            roll = 0
        roll = max(0, roll)
        roll = min(10, roll)
        self.hydrographics = uwp.Hydrographics(roll)

    def determine_population(self):
        '''Set population'''
        roll = D6.roll(2, -2)
        if roll == 10:
            roll = D6.roll(2, 3)
        self.population = uwp.Population(roll)

    def determine_government(self):
        '''Set government'''
        roll = FLUX.flux() + int(self.population)
        roll = min(roll, 15)
        roll = max(roll, 0)
        self.government = uwp.Government(roll)

    def determine_law(self):
        '''Set law level'''
        roll = FLUX.flux() + int(self.government)
        roll = min(roll, 18)
        roll = max(roll, 0)
        self.law_level = uwp.LawLevel(roll)

    def determine_tech(self):
        '''Set tech level'''
        mod = 0
        mod += self._mod_starport()
        mod += self._mod_physical()
        mod += self._mod_population()
        LOGGER.debug('determine_tech(): mod = %s', mod)
        roll = D6.roll(1, mod, floor=0)
        LOGGER.debug('TL result = %s', roll)
        self.tech_level = uwp.TechLevel(roll)

    def _mod_starport(self):
        '''TL mods for starport'''
        mod = 0
        if self.starport == 'A':
            mod += 6
        elif self.starport == 'B':
            mod += 4
        elif self.starport == 'C':
            mod += 2
        elif self.starport == 'X':
            mod -= 4
        elif self.starport == 'F':
            mod += 1
        LOGGER.debug('Starport = %s TL DM = %s', str(self.starport), mod)
        return mod

    def _mod_physical(self):
        '''TL mods for physical profile values'''
        mod = 0
        # Size
        if str(self.size) in '01':
            mod += 2
        elif str(self.size) in '234':
            mod += 1
        # Atmosphere
        if str(self.atmosphere) in '0123ABCDEF':
            mod += 1
        # Hydrographics
        if str(self.hydrographics) == '9':
            mod += 1
        elif str(self.hydrographics) == 'A':
            mod += 2
        LOGGER.debug('Physical TL DM = %s', mod)
        return mod

    def _mod_population(self):
        ''' TL mods for population-related profile values'''
        mod = 0
        # Population
        if str(self.population) in '12345':
            mod += 1
        elif str(self.population) == '9':
            mod += 2
        elif str(self.population) in 'ABCDEF':
            mod += 4
        # Government
        if str(self.government) in '05':
            mod += 1
        elif str(self.government) == 'D':
            mod -= 2
        LOGGER.debug('Population TL DM = %s', mod)
        return mod

    def determine_trade_codes(self):
        '''Set trade codes'''
        if self.system is not None:
            tcs = TradeCodes(self, self.system)
        else:
            tcs = TradeCodes(self)
        self.trade_codes = tcs.generate()

    def as_json(self):
        '''Return JSON representation'''
        planet = {
            'uwp': self.uwp(),
            'trade_codes': self.trade_codes,
            'travel_code': self.travel_code,
            'bases': self.bases,
            'is_mainworld': self.is_mainworld,
            'orbit': self.orbit,
            'mainworld_type': self.mainworld_type,
            'parent_type': self.parent_type,
            'orbit_around_parent': self.orbit_around_parent
        }
        return json.dumps(planet)

    def json_import(self, jdata):
        '''Import from JSON'''
        planet = json.loads(jdata)
        self.trade_codes = planet['trade_codes']
        self.travel_code = planet['travel_code']
        self.bases = planet['bases']
        self.is_mainworld = planet['is_mainworld']
        self.orbit = planet['orbit']
        self._load_uwp(planet['uwp'])
        self.mainworld_type = planet['mainworld_type']
        self.parent_type = planet['parent_type']
        self.orbit_around_parent = planet['orbit_around_parent']

    def _load_uwp(self, uwp_data):
        '''Set planetary data from UWP'''
        self.starport = str(uwp_data[0])
        self.size = uwp.Size(str(uwp_data[1]))
        self.atmosphere = uwp.Atmosphere(str(uwp_data[2]))
        self.hydrographics = uwp.Hydrographics(str(uwp_data[3]))
        self.population = uwp.Population(str(uwp_data[4]))
        self.government = uwp.Government(str(uwp_data[5]))
        self.law_level = uwp.LawLevel(str(uwp_data[6]))
        self.tech_level = uwp.TechLevel(str(uwp_data[8]))

    def determine_mainworld_type(self):
        '''Determine if satellite (and type) or planet'''
        close_orbits = ['Ay', 'Bee', 'Cee', 'Dee', 'Ee', 'Eff',
                        'Gee', 'Aitch', 'Eye', 'Jay', 'Kay', 'Ell', 'Em']
        far_orbits = ['En', 'Oh', 'Pee', 'Que', 'Arr', 'Ess',
                      'Tee', 'Yu', 'Vee', 'Dub', 'Ex', 'Wye', 'Zee']
        LOGGER.debug('UWP = %s', self.uwp())
        if int(self.size) == 0:
            # Asteroid belt => planet
            LOGGER.debug('Planet is belt => mainworld_type = Planet')
            self.mainworld_type = 'Planet'
        else:
            flux = FLUX.flux()
            LOGGER.debug('Flux roll is %s', flux)
            self.mainworld_type = self.mw_type_flux_table.lookup(flux)
            LOGGER.debug('Mainworld type is %s', self.mainworld_type)
        if self.mainworld_type == 'Planet':
            self.parent_world = None
            self.orbit_around_parent = None
        elif self.mainworld_type == 'Close Satellite':
            self.trade_codes.append('Lk')
            self.parent_world = self.parent_type_flux_table.lookup(FLUX.flux())
            roll = FLUX.flux()
            if self.parent_world == 'Gas Giant':
                roll -= 2
            roll = max(roll, -6)
            roll = min(roll, 6)
            self.orbit_around_parent = close_orbits[roll + 6]
        elif self.mainworld_type == 'Far Satellite':
            self.trade_codes.append('Sa')
            self.parent_world = self.parent_type_flux_table.lookup(FLUX.flux())
            roll = FLUX.flux()
            if self.parent_world == 'Gas Giant':
                roll -= 2
            roll = max(roll, -6)
            roll = min(roll, 6)
            self.orbit_around_parent = far_orbits[roll + 6]
