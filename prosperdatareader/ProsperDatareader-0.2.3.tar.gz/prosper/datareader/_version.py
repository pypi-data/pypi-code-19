"""_version.py as per: http://stackoverflow.com/a/7071358"""
from codecs import decode
import os
from subprocess import check_output
import warnings

INSTALLED = True
try:    #pragma: no cover
    import semantic_version
except ImportError:
    INSTALLED = False

def get_version():
    """tries to resolve version number

    Returns:
        (str): symantic_version for library

    """
    git_tag = os.environ.get('TRAVIS_TAG')

    version_str = ''
    if git_tag:
        version_str = git_tag
    elif _has_tags():
        version_str = _latest_tag()
        #TODO: dev ++ minor rev
    else:
        warnings.warn('Unable to find tag version', UserWarning)
        version_str = '0.0.1'

    return version_str

def _has_tags():    #pragma: no cover
    """checks if any git tags exist
    source: https://github.com/ccpgames/setuphelpers/blob/master/setuphelpers.py

    """
    try:
        return len(check_output(["git", "tag"]).splitlines()) > 0
    except:
        return False

def _latest_tag(): #pragma: no cover
    """Gets the latest git tag according to PEP440.
    source: https://github.com/ccpgames/setuphelpers/blob/master/setuphelpers.py

    """
    if not INSTALLED:   #pragma: no cover
        warnings.warn('semantic_version not loaded', UserWarning)
        return '0.0.1'

    latest_tag = semantic_version.Version('0.0.0')

    for tag in check_output(['git', 'tag']).splitlines():
        tag_str = decode(tag, 'utf-8').replace('v', '')
        try:
            tag_version = semantic_version.Version(tag_str)
        except Exception:
            continue

        if tag_version > latest_tag:
            latest_tag = tag_version

    return str(latest_tag)

__version__ = get_version()
