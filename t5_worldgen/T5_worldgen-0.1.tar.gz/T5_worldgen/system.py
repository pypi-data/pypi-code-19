'''T5_worldgen system module'''
from __future__ import print_function

import logging
import json
import re
from random import randint, seed
from T5_worldgen.pseudohex import Pseudohex
from T5_worldgen.util import Die, Flux, Table
from T5_worldgen.trade_codes import TradeCodes
from T5_worldgen.planet import Planet
from T5_worldgen.star import Primary

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.ERROR)

D3 = Die(3)
D6 = Die(6)
FLUX = Flux()


class System(object):
    '''Return a T5 basic system with the specified name and location hex'''

    naval_base_presence = Table()
    naval_base_presence.add_row('A', 6)
    naval_base_presence.add_row('B', 5)

    scout_base_presence = Table()
    scout_base_presence.add_row('A', 4)
    scout_base_presence.add_row('B', 5)
    scout_base_presence.add_row('C', 6)
    scout_base_presence.add_row('D', 7)

    mw_orbit_flux_table = Table()
    mw_orbit_flux_table.add_row(-6, -2)
    mw_orbit_flux_table.add_row((-5, -3), -1)
    mw_orbit_flux_table.add_row((-2, 2), 0)
    mw_orbit_flux_table.add_row((3, 5), 1)
    mw_orbit_flux_table.add_row(6, 2)

    def __init__(self, name='', location_hex='0000'):
        self.hex = location_hex
        self.name = name
        self.zone = ''
        self.stellar = Primary()
        self.mainworld = Planet()
        self.determine_mw_orbit()

        self.bases = self.determine_bases()
        self.pbg = Pbg(self.mainworld)
        self.allegiance = 'Na'
        self.determine_trade_codes()
        self.importance_x = ImportanceExtension(
            self.mainworld,
            self)
        self.economic_x = EconomicExtension(
            self.pbg,
            int(self.mainworld.population),
            int(self.mainworld.tech_level),
            self.mainworld.trade_codes,
            int(self.importance_x))
        self.cultural_x = CulturalExtension(
            int(self.mainworld.population),
            int(self.importance_x),
            int(self.mainworld.tech_level))
        self.nobility = self.determine_nobility()
        self.num_worlds = (
            self.pbg.belts +
            self.pbg.gasgiants +
            D6.roll(1) + 1)
        self.determine_travel_zone()

    def display(self):
        '''Display'''
        return '{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}'.format(
            self.hex,
            self.name,
            self.mainworld.uwp(),
            ' '.join(self.mainworld.trade_codes),
            str(self.importance_x),
            str(self.economic_x),
            str(self.cultural_x),
            self.nobility,
            self.bases,
            self.zone,
            str(self.pbg),
            self.num_worlds,
            self.allegiance,
            self.stellar.display()
        )

    def __str__(self):
        oformat = '{0:4} {1:20} {2:9} {3:18} {4:4} {5:7} {6:6} ' +\
            '{7:7} {8:2} {9:1} {10:3} {11:2} {12:2} {13:14}'
        return oformat.format(
            self.hex,
            self.name,
            self.mainworld.uwp(),
            ' '.join(self.mainworld.trade_codes),
            str(self.importance_x),
            str(self.economic_x),
            str(self.cultural_x.display()),
            self.nobility,
            self.bases,
            self.zone,
            str(self.pbg),
            self.num_worlds,
            self.allegiance,
            self.stellar)

    def determine_nobility(self):
        '''Determine noble representation'''
        nobility = 'B'  # Every world gets a knight
        # Baronet
        if (
                'Pa' in self.mainworld.trade_codes or
                'Pr' in self.mainworld.trade_codes):
            nobility += 'c'
        # Baron
        if (
                'Ag' in self.mainworld.trade_codes or
                'Ri' in self.mainworld.trade_codes):
            nobility += 'C'
        if 'Pi' in self.mainworld.trade_codes:
            nobility += 'D'     # Marquis
        if 'Ph' in self.mainworld.trade_codes:
            nobility += 'e'     # Viscount
        # Count
        if (
                'In' in self.mainworld.trade_codes or
                'Hi' in self.mainworld.trade_codes):
            nobility += 'E'
        if int(self.importance_x) >= 4:
            nobility += 'f'     # Duke
        return nobility

    def determine_bases(self):
        '''Determine bases'''
        bases = ''
        # Naval base
        target = self.naval_base_presence.lookup(self.mainworld.starport)
        if target is not None:
            if D6.roll(2) <= target:
                bases += 'N'
        # Scout base
        target = self.scout_base_presence.lookup(self.mainworld.starport)
        if target is not None:
            if D6.roll(2) <= target:
                bases += 'S'
        return bases

    def determine_trade_codes(self):
        '''Determine climate trade codes'''
        tcs = TradeCodes(self.mainworld, self)
        self.mainworld.trade_codes = tcs.generate()

    def determine_mw_orbit(self):
        '''Determine mainworld orbit'''
        orbit = self.stellar.habitable_zone +\
            self.mw_orbit_flux_table.lookup(FLUX.flux())
        orbit = max(orbit, 0)
        self.mainworld.orbit = orbit

    def determine_travel_zone(self, starport_x_is_red=True):
        '''Determine travel zone - A or R'''
        self.zone = ''
        if int(self.mainworld.government) + int(self.mainworld.law_level) in [20, 21]:
            self.zone = 'A'
            self.mainworld.trade_codes.append('Da')
        elif int(self.mainworld.government) + int(self.mainworld.law_level) > 22:
            self.zone = 'R'
        if  starport_x_is_red:
            if self.mainworld.starport == 'X':
                self.zone = 'R'
                self.mainworld.trade_codes.append('Fo')

    def as_json(self):
        '''Return JSON representation of system'''
        system_dict = {
            'name': self.name,
            'hex': self.hex,
            'stellar': self.stellar.as_json(),
            'mainworld': self.mainworld.as_json(),
            'bases': self.bases,
            'pbg': str(self.pbg),
            'allegiance': self.allegiance,
            'Ix': str(self.importance_x),
            'Ex': str(self.economic_x),
            'Cx': str(self.cultural_x),
            'nobility': self.nobility,
            'worlds': self.num_worlds,
            'zone': self.zone
        }
        return json.dumps(system_dict)

    def json_import(self, jdata):
        '''Import from JSON'''
        system_dict = json.loads(jdata)
        self.name = system_dict['name']
        self.hex = system_dict['hex']
        self.bases = system_dict['bases']
        self.allegiance = system_dict['allegiance']
        self.nobility = system_dict['nobility']
        self.num_worlds = int(system_dict['worlds'])
        self.zone = system_dict['zone']
        self.stellar.json_import(system_dict['stellar'])
        self.mainworld.json_import(system_dict['mainworld'])
        self.pbg.json_import(system_dict['pbg'])
        self.importance_x.json_import(system_dict['Ix'])
        self.economic_x.json_import(system_dict['Ex'])
        self.cultural_x.json_import(system_dict['Cx'])


