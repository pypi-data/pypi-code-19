'''
UPPs for planets
'''

from T5_worldgen.pseudohex import Pseudohex
from T5_worldgen.util import Table


class UPP(object):
    '''Old UPP object'''
    def __init__(self):
        self.value = '0'
        self.descriptions = []

    def get(self):
        '''Return value'''
        return self.value

    def set(self, value):
        '''Set value'''
        if isinstance(value, int):
            if value in range(0, len(self.descriptions)):
                self.value = self.descriptions[value][0]
            else:
                raise TypeError('Bad value %s', value)
        else:
            val = str(value).upper()
            valid = False
            for descr in self.descriptions:
                if val == descr[0]:
                    self.value = val
                    valid = True
            if valid is False:
                raise TypeError('Bad value %s', value)

    def asint(self):
        '''Return value as int'''
        values = []
        for descr in self.descriptions:
            values.append(descr[0])
        return values.index(self.value)

    def description(self):
        '''Return description for UPP value'''
        return self.descriptions[self.value]


class Starport(UPP):
    '''Starport'''
    def __init__(self):
        super(Starport, self).__init__()
        self.descriptions = [
            ('X', 'None'),
            ('E', 'Frontier'),
            ('D', 'Poor'),
            ('C', 'Routine'),
            ('B', 'Good'),
            ('A', 'Excellent')
        ]


class Size(Pseudohex):
    '''World size'''
    def __init__(self, value=0):
        super(Size, self).__init__(value)
        self.valid = '0123456789ABCDEFGXY'
        self.descriptions = [
            ("0", "<800 km, neg. gravity"),
            ("1", "1,600 km, 0.05 G"),
            ("2", "3,200 km, 0.15 G (Triton, Luna, Europa)"),
            ("3", "4,800 km, 0.25 G (Mercury, Ganymede)"),
            ("4", "6,400 km, 0.35 G (Mars)"),
            ("5", "8,000 km, 0.45 G"),
            ("6", "9,600 km, 0.70 G"),
            ("7", "11,200 km, 0.9 G"),
            ("8", "12,800 km, 1.0 G (Terra)"),
            ("9", "14,400 km, 1.25 G"),
            ("A", ">16,000 km, >1.4 G"),
            ("B", "Helian sizes"),
            ("C", "Helian sizes"),
            ("D", "Helian sizes"),
            ("E", "Helian sizes"),
            ("F", "Helian sizes"),
            ("G", "Jovian sizes"),
            ("X", "Planetary-Mass Artifact"),
            ("Y", "Asteroid Belt")
        ]
        self._set(value)

    def description(self):
        '''Return description for UPP value'''
        return self.descriptions[self._value]


class Atmosphere(Pseudohex):
    '''World atmosphere'''
    def __init__(self, value=0):
        super(Atmosphere, self).__init__(value)
        self.valid = '0123456789ABCDEFG'
        self.descriptions = [
            ("0", "Vacuum"),
            ("1", "Trace"),
            ("2", "Very Thin Tainted"),
            ("3", "Very Thin Breathable"),
            ("4", "Thin Tainted"),
            ("5", "Thin Breathable"),
            ("6", "Standard Breathable"),
            ("7", "Standard Tainted"),
            ("8", "Dense Breathable"),
            ("9", "Dense Tainted"),
            ("A", "Exotic"),
            ("B", "Corrosive"),
            ("C", "Insidious"),
            ("D", "Super-High Density"),
            ("E", "x"),
            ("F", "x"),
            ("G", "Gas Giant Envelope"),
        ]
        self._set(value)

    def description(self):
        '''Return description for UPP value'''
        return self.descriptions[self._value]


class Hydrographics(Pseudohex):
    '''World Hydrographics'''
    def __init__(self, value=0):
        super(Hydrographics, self).__init__(value)
        self.valid = '0123456789ABFG'
        self.descriptions = [
            ("0", "<5% (Trace)"),
            ("1", "<15% (Dry / tiny ice caps)"),
            ("2", "<25% (Small seas / ice caps)"),
            ("3", "<35% (Small oceans / large ice caps)"),
            ("4", "<45% (Wet)"),
            ("5", "<55% (Large oceans)"),
            ("6", "<65%"),
            ("7", "<75% (Terra)"),
            ("8", "<85% (Water world)"),
            ("9", "<95% (No continents)"),
            ("A", "<100% (Total coverage)"),
            ("B", "Superdense (incredibly deep world oceans)"),
            ("F", "Intense Volcanism (molten surface)"),
            ("G", "Gas Giant Core")
        ]
        self._set(value)

    def description(self):
        '''Return description for UPP value'''
        return self.descriptions[self._value]


class Biosphere(Pseudohex):
    '''World biosphere (non-standard UPP)'''
    def __init__(self, value=0):
        super(Biosphere, self).__init__(value)
        self.valid = '0123456789ABCD'
        self.descriptions = [
            ("0", "Sterile"),
            ("1", "Building Blocks (amino acids, or equivalent)"),
            ("2", "Single-celled organisms"),
            ("3", "Producers (atmosphere begins to transform)"),
            ("4", "Multi-cellular organisms"),
            ("5", "Complex single-celled life (nucleic cells, or equivalent)"),
            ("6", "Complex multi-cellular life (microscopic animals)"),
            ("7", "Small macroscopic life"),
            ("8", "Large macroscopic life"),
            ("9", "Simple global ecology (life goes out of the oceans and " +
             "onto land or into the air, etc.)"),
            ("A", "Complex global ecology"),
            ("B", "Proto-sapience"),
            ("C", "Full sapience"),
            ("D", "Trans-sapience (able to deliberately alter their own " +
             "evolution, minimum Tech Level C)")
        ]
        self.chemistry = ''
        self.age_modifier = 0
        self.chemistry_values = [('Water', 0), ('Ammonia', 1), ('Methane', 3)]
        self._set(value)

    def description(self):
        '''Return description for UPP value'''
        return self.descriptions[self._value]

    def generate_chemistry(self, ranges, roll):
        '''
        Inputs:
        - range in table
        - roll
        Returns:
        - chemistry
        - age modifier
        '''
        if len(ranges) == 3:
            # Build table
            chemistry_table = Table()
            for i in range(0, len(ranges)):
                chemistry_table.add_row(ranges[i], self.chemistry_values[i])

            # Generate
            return chemistry_table.lookup(roll)


