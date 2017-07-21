'''Sector/subsector'''
from __future__ import print_function

from random import randint, seed
import re
import logging
from T5_worldgen.system import System
from T5_worldgen.util import Table

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.CRITICAL)

class _MappingRegion(object):
    '''Sector/subsector base class'''

    system_presence_table = Table()
    system_presence_table.add_row('Extra galactic', 1)
    system_presence_table.add_row('Rift', 3)
    system_presence_table.add_row('Sparse', 17)
    system_presence_table.add_row('Scattered', 33)
    system_presence_table.add_row('Standard', 50)
    system_presence_table.add_row('Dense', 66)
    system_presence_table.add_row('Cluster', 83)
    system_presence_table.add_row('Core', 91)

    def __init__(self, name, density='Standard'):
        seed()
        self.name = name
        self.size_x = 0
        self.size_y = 0
        self.hexes = {}
        self.density = density

    def display(self):
        '''Display'''
        hexlist = sorted(self.hexes.keys())
        for hex_id in hexlist:
            print(self.hexes[hex_id].display())

    def as_list(self):
        '''Return contents as list'''
        out = []
        hexlist = sorted(self.hexes.keys())
        for hex_id in hexlist:
            out.append(self.hexes[hex_id].display())
        return out

    @staticmethod
    def percentile():
        '''1-100%'''
        return randint(1, 100)

    def process_hex(self, hex_id, ss_id=''):
        '''Add system on probability check'''
        name = 'Name-{}{}'.format(hex_id, ss_id)
        if self.percentile() <= \
                self.system_presence_table.lookup(self.density):
            self.hexes[hex_id] = System(name, hex_id)

    def t5_tab(self):
        '''Output in T5 tab format'''
        out = ['\t'.join([
            'Hex', 'Name', 'UWP', 'Remarks', '{Ix}', '(Ex)', '[Cx]',
            'Nobility', 'Bases', 'Zone', 'PBG', 'W', 'Allegiance',
            'Stars'])]
        out.extend(self.as_list())
        return out

    def find_nearby_hexes(self, o_hex_id, radius=1):
        '''Find hexes within radius of hex_id'''

        '''
            B
        A       C
            O
        F       D
            E

        Add column of r+1 hexes starting at A, C
        Add column of r+2 hexes starting at A+1
        ... etc ...
        Add column of 2r hexes starting at B (excluding O)

        Hex IDs on A->B (and B->C) depend on co-ordinates of O, size of r
        '''
        nearby_hexes = []
        o_col = int(o_hex_id[:2])
        o_row = int(o_hex_id[2:])
        side_length = radius + 1
        a_col = o_col - radius
        c_col = o_col + radius
        if self._is_even(o_col):
            if self._is_even(radius):
                x_row = o_row - int(radius / 2) + 0.5
            else:
                x_row = o_row - int(radius / 2)
        else:
            if self._is_even(radius):
                x_row = o_row - int(radius / 2)
            else:
                x_row = o_row - int(radius / 2) - 0.5

        LOGGER.debug('O = %s radius = %s', o_hex_id, radius)
        LOGGER.debug('A = %s%s', a_col, x_row)
        col_length = side_length
        for col in range(0, radius):
            l_col = a_col + col
            r_col = c_col - col
            LOGGER.debug('l_col = %s r_col = %s x_row = %s', l_col, r_col, x_row)
            LOGGER.debug('col_length = %s', col_length)
            for idx in range(0, col_length):
                row = x_row + idx
                if l_col > 0 and int(row) > 0:
                    l_hex_id = '{0:02d}{1:02d}'.format(l_col, int(row))
                    LOGGER.debug('Adding %s', l_hex_id)
                    nearby_hexes.append(l_hex_id)
                if r_col > 0 and int(row) > 0:
                    r_hex_id = '{0:02d}{1:02d}'.format(r_col, int(row))
                    LOGGER.debug('Adding %s', r_hex_id)
                    nearby_hexes.append(r_hex_id)
            x_row -= 0.5
            col_length += 1
        for row in range(o_row - radius, o_row + radius + 1):
            if row > 0:
                hex_id = '{0:02d}{1:02d}'.format(o_col, row)
                if hex_id != o_hex_id:
                    LOGGER.debug('Adding %s', hex_id)
                    nearby_hexes.append(hex_id)
        return sorted(nearby_hexes)

    @staticmethod
    def _is_even(number):
        '''Return True for even number'''
        return float(number) / 2 == int(number / 2)

    def find_nearby_systems(self, hex_id, radius):
        '''Find worlds/systems in nearby hexes'''
        nearby_worlds = []
        for hex_id in self.find_nearby_hexes(hex_id, radius):
            if self.is_system(hex_id):
                nearby_worlds.append(self.is_system(hex_id))
        return nearby_worlds

    def is_system(self, hex_id):
        '''Return False if there is a system at hex_id, system otherwise'''
        if hex_id in self.hexes.keys():
            return self.hexes[hex_id]
        else:
            return False

    def find_owning_system(self, hex_id):
        '''Return hex_id for most important system within 6 hexes'''
        nearby_systems = self.find_nearby_systems(hex_id, 6)
        most_important_system_ix = []
        importance = -10
        for system in nearby_systems:
            if int(system.importance_x) == importance:
                most_important_system_ix.append(system)
            elif int(system.importance_x) > importance:
                most_important_system_ix = [system]
                importance = int(system.importance_x)
        if len(most_important_system_ix) > 1:
            # Need to resolve tie - use Population
            population = -1
            most_important_system_pop = []
            for system in most_important_system_ix:
                if int(system.mainworld.population) == population:
                    most_important_system_pop.append(system)
                elif int(system.mainworld.population) > population:
                    most_important_system_pop = [system]
                    population = int(system.mainworld.population)
            if len(most_important_system_pop) > 1:
                # Another tie - resolve wth TL
                tech_level = -1
                most_important_system_tl = []
                for system in most_important_system_pop:
                    if int(system.mainworld.tech_level) == tech_level:
                        most_important_system_tl.append(system)
                    elif int(system.mainworld.tech_level) > tech_level:
                        most_important_system_tl = [system]
                        tech_level = int(system.mainworld.tech_level)
                if len(most_important_system_tl) > 1:
                    # Tie - pick one at random
                    return(
                        most_important_system_tl[randint(
                            0, len(most_important_system_tl) - 1)].hex
                    )
                else:
                    return most_important_system_tl[0].hex
            else:
                return most_important_system_pop[0].hex
        else:
            return most_important_system_ix[0].hex

    def trade_code_owning_system(self):
        '''Trade codes extra pass - O:'''
        for hex_id in self.hexes.keys():
            owned = False
            trade_codes = self.hexes[hex_id].mainworld.trade_codes
            for i, code in enumerate(trade_codes):
                if code.startswith('O:'):
                    LOGGER.debug('Found owned system %s', str(self.hexes[hex_id]))
                    owner = self.find_owning_system(hex_id)
                    trade_codes[i] = 'O:{}'.format(owner)
                    owned = True
            if owned:
                self.hexes[hex_id].mainworld.trade_codes = trade_codes


