import os
import pkg_resources
import csv
try:
    import cPickle as pickle
except:
    import pickle

from . import db
from . import source

class Translator(source.Source, db.DB):
    '''
    A local CSV translator uses a .csv file to create a chemspectranslator DB.
    '''
    def _read(self):
        with open(self.dbFilePath, 'rb') as csvfile:
            nul   = [csvfile.readline() for i in range(self.skipLines) ]
            cols  = [ x.strip() for x in csvfile.readline().replace('\n', '').split(',') ]
            mechs = [ x.strip() for x in csvfile.readline().replace('\n', '').split(',') ]

        nul = [ self.addMech(db.Mechanism(cols[i])) for i in range(len(cols)) if not mechs[i] == '' ]

        id = self._getID()
        with open(self.dbFilePath, 'rb') as csvfile:
            nul = [csvfile.readline() for i in range(self.skipLines+2) ]
            spamreader = csv.DictReader(csvfile, fieldnames=cols)
            for row in spamreader:
                # split line fields into items
                rowproc   = { x : self.parseField(row[x]) for x in row }
                for name, mech in self.mechs.iteritems():
                    for item in rowproc[name]:
                        if len(item) > 0:
                            # separate prefactor from species
                            frac, count, spec = self.parseItem(item)
                            # and add to the mech
                            newSpec = db.Species(spec)
                            newID   = db.ID(id)
                            mech.addItem(newSpec, newID, frac, count)
                id = self._getID()

        assocs = { k: [ cols[i] for i in range(len(cols)) if mechs[i] == k ] for k in mechs }
        for mergeName in assocs:
            if len(mergeName) > 0:
                if len(assocs[mergeName]) > 1:
                    mergeMechs = assocs[mergeName]
                    mergeMechs.sort()
                    self.mergeMechs(mergeMechs, mergeName)

    def _load(self):
        # see if we can write at the cache location
        cacheWritable = os.access(self.dbCachePath, os.W_OK)
        # see if we can read at the cache location
        cacheReadable = os.access(self.dbCachePath, os.R_OK)

        # remove cache if outdated
        if cacheWritable:
            if os.path.getmtime(self.dbFilePath) > os.path.getmtime(self.dbCachePath):
                print('Translator DB newer than cache file, rebuilding...')
                os.remove(self.dbCachePath)

        if cacheReadable:
            with open(self.dbCachePath, 'rb') as f:
                self.mechs = pickle.load(f)
        else:
            self._read()
            try:
                with open(self.dbCachePath, 'wb') as f:
                    pickle.dump(self.mechs, f, pickle.HIGHEST_PROTOCOL)
            except:
                import warnings
                warnings.warn("Caching disabled - {:s} not writeable to user.".format(self.dbCachePath))

    def __init__(self, dbFilePath=pkg_resources.resource_filename(__name__, os.path.join('data','translator_db.csv')), skipLines=2):
        super(Translator, self). __init__()
        self.dbFilePath    = dbFilePath
        self.dbCachePath   = dbFilePath + '.cache'
        self.skipLines     = skipLines
        self._load()
