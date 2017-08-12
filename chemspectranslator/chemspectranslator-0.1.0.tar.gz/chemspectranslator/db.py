import sys
import numpy as np
import csv

class ID(object):
    '''
    An ID is a data structure that consists of an integer value, which is associated with a
    number of Species items, where each species can have a multiplier associated
    with it (e.g. ID 12 == 3 PAR).
    '''
    def __repr__(self):
        return 'ID {:d}'.format(self.value)
    def calcCount(self, input_species):
        count = [ f for f, x in self.species if x == input_species ]
        return count[0]
    def addSpecies(self, species, count):
        self.species.append( (count, species) )
    def __eq__(self, other):
        return self.value == other.value
    def __hash__(self):
        return hash(self.value)
    def __init__(self, value):
        self.value   = value
        self.species = []

class Species(object):
    '''
    A Species is a data structure that consists of a string name, which is associated with a
    number of ID items, where each id can have a fraction associated with
    it (e.g. TOLUENE = 0.3 * 4).
    '''
    def __repr__(self):
        return 'Species {:s}'.format(self.name)
    def calcFractionalAmount(self, input_id):
        id     = [ x for f, x in self.ids if x == input_id ]
        all    = np.array( [ f for f, x in self.ids ] )
        given  = np.greater_equal(all, 0.0)
        fixed  = sum(all[given])
        if np.any(np.logical_not(given)):
            remaining = 1.0 - fixed
            all[np.logical_not(given)] = remaining / len(all[np.logical_not(given)])
        f = [ all[i] for i, x in enumerate(self.ids) if x[1] == input_id ][0]
        return f
    def addID(self, id, prefactor):
        self.ids.append( (prefactor, id) )
    def __hash__(self):
        return hash(self.name)
    def __eq__(self, other):
        return self.name == other.name
    def __init__(self, name):
        self.name  = name
        self.ids   = []

class Mechanism(object):
    '''
    A mechanism is a collection of ID and Species items, with reciprocal relations such that
    a species can consist of multiple IDs, and an ID can be a fraction of (several) species.
    '''
    def __repr__(self):
        return '{:s} ({:d} species, {:d} ids)'.format(self.name, len(self.species), len(self.ids))
    def addSpecies(self, species):
        self.species.append(species)
        self.speciesnames.append(species.name)
    def addID(self, id):
        self.ids.append(id)
        self.idnames.append(id.value)
    def getIDsForSpecies(self, input_species):
        spec = self.findSpecies(input_species.name)
        return spec[0].ids if len(spec) == 1 else None
    def getSpeciesForID(self, input_id):
        id = self.findID(input_id.value)
        return id[0].species if len(id) == 1 else None
    def findSpecies(self, input_name, caseSensitive=True):
        if caseSensitive:
            res = [ self.species[i] for i, v in enumerate(self.speciesnames) if v == input_name ]
        else:
            res = [ self.species[i] for i, v in enumerate(self.speciesnames) if v.lower() == input_name.lower() ]
        return res
    def findID(self, input_value):
        return [ self.ids[i] for i, v in enumerate(self.idnames) if v == input_value ]
    def addItem(self, new_species, new_id, prefactor = -1.0, count = 1.0):
        # check if this species already exists
        species = self.findSpecies(new_species.name)
        if len(species) == 0:
            # if not, add it
            species = new_species
            self.addSpecies(species)
        else:
            # findSpecies returns a list
            species = species[0]

        # check if this id already exists
        id = self.findID(new_id.value)
        if len(id) == 0:
            # if not, add it
            id = new_id
            self.addID(id)
        else:
            # findID returns a list
            id = id[0]

        species.addID(id, prefactor)
        id.addSpecies(species, count)

    def __init__(self, name):
        self.name    = name
        self.ids     = []
        # array holding the comparison values for faster indexing
        self.idnames = []
        self.species = []
        # array holding the comparison values for faster indexing
        self.speciesnames = []

class TranslationResult(object):
    '''
    A TranslationResult is the object resulting from a translate query to the DB. Contains
    query, source and target information, as well as the actual translation result.
    '''
    def __repr__(self):
        return 'TranslationResult (<{:s}> from <{:s}> to <{:s}>)'.format(self.input, self.source, self.target)
    def __getitem__(self, index):
        return self.result[index]
    def __str__(self):
        specs = list(set([ species for prefactor, species in self.result ]))
        total = { x: 0 for x in specs }
        for prefactor, species in self.result:
            total[species] += prefactor
        return ' + '.join([ "{:6.3f} * {:s}".format(prefactor, species) for species, prefactor in total.iteritems() ])
    def __init__(self, input, source, target, prefactors, species):
        self.input  = input
        self.source = source
        self.target = target

        tresult = { x.name: 0.0 for x in set(species) }
        def add(spec, amount):
            tresult[spec] += amount
        nul = [ add(x.name, fac) for fac, x in zip(prefactors, species) ]

        self.result = zip( [ f for f in tresult.itervalues() ], [ f for f in tresult.iterkeys() ])