class Subsector(_MappingRegion):
    '''Subsector
    Subsector(name)
    Optional
    - subsector_id (dflt = '')
    - density (dflt='Standard')
    '''
    def __init__(self, name, subsector_id='', density='Standard'):
        super(Subsector, self).__init__(name, density)
        self.size_x = 8
        self.size_y = 10
        self.base_x = 0
        self.base_y = 0
        self.subsector_id = subsector_id
        self.populate_subsector()

    def populate_subsector(self):
        '''Generate systems'''
        for x_coord in range(1, self.size_x + 1):
            for y_coord in range(1, self.size_y + 1):
                self.process_hex(
                    '{0:02d}{1:02d}'.format(x_coord, y_coord),
                    self.subsector_id)


class Sector(_MappingRegion):
    '''Sector'''
    def __init__(self, name, density='Standard'):
        super(Sector, self).__init__(name, density)
        self.size_x = 32
        self.size_y = 40
        self._subsector_offsets = {}
        self._determine_offsets()
        self.subsectors = {}
        self.generate_subsectors()
        self.get_system_hex = re.compile(r'^(\d\d\d\d)')
        # self.populate_hexes()
        self.populate_sector()
        self.trade_code_owning_system()
        self.populate_subsectors()

    def display(self):
        '''Display'''
        print('\t'.join([
            'Hex', 'Name', 'UWP', 'Remarks', '{Ix}', '(Ex)', '[Cx]',
            'Nobility', 'Bases', 'Zone', 'PBG', 'W', 'Allegiance',
            'Stars']))
        subsectors = 'AEIMBFJNCGKODHLP'
        for ss_id in subsectors:
            for hex_id in sorted(self.subsectors[ss_id].hexes.keys()):
                data = self.subsectors[ss_id].hexes[hex_id].display()
                # Transform hex to Sector co-ordinates
                print(self.transform_coordinates(data, ss_id))

    def t5_tab(self):
        '''Output in T5 tabular format'''
        out = ['\t'.join([
            'Hex', 'Name', 'UWP', 'Remarks', '{Ix}', '(Ex)', '[Cx]',
            'Nobility', 'Bases', 'Zone', 'PBG', 'W', 'Allegiance',
            'Stars'])]
        subsectors = 'AEIMBFJNCGKODHLP'
        for ss_id in subsectors:
            for hex_id in sorted(self.subsectors[ss_id].hexes.keys()):
                data = self.subsectors[ss_id].hexes[hex_id].display()
                # Transform hex to Sector co-ordinates
                out.append(self.transform_coordinates(data, ss_id))
        return out


    def generate_subsectors(self):
        '''Generate subsectors'''
        for ss_id in 'ABCDEFGHIJKLMNOP':
            self.subsectors[ss_id] = Subsector(
                'Subsector-{}'.format(ss_id), ss_id, self.density)
            self.subsectors[ss_id].hexes = {}

    def _determine_offsets(self):
        '''Determine hex offsets by subsector_id'''
        for ctr, row in enumerate(['ABCD', 'EFGH', 'IJKL', 'MNOP']):
            for ss_id in row:
                offset_x = row.index(ss_id) * 8
                offset_y = ctr * 10
                self._subsector_offsets[ss_id] = (offset_x, offset_y)

    def transform_coordinates(self, system_data, ss_id):
        '''System data: transform hex to Sector co-ordinates'''
        orig = self.get_system_hex.match(system_data).group(1)
        x_id = int(orig[:2])
        y_id = int(orig[2:])
        x_id += self._subsector_offsets[ss_id][0]
        y_id += self._subsector_offsets[ss_id][1]
        new = '{0:02d}{1:02d}'.format(x_id, y_id)
        return system_data.replace(orig, new, 1)

    def as_list(self):
        '''Output subsectors as list'''
        out = []
        subsectors = 'AEIMBFJNCGKODHLP'
        for ss_id in subsectors:
            for hex_id in sorted(self.subsectors[ss_id].hexes.keys()):
                data = self.subsectors[ss_id].hexes[hex_id].as_list()
                # Transform hex to Sector co-ordinates
                print(self.transform_coordinates(data, ss_id))

    def populate_hexes(self):
        '''Populate hexes dict with subsector data'''
        for ss_id in self.subsectors.keys():
            subsector = self.subsectors[ss_id]
            for hex_id in subsector.hexes.keys():
                new_hex_id = self.transform_coordinates(hex_id, ss_id)
                self.hexes[new_hex_id] = subsector.hexes[hex_id]

    def populate_sector(self):
        '''Populate sector'''
        for x_coord in range(1, self.size_x + 1):
            for y_coord in range(1, self.size_y + 1):
                hex_id = '{0:02d}{1:02d}'.format(x_coord, y_coord)
                self.process_hex(hex_id, self.find_subsector_id(hex_id))

    @staticmethod
    def find_subsector_id(hex_id):
        '''hex_id in range 0000-3240, return subsector ID (A-P)'''
        hex_id_col = int(hex_id[:2]) - 1
        hex_id_row = int(hex_id[2:]) - 1
        try:
            return['ABCD', 'EFGH', 'IJKL', 'MNOP'][hex_id_row / 10][hex_id_col / 8]
        except IndexError:
            print(
                'IndexError: hex_id = {} ({}, {})'.format(
                    hex_id, hex_id_col, hex_id_row))
            raise

    def populate_subsectors(self):
        '''Populate subsectors using data from self.hexes'''
        for hex_id in self.hexes.keys():
            subsector_id = self.find_subsector_id(hex_id)
            # system = self.hexes[hex_id]
            jdata = self.hexes[hex_id].as_json()
            ss_hex_id = self.sector_hex_to_subsector_hex(hex_id)
            LOGGER.debug(
                'hex_id = %s, ss_hex_id = %s ss_id = %s',
                hex_id, ss_hex_id, subsector_id)
            LOGGER.debug('(1) self.hexes.hex = %s', self.hexes[hex_id].hex)
            self.subsectors[subsector_id].hexes[ss_hex_id] = System()
            self.subsectors[subsector_id].hexes[ss_hex_id].json_import(jdata)
            self.subsectors[subsector_id].hexes[ss_hex_id].hex = ss_hex_id
            LOGGER.debug('(2) self.hexes.hex = %s', self.hexes[hex_id].hex)
        LOGGER.setLevel(logging.CRITICAL)

    @staticmethod
    def sector_hex_to_subsector_hex(hex_id):
        '''Transform sector hex_id to subsector hex_id'''
        hex_id_col = int(hex_id[:2])
        hex_id_row = int(hex_id[2:])
        col = hex_id_col % 8
        row = hex_id_row % 10
        if col == 0:
            col = 8
        if row == 0:
            row = 10
        return '{0:02d}{1:02d}'.format(col, row)

    def subsector_hex_to_sector_hex(self, hex_id, subsector_id):
        '''Transform subsector hex_id to sector hex_id, given subsector_id'''
        hex_id_col = int(hex_id[:2])
        hex_id_row = int(hex_id[2:])
        return '{0:02d}{1:02d}'.format(
            hex_id_col + self._subsector_offsets[subsector_id][0],
            hex_id_row + self._subsector_offsets[subsector_id][1]
        )
