''' fieldModifiers.py: functions for modifying entries of bibtex databases '''
from .cminfc import warnCm


def doiToLink(entryRef):
    ''' Move the entryRef "doi" field into a properly formatted URL in the "link" field

        Args:
            entryRef (obj): a bib database entry. It will be modified

        Returns:
            (bool): was a DOI found and successfully converted?
    '''
    if 'doi' in entryRef.keys() and len(entryRef['doi']) > 0:
        if entryRef['doi'][0:4] == 'http':
            warnCm('doi field of', entryRef['ID'], 'is a link! Remove the http....org/ part.')
            doiUrl = entryRef['doi']
        else:
            doiUrl = 'http://dx.doi.org/' + entryRef['doi']
        entryRef['link'] = doiUrl
        return True
    else:
        return False


def urlToLink(entryRef):
    ''' Move the entryRef "url" or "link" field into a URL in the "link" field

        Args:
            entryRef (obj): a bib database entry. It will be modified

        Returns:
            (bool): was a URL found and successfully converted?
    '''
    if 'url' in entryRef.keys() and len(entryRef['url']) > 0:
        entryRef['link'] = entryRef['url']
        return True
    elif 'link' in entryRef.keys() and len(entryRef['link']) > 0:
        entryRef['link'] = entryRef['link']
        return True
    else:
        return False