class Pbg(object):
    '''PBG storage'''
    def __init__(self, population=0):
        self.pop = self._determine_pop_digit(population)
        self.belts = self._determine_belts()
        self.gasgiants = self._determine_gas_giants()

    def __str__(self):
        return '{}{}{}'.format(
            self.pop,
            self.belts,
            self.gasgiants)

    def json_import(self, jdata):
        '''Import from JSON'''
        try:
            self.pop = int(jdata[0])
            self.belts = int(jdata[1])
            self.gasgiants = int(jdata[2])
        except ValueError:
            raise

    @staticmethod
    def _determine_pop_digit(population):
        '''Determine population digit'''
        if population == 0:
            return 0
        else:
            seed()
            return randint(1, 9)

    @staticmethod
    def _determine_belts():
        '''Determine number of belts'''
        return D3.roll(1, -3, floor=0)

    @staticmethod
    def _determine_gas_giants():
        '''Determne number of gas giants'''
        return max(int(D6.roll(2) / 2) - 2, 0)


class ImportanceExtension(object):
    '''Importance extension'''
    def __init__(self, planet, system):
        self.value = 0
        # Starport
        if planet.starport in 'AB':
            self.value += 1
        elif planet.starport in 'DEX':
            self.value -= 1
        # Tech level
        if int(planet.tech_level) >= 16:
            self.value += 1
        if int(planet.tech_level) >= 10:
            self.value += 1
        if int(planet.tech_level) <= 8:
            self.value -= 1
        # Trade codes, population
        if int(planet.population) <= 6:
            self.value -= 1
        for code in ['Ag', 'Hi', 'In', 'Ri']:
            if code in planet.trade_codes:
                self.value += 1
        # Bases
        if 'N' in system.bases and 'S' in system.bases:
            self.value += 1
        if 'W' in system.bases:
            self.value += 1

    def display(self):
        '''Display Ix'''
        return '{' + '{0:+X}'.format(self.value) + '}'

    def __str__(self):
        return self.display()

    def __int__(self):
        return self.value

    def json_import(self, jdata):
        '''Import from JSON'''
        try:
            self.value = int(re.match(r'{(.+)}', jdata).group(1))
        except AttributeError:
            raise


