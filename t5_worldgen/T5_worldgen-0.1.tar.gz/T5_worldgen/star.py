'''star module'''

import logging
import json

from T5_worldgen.util import Die, Flux, Table

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.CRITICAL)

D2 = Die(2)
D5 = Die(5)
D6 = Die(6)
D10 = Die(10)
FLUX = Flux()


class _Star(object):
    '''Star base class'''
    # Spectral type
    spectral_type_table = Table()
    spectral_type_table.add_row(-6, 'OB')
    spectral_type_table.add_row((-5, -4), 'A')
    spectral_type_table.add_row((-3, -2), 'F')
    spectral_type_table.add_row((-1, 0), 'G')
    spectral_type_table.add_row((1, 2), 'K')
    spectral_type_table.add_row((3, 5), 'M')
    spectral_type_table.add_row((6, 8), 'BD')

    size_o_table = Table()
    size_o_table.add_row((-6, -5), 'Ia')
    size_o_table.add_row(-4, 'Ib')
    size_o_table.add_row(-3, 'II')
    size_o_table.add_row((-2, 0), 'III')
    size_o_table.add_row((1, 3), 'V')
    size_o_table.add_row(4, 'IV')
    size_o_table.add_row(5, 'D')
    size_o_table.add_row((6, 8), 'IV')

    # Size
    size_b_table = Table()
    size_b_table.add_row((-6, -5), 'Ia')
    size_b_table.add_row(-4, 'Ib')
    size_b_table.add_row(-3, 'II')
    size_b_table.add_row((-2, 1), 'III')
    size_b_table.add_row((2, 3), 'V')
    size_b_table.add_row(4, 'IV')
    size_b_table.add_row(5, 'D')
    size_b_table.add_row((6, 8), 'IV')

    size_a_table = Table()
    size_a_table.add_row((-6, -5), 'Ia')
    size_a_table.add_row(-4, 'Ib')
    size_a_table.add_row(-3, 'II')
    size_a_table.add_row(-2, 'III')
    size_a_table.add_row(-1, 'IV')
    size_a_table.add_row((0, 4), 'V')
    size_a_table.add_row(5, 'D')
    size_a_table.add_row((6, 8), 'V')

    size_f_table = Table()
    size_f_table.add_row((-6, -5), 'II')
    size_f_table.add_row(-4, 'III')
    size_f_table.add_row(-3, 'IV')
    size_f_table.add_row((-2, 3), 'V')
    size_f_table.add_row(4, 'VI')
    size_f_table.add_row(5, 'D')
    size_f_table.add_row((6, 8), 'VI')

    size_g_table = Table()
    size_g_table.add_row((-6, -5), 'II')
    size_g_table.add_row(-4, 'III')
    size_g_table.add_row(-3, 'IV')
    size_g_table.add_row((-2, 3), 'V')
    size_g_table.add_row(4, 'VI')
    size_g_table.add_row(5, 'D')
    size_g_table.add_row((6, 8), 'VI')

    size_k_table = Table()
    size_k_table.add_row((-6, -5), 'II')
    size_k_table.add_row(-4, 'III')
    size_k_table.add_row(-3, 'IV')
    size_k_table.add_row((-2, 3), 'V')
    size_k_table.add_row(4, 'VI')
    size_k_table.add_row(5, 'D')
    size_k_table.add_row((6, 8), 'VI')

    size_m_table = Table()
    size_m_table.add_row((-6, -3), 'II')
    size_m_table.add_row(-2, 'III')
    size_m_table.add_row((-1, 3), 'V')
    size_m_table.add_row(4, 'VI')
    size_m_table.add_row(5, 'D')
    size_m_table.add_row((6, 8), 'VI')

    # Habitable zone
    hz_orbit_o_table = Table()
    hz_orbit_o_table.add_row('Ia', 15)
    hz_orbit_o_table.add_row('Ib', 15)
    hz_orbit_o_table.add_row('II', 14)
    hz_orbit_o_table.add_row('III', 13)
    hz_orbit_o_table.add_row('IV', 12)
    hz_orbit_o_table.add_row('V', 11)
    hz_orbit_o_table.add_row('D', 1)

    hz_orbit_b_table = Table()
    hz_orbit_b_table.add_row('Ia', 13)
    hz_orbit_b_table.add_row('Ib', 13)
    hz_orbit_b_table.add_row('II', 12)
    hz_orbit_b_table.add_row('III', 11)
    hz_orbit_b_table.add_row('IV', 10)
    hz_orbit_b_table.add_row('V', 9)
    hz_orbit_b_table.add_row('D', 0)

    hz_orbit_a_table = Table()
    hz_orbit_a_table.add_row('Ia', 12)
    hz_orbit_a_table.add_row('Ib', 11)
    hz_orbit_a_table.add_row('II', 9)
    hz_orbit_a_table.add_row('III', 7)
    hz_orbit_a_table.add_row('IV', 7)
    hz_orbit_a_table.add_row('V', 7)
    hz_orbit_a_table.add_row('D', 0)

    hz_orbit_f_table = Table()
    hz_orbit_f_table.add_row('Ia', 11)
    hz_orbit_f_table.add_row('Ib', 10)
    hz_orbit_f_table.add_row('II', 9)
    hz_orbit_f_table.add_row('III', 6)
    hz_orbit_f_table.add_row('IV', 6)
    hz_orbit_f_table.add_row('V', 5)
    hz_orbit_f_table.add_row('VI', 3)
    hz_orbit_f_table.add_row('D', 0)

    hz_orbit_g_table = Table()
    hz_orbit_g_table.add_row('Ia', 12)
    hz_orbit_g_table.add_row('Ib', 10)
    hz_orbit_g_table.add_row('II', 9)
    hz_orbit_g_table.add_row('III', 7)
    hz_orbit_g_table.add_row('IV', 5)
    hz_orbit_g_table.add_row('V', 3)
    hz_orbit_g_table.add_row('VI', 2)
    hz_orbit_g_table.add_row('D', 0)

    hz_orbit_k_table = Table()
    hz_orbit_k_table.add_row('Ia', 12)
    hz_orbit_k_table.add_row('Ib', 10)
    hz_orbit_k_table.add_row('II', 9)
    hz_orbit_k_table.add_row('III', 8)
    hz_orbit_k_table.add_row('IV', 5)
    hz_orbit_k_table.add_row('V', 2)
    hz_orbit_k_table.add_row('VI', 1)
    hz_orbit_k_table.add_row('D', 0)

    hz_orbit_m_table = Table()
    hz_orbit_m_table.add_row('Ia', 12)
    hz_orbit_m_table.add_row('Ib', 11)
    hz_orbit_m_table.add_row('II', 10)
    hz_orbit_m_table.add_row('III', 0)
    hz_orbit_m_table.add_row('V', 0)
    hz_orbit_m_table.add_row('VI', 0)
    hz_orbit_m_table.add_row('D', 0)

    def __init__(self):
        self.spectral_type = ''
        self.decimal = 0
        self.size = ''
        self.companion = None
        self.primary_rolls = {}
        self.habitable_zone = ''

    def __str__(self):
        return self.code()

    def code(self):
        '''Return spec type, decimal, size for this star only'''
        if self.spectral_type == 'BD':
            return 'BD'
        elif self.size == 'D':
            return 'D'
        else:
            return '{}{} {}'.format(
                self.spectral_type, self.decimal, self.size)

    def display(self):
        '''Combine spectral type, decimal, size'''
        resp = [str(self)]
        if self.companion is not None:
            resp.append(str(self.companion))
        return ' '.join(resp)

    def set_decimal(self):
        '''Set spectral decimal'''
        if self.spectral_type == 'F' and self.size == 'VI':
            self.decimal = D5.roll(1, -1)
        else:
            self.decimal = D10.roll(1, -1)

    def has_companion(self):
        '''Companion star?'''
        if FLUX.flux() >= 3:
            LOGGER.debug('Companion exists')
            self.companion = Secondary(self.primary_rolls)

    def json_import(self, jdata):
        '''Import from JSON'''
        LOGGER.setLevel(logging.ERROR)
        star_dict = json.loads(jdata)
        self.decimal = star_dict['decimal']
        self.habitable_zone = star_dict['habitable_zone']
        self.spectral_type = star_dict['spectral_type']
        self.size = star_dict['size']
        if star_dict['companion'] is not None:
            self.companion = Secondary({'Spectral type': 3, 'Size': 3})
            self.companion.json_import(star_dict['companion'])
        else:
            self.companion = None

    def set_hz(self):
        '''Set habitable zone orbit'''
        if self.spectral_type == 'O':
            self.habitable_zone = self.hz_orbit_o_table.lookup(self.size)
        elif self.spectral_type == 'B':
            self.habitable_zone = self.hz_orbit_b_table.lookup(self.size)
        elif self.spectral_type == 'A':
            self.habitable_zone = self.hz_orbit_a_table.lookup(self.size)
        elif self.spectral_type == 'F':
            self.habitable_zone = self.hz_orbit_f_table.lookup(self.size)
        elif self.spectral_type == 'G':
            self.habitable_zone = self.hz_orbit_g_table.lookup(self.size)
        elif self.spectral_type == 'K':
            self.habitable_zone = self.hz_orbit_k_table.lookup(self.size)
        elif self.spectral_type == 'M':
            self.habitable_zone = self.hz_orbit_m_table.lookup(self.size)


