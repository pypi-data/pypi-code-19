''' bibreduce.py: Provides entry point cmMain(), and API interface main() '''

import bibtexparser
import argparse

from .cminfc import parseCmArgs, warnCm
from .fieldModifiers import doiToLink, urlToLink


def reduceEntry(e, reduceOptions):
    ''' Do the reducing on the object

        Args:
            e (obj): reference to the bib entry. it will be modified
            reduceOptions (obj): the options for how to process fields
    '''
    if not reduceOptions.abstract:
        e['abstract'] = ''

    if not reduceOptions.title:
        e['title'] = ''

    if not reduceOptions.coauthors:
        authStr = e['author'].replace('\n', ' ')
        authList = authStr.split(' and ')
        if len(authList) == 1:
            e['author'] = authList[0]
        elif len(authList) == 2:
            e['author'] = ' and '.join(authList)
        else:
            e['author'] = authList[0] + ' and others'

    # Link handling
    linkConverters = [urlToLink, doiToLink]
    if reduceOptions.urlLinks:
        pass
    elif reduceOptions.doiLinks:
        linkConverters = linkConverters[::-1]
    else:
        linkConverters = None

    if linkConverters is not None:
        if not linkConverters[0](e):
            if not linkConverters[1](e):
                warnCm('No associated link for', e['ID'])
                e['link'] = ''
    else:
        e['link'] = ''

    if 'url' in e.keys():
        e.pop('url')


def preprocessArgs(nameSpace):
    '''
        Args:
            nameSpace (argparse.Namespace): structure of raw arguments from command line
    '''
    froot, fsuffix = nameSpace.infilename.split('.')
    if fsuffix == 'bib':
        pass
    elif fsuffix == 'aux':  # export the bibliography first
        from shutil import which
        if which('bibexport') is None:
            raise Exception('bibexport is not installed. Cannot process .aux files')

        import os
        exCmdStr = 'bibexport -o ' + froot + '.bib ' + nameSpace.infilename
        print('\n>>>', exCmdStr)
        os.system(exCmdStr)
        print()
        nameSpace.infilename = froot + '.bib'
    else:
        raise Exception('This is not a .bib or .aux file')

    # Default outfile
    if nameSpace.outfilename is None:
        nameSpace.outfilename = froot + '_proc.bib'

    return nameSpace


def main(infilename, outfilename=None,
         title=False,
         coauthors=False,
         doiLinks=False,
         urlLinks=False,
         abstract=False):
    ''' API version of bibreduce

        Args:
            infilename (str)
            outfilename (str, NoneType)
            title (bool): include title in new bibliography
            coauthors (bool): include coauthors in new bibliography
            urlLinks (bool): include urlLinks in new bibliography
            doiLinks (bool): include doiLinks in new bibliography
            abstract (bool): include abstract in new bibliography
    '''
    argStruct = argparse.Namespace()
    argStruct.__dict__.update(locals())
    reduceFromStruct(argStruct)


def cmMain():
    ''' Command line processing version of bibreduce '''
    argStruct = parseCmArgs()
    reduceFromStruct(argStruct)


def reduceFromStruct(argStruct):
    preprocessArgs(argStruct)
    with open(argStruct.infilename) as fx:
        bibdb = bibtexparser.load(fx)
    for e in bibdb.entries:
        reduceEntry(e, argStruct)
    with open(argStruct.outfilename, 'w') as fx:
        bibtexparser.dump(bibdb, fx)