class DB(object):
    '''
    The DB is the overarching data structure of a chemspectranslator, it holds all the Mechanism items,
    cares about listing, dumping, merging of mechanisms, as well as actually translating things between
    mechanisms.
    '''
    @property
    def uids(self):
        '''
        List of unique IDs in the translator DB.
        '''
        from itertools import chain
        uids = set()
        nul = [ uids.add(i) for i in chain.from_iterable([ mech.idnames for mech in self.mechs.itervalues() ]) ]
        return list(uids)
    def __repr__(self):
        return "DB ({:d} mechs)".format( len(self.mechs.keys()) )
    def list(self):
        '''
        List the full DB (might take a while).
        '''
        def get(mech, id):
            out = []
            specs = mech.getSpeciesForID(id)
            if not specs is None:
                for prefactor, spec in specs:
                    frac  = spec.calcFractionalAmount(id)
                    count = 1
                    anid  = [ x for x in mech.getIDsForSpecies(spec) if x[1] == id ]
                    if len(anid) > 0:
                        aspec = [ x for x in anid[0][1].species if x[1] == spec ]
                        count = aspec[0][0]
                    counts = []
                    nul = [ [ counts.append(y[0]) for y in x[1].species ] for x in spec.ids ]
                    prefactor = count if max(counts) > 1 else frac
                    out.append( ( prefactor, spec.name) )
            return out
        return { id : { mech: get(self.mechs[mech], ID(id)) for mech in self.mechs } for id in self.uids }

    def dump(self, f=sys.stdout):
        '''
        Dump the full DB (might take a while) to <f>. <f> can be a file handle or another connection.
        Defaults to sys.stdout.
        '''
        listing = self.list()
        w = csv.DictWriter(f, [ 'UID' ] + self.mechs.keys() )

        def pprint_field(field):
            out = ''
            if len(field) > 0:
                out = ' + '.join([ '{:>5.2f} {:>5s}'.format(item[0], item[1]) for item in field ])
            return out

        w.writeheader()
        for i, values in listing.iteritems():
            row = { 'UID' : str(i) }
            for mech, value in values.iteritems():
                row[mech] = pprint_field(value)
            w.writerow(row)

    def mergeMechs(self, mechList, mergedName):
        '''
        Merge mechanisms in <mechList> and create a new merged mechanism <mergedName>
        '''
        newMech = Mechanism(mergedName)
        for id in self.uids:
            for name in mechList:
                oldID   = self.mechs[name].findID(id)
                if len(oldID) > 0:
                    oldSpecs = self.mechs[name].getSpeciesForID(oldID[0])
                    for oldSpec in oldSpecs:
                        frac    = oldSpec[1].calcFractionalAmount(oldID[0])
                        count   = oldID[0].calcCount(oldSpec[1])
                        newSpec = Species(oldSpec[1].name)
                        newID   = ID(oldID[0].value)
                        newMech.addItem(newSpec, newID, frac, count)
                    # assumption: first item serves first,don't need the rest
                    break
        self.mechs[mergedName] = newMech
        for name in mechList:
            del self.mechs[name]

    def translate(self, spec, source, target, caseSensitive=True):
        '''
        Translate species <spec> from mechanism <source> to mechanism <target>.
        '''
        if not any( [ x == source for x in self.mechs ] ):
            raise Exception('Source mechanism {:s} does not exists.'.format(source))
        if not any( [ x == target for x in self.mechs ] ):
            raise Exception('Target mechanism {:s} does not exists.'.format(target))

        source_mech = self.mechs[source]
        target_mech = self.mechs[target]

        source_spec = source_mech.findSpecies(spec, caseSensitive=caseSensitive)
        if len(source_spec) == 0:
            raise Exception('Species {:s} does not exist in source mechanism.'.format(spec))

        target_counts = [ ]
        target_specs  = [ ]
        target_fracs  = [ ]
        for id in source_spec[0].ids:
            new_specs      =  target_mech.getSpeciesForID(id[1])
            if not new_specs is None:
                for new_spec in new_specs:
                    target_counts += [ new_spec[0] ]
                    target_specs  += [ new_spec[1] ]
                    target_fracs  += [ new_spec[1].calcFractionalAmount(id[1]) ]

        prefactors    = [ ]
        for i in range(len(target_specs)):
            prefactors += [ target_counts[i] if target_counts[i] > 1 else target_fracs[i] ]

        return TranslationResult(spec, source, target, prefactors, target_specs )

    def _getID(self):
        self.idcount += 1
        return self.idcount
    def listMechs(self):
        '''
        Return a list of mechanism names known to the database.
        '''
        return self.mechs.keys()
    def mechExists(self, name):
        '''
        Does a mechanism name exist in the database?
        '''
        return any( [ x == name for x in self.mechs.keys() ] )
    def addMech(self, mech):
        '''
        Add a mechanism.
        '''
        self.mechs[mech.name] = mech
    def __init__(self):
        self.idcount = 0
        self.mechs = {}