class Primary(_Star):
    '''Primary class'''
    def __init__(self):
        super(Primary, self).__init__()
        self.primary_rolls = {'Spectral type': 0, 'Size': 0}
        self.secondaries = {'Close': None, 'Near': None, 'Far': None}
        self.set_spectral_type()
        self.set_decimal()
        self.set_size()
        LOGGER.debug('Primary: primary_rolls = %s', self.primary_rolls)
        self.set_hz()
        self.has_companion()
        for zone in self.secondaries:
            self.has_secondary(zone)

    def display(self):
        '''Combine spectral type, decimal, size'''
        resp = [str(self)]
        if self.companion is not None:
            resp.append(str(self.companion))
        for zone in self.secondaries:
            if self.secondaries[zone] is not None:
                resp.append(str(self.secondaries[zone]))
        return ' '.join(resp)

    def set_spectral_type(self):
        '''Set spectral type'''
        roll = FLUX.flux()
        self.spectral_type = self.spectral_type_table.lookup(roll)
        if self.spectral_type == 'OB':
            # Decide randomly
            self.spectral_type = 'OB'[D2.roll(1, -1)]
        self.primary_rolls['Spectral type'] = roll

    def set_size(self):
        '''Set size'''
        roll = FLUX.flux()
        self.primary_rolls['Size'] = roll
        if self.spectral_type == 'O':
            self.size = self.size_o_table.lookup(roll)
        elif self.spectral_type == 'B':
            self.size = self.size_b_table.lookup(roll)
        elif self.spectral_type == 'A':
            self.size = self.size_a_table.lookup(roll)
        elif self.spectral_type == 'F':
            self.size = self.size_f_table.lookup(roll)
        elif self.spectral_type == 'G':
            self.size = self.size_g_table.lookup(roll)
        elif self.spectral_type == 'K':
            self.size = self.size_k_table.lookup(roll)
        elif self.spectral_type == 'M':
            self.size = self.size_m_table.lookup(roll)

    def has_secondary(self, zone):
        '''Secondary in zone?'''
        if FLUX.flux() >= 3:
            LOGGER.debug('Secondary in zone %s exists', zone)
            self.secondaries[zone] = Secondary(self.primary_rolls)

    def as_json(self):
        '''Return JSON representation of star'''
        star_dict = {
            'spectral_type': self.spectral_type,
            'decimal': self.decimal,
            'size': self.size,
            'habitable_zone': self.habitable_zone
        }
        if self.companion is not None:
            star_dict['companion'] = self.companion.as_json()
        else:
            star_dict['companion'] = None
        star_dict['secondaries'] = {}
        for zone in self.secondaries.keys():
            if self.secondaries[zone] is not None:
                star_dict['secondaries'][zone] = \
                    self.secondaries[zone].as_json()
        return json.dumps(star_dict)

    def json_import(self, jdata):
        '''Import from JSON'''
        LOGGER.setLevel(logging.ERROR)
        # Common elements (spectral_type, size, decmal, hz, companion)
        super(Primary, self).json_import(jdata)
        star_dict = json.loads(jdata)
        # Secondaries
        for zone in star_dict['secondaries'].keys():
            self.secondaries[zone] = Secondary({'Spectral type': 3, 'Size': 3})
            self.secondaries[zone].json_import(star_dict['secondaries'][zone])