class EconomicExtension(object):
    '''Economic extension data'''
    def __init__(
            self,
            pbg,
            population=0,
            tech_level=0,
            trade_codes=None,
            importance_x=0
    ):
        LOGGER.debug('args to EconomicExtension')
        LOGGER.debug(
            'pbg = %s pop = %s tl = %s Ix = %s',
            str(pbg), population, tech_level, importance_x)
        if trade_codes is None:
            trade_codes = []
        LOGGER.debug('trade codes = %s', ' '.join(trade_codes))
        self.resources = Pseudohex(self._calculate_resources(
            tech_level, pbg))
        self.labor = Pseudohex(max(population - 1, 0))
        self.infrastructure = Pseudohex(self._calculate_infrastructure(
            importance_x, trade_codes))
        self.efficiency = FLUX.flux()
        self.resource_units = self.calculate_ru()

    @staticmethod
    def _calculate_resources(tech_level, pbg):
        '''Resources stuff'''
        resources = D6.roll(2)
        if tech_level >= 8:
            resources += pbg.gasgiants
            resources += pbg.belts
        resources = max(resources, 0)
        return resources

    @staticmethod
    def _calculate_infrastructure(importance_x, trade_codes):
        '''Determine infrastructure rating'''
        infrastructure = D6.roll(2, importance_x)
        if (
                'Ba' in trade_codes or
                'Di' in trade_codes
        ):
            LOGGER.debug('Ba/Di => infrastructure = 0')
            infrastructure = 0
        if 'Lo' in trade_codes:
            LOGGER.debug('Lo => infrastructure = 1')
            infrastructure = 1
        if 'Ni' in trade_codes:
            LOGGER.debug('Ni => infrastructure = 1D6 + Ix')
            infrastructure = D6.roll(1, importance_x)
        infrastructure = max(infrastructure, 0)
        return infrastructure

    def calculate_ru(self):
        '''Calculate RU for system'''
        values = [
            int(self.resources),
            int(self.labor),
            int(self.infrastructure),
            self.efficiency]
        resu = 1
        for value in values:
            if value == 0:
                resu = resu
            else:
                resu = resu * value
        return resu

    def display(self):
        '''Display Ex'''
        return '({0}{1}{2}{3:+X})'.format(
            str(self.resources),
            str(self.labor),
            str(self.infrastructure),
            self.efficiency
        )

    def __str__(self):
        '''str() representation'''
        return self.display()

    def json_import(self, jdata):
        '''Import from JSON'''
        try:
            (resources, labor, infrastructure, efficiency) = re.match(
                r'\((.)(.)(.)([+-].)\)',
                jdata
            ).groups()
            self.resources = Pseudohex(str(resources))
            self.labor = Pseudohex(str(labor))
            self.infrastructure = Pseudohex(str(infrastructure))
            self.efficiency = int(efficiency, 16)
        except AttributeError:
            print('Error importing: jdata = {}'.format(jdata))
            raise


class CulturalExtension(object):
    '''Cultural extension data'''
    def __init__(self, population=0, importance_x=0, tech_level=0):
        # Reverse-engineer Traveller map checks
        if population == 0:
            self.homogeneity = Pseudohex(0)
            self.acceptance = Pseudohex(0)
            self.strangeness = Pseudohex(0)
            self.symbols = Pseudohex(0)
        else:
            homogeneity = population + FLUX.flux()
            acceptance = population + importance_x
            strangeness = FLUX.flux() + 5
            symbols = FLUX.flux() + tech_level
            self.homogeneity = Pseudohex(max(homogeneity, 1))
            self.acceptance = Pseudohex(max(acceptance, 1))
            self.strangeness = Pseudohex(max(strangeness, 1))
            self.symbols = Pseudohex(max(symbols, 1))

    def display(self):
        '''Display Cx'''
        return '[{}{}{}{}]'.format(
            str(self.homogeneity),
            str(self.acceptance),
            str(self.strangeness),
            str(self.symbols)
        )

    def __str__(self):
        '''str() representation'''
        return self.display()

    def json_import(self, jdata):
        '''Import from JSON'''
        try:
            (homogeneity, acceptance, strangeness, symbols) = re.match(
                r'\[(.)(.)(.)(.)\]', jdata).groups()
            self.homogeneity = Pseudohex(str(homogeneity))
            self.acceptance = Pseudohex(str(acceptance))
            self.strangeness = Pseudohex(str(strangeness))
            self.symbols = Pseudohex(str(symbols))
        except AttributeError:
            raise
