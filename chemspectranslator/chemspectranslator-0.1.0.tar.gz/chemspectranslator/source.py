class Source(object):
    '''
    A Source is a database input method, like a .csv file or a Google Spreadsheet. It can create a
    chemspectranslator DB based on these input methods. This is just the base class that defines
    how fields and items are parsed. It is used by the various subclasses and should not be used
    directly by the user.
    '''
    def parseField(self, txt):
        '''
        Takes a string (a full input text field), breaks it (e.g. ' 3*A +  3 * B') into items
        and removes spaces (e.g. [ '3*A', '3 * B' ] ). Break characters considered are "+" and ";".
        '''
        return [ x.strip() for x in txt.replace(';','+').split('+') ]

    def parseItem(self, txt):
        '''
        Splits item into prefactor, count and species, e.g. '0.4 * TOLUENE' or '3 PAR'.
        '''
        # split prefactor and species (e.g, '0.4 * TOLUENE')
        parts = [ x.strip() for x in txt.split('*') ]
        if len(parts) > 1:
            prefactor = float(parts[0])
            species   = parts[1]
        else:
            prefactor = -1.0
            species   = parts[0]
        # split count and species (e.g, '3 PAR')
        parts = [ x.strip() for x in species.split(' ') ]
        try:
            count = int(parts[0])
            species = ' '.join(parts[1:len(parts)])
        except:
            count = 1
        # remove units at the end
        species = species.split(", ")[0]

        return prefactor, count, species