class Secondary(_Star):
    '''Non-primary star class'''
    def __init__(self, primary_rolls):
        super(Secondary, self).__init__()
        self.primary_rolls = primary_rolls
        LOGGER.debug('Secondary: primary_rolls = %s', self.primary_rolls)
        self.set_spectral_type()
        self.set_decimal()
        self.set_size()
        self.set_hz()
        self.has_companion()

    def set_spectral_type(self):
        '''Set spectral type'''
        roll = D6.roll(1, -1)
        roll += self.primary_rolls['Spectral type']
        roll = min(roll, 8)
        roll = max(roll, -6)
        self.spectral_type = self.spectral_type_table.lookup(roll)
        if self.spectral_type == 'OB':
            # Decide randomly
            self.spectral_type = 'OB'[D2.roll(1, -1)]

    def set_size(self):
        '''Set size'''
        roll = D6.roll(1, -1)
        roll += self.primary_rolls['Size']
        roll = min(roll, 8)
        roll = max(roll, -6)
        if self.spectral_type == 'O':
            self.size = self.size_o_table.lookup(roll)
        elif self.spectral_type == 'B':
            self.size = self.size_b_table.lookup(roll)
        elif self.spectral_type == 'A':
            self.size = self.size_a_table.lookup(roll)
        elif self.spectral_type == 'F':
            self.size = self.size_f_table.lookup(roll)
        elif self.spectral_type == 'G':
            self.size = self.size_g_table.lookup(roll)
        elif self.spectral_type == 'K':
            self.size = self.size_k_table.lookup(roll)
        elif self.spectral_type == 'M':
            self.size = self.size_m_table.lookup(roll)

    def as_json(self):
        '''Return JSON representation'''
        star_dict = {
            'spectral_type': self.spectral_type,
            'decimal': self.decimal,
            'size': self.size,
            'habitable_zone': self.habitable_zone,
        }
        if self.companion is not None:
            star_dict['companion'] = self.companion.as_json()
        else:
            star_dict['companion'] = None

        return json.dumps(star_dict)