class Population(Pseudohex):
    '''World population'''
    def __init__(self, value=0):
        super(Population, self).__init__(value)
        self.valid = '0123456789ABCDEF'
        self.descriptions = [
            ("0", "Uninhabited"),
            ("1", "Few"),
            ("2", "Hundreds"),
            ("3", "Thousands"),
            ("4", "Tens of thousands"),
            ("5", "Hundreds of thousands"),
            ("6", "Millions"),
            ("7", "Tens of millions"),
            ("8", "Hundreds of millions"),
            ("9", "Billions"),
            ("A", "Tens of billions"),
            ("B", "Hundreds of billions"),
            ("C", "Trillions"),
            ("D", "Tens of trillions"),
            ("E", "Hundreds of trillions"),
            ("F", "Quadrillions")
        ]
        self._set(value)

    def description(self):
        '''Return description for UPP value'''
        return self.descriptions[self._value]


class Government(Pseudohex):
    '''World government'''
    def __init__(self, value=0):
        super(Government, self).__init__(value)
        self.valid = '0123456789ABCDEF'
        self.descriptions = [
            ("0", "No government structure"),
            ("1", "Company/corporation"),
            ("2", "Participating democracy"),
            ("3", "Self-perpetuating oligarchy"),
            ("4", "Representative democracy"),
            ("5", "Feudal technocracy"),
            ("6", "Captive government/colony"),
            ("7", "Balkanization"),
            ("8", "Civil service bureaucracy"),
            ("9", "Impersonal bureaucracy"),
            ("A", "Charismatic dictatorship"),
            ("B", "Non-charismatic dictatorship"),
            ("C", "Charismatic oligarchy"),
            ("D", "Religious dictatorship"),
            ("E", "Religious autocracy"),
            ("F", "Totalitarian oligarchy")
        ]
        self._set(value)

    def description(self):
        '''Return description for UPP value'''
        return self.descriptions[self._value]


class LawLevel(Pseudohex):
    '''World law level'''
    def __init__(self, value=0):
        super(LawLevel, self).__init__(value)
        self.valid = '0123456789ABCDEFGHJ'
        self.descriptions = [
            ("0", "No law. No restrictions"),
            ("1", "Low law. Prohibition of WMD, psi weapons"),
            ("2", "Low law. Prohibition of 'portable' weapons"),
            ("3", "Low law. Prohibition of acid, fire, gas weapons"),
            ("4", "Moderate law. Prohibition of laser, beam weapons"),
            ("5", "Moderate law. No shock, EMP, rad, mag, grav weapons"),
            ("6", "Moderate law. Prohibition of machine guns"),
            ("7", "Moderate law. Prohibition of pistols"),
            ("8", "High law. Open display of weapons prohibited"),
            ("9", "High law. No weapons outside the home"),
            ("A", "Extreme law. All weapons prohibited"),
            ("B", "Extreme law. Continental passports required"),
            ("C", "Extreme law. Unrestricted invasion of privacy"),
            ("D", "Extreme law. Paramilitary law enforcement"),
            ("E", "Extreme law. Full-fledge police state"),
            ("F", "Extreme law. Daily life rigidly controlled"),
            ("G", "Extreme law. Disproportionate punishment"),
            ("H", "Extreme law. Legalized oppressive practices"),
            ("J", "Extreme law. Routine oppression")
        ]
        self._set(value)

    def description(self):
        '''Return description for UPP value'''
        return self.descriptions[self._value]


class TechLevel(Pseudohex):
    '''World tech level'''
    def __init__(self, value=0):
        super(TechLevel, self).__init__(value)
        self.valid = '0123456789ABCDEFGHJKLMNP'
        self.descriptions = [
            ("0", "No industry. Everything must be imported."),
            ("1", "Primitive. Mostly only raw materials made locally."),
            ("2", "Primitive. Mostly only raw materials made locally."),
            ("3", "Primitive. Mostly only raw materials made locally."),
            ("4", "Industrial. Local tools maintained, some produced."),
            ("5", "Industrial. Local tools maintained, some produced."),
            ("6", "Industrial. Local tools maintained, some produced."),
            ("7", "Pre-Stellar. Production and maintenance of space " +
             "technologies."),
            ("8", "Pre-Stellar. Production and maintenance of space " +
             "technologies."),
            ("9", "Pre-Stellar. Production and maintenance of space " +
             "technologies."),
            ("A", "Early Stellar. Support for A.I. and local starship " +
             "production."),
            ("B", "Early Stellar. Support for A.I. and local starship " +
             "production."),
            ("C", "Average Stellar. Support for terraforming, flying " +
             "cities, clones."),
            ("D", "Average Stellar. Support for terraforming, flying " +
             "cities, clones."),
            ("E", "Average Stellar. Support for terraforming, flying " +
             "cities, clones."),
            ("F", "High Stellar. Support for highest of the high tech."),
            ("G", "Imperial Maximum"),
            ("H", "Darrian Maximum"),
            ("J", "Presumed Ancient"),
            ("K", "Presumed Ancient")
        ]
        self._set(value)

    def description(self):
        '''Return description for UPP value'''
        return self.descriptions[self._value]
