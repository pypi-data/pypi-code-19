from urllib.request import urlopen, HTTPError

from .utils import remove_comments
from .cache import CACHE
from .config import CONFIG, MPLS_TYPES

import json
import matplotlib as mpl
import matplotlib.style
import logging

logger = logging.getLogger(__name__)


def __get(name, stype, **kwargs):
    """

    Parameters
    ----------
    name: str

    stype: str

    kwargs:
    - stylelib_url: str

    - ignore_cache: bool


    Raises
    ------
    FileNotFoundError:
    HTTPError:
    JSONDecodeError:
    """
    data_url = kwargs.get('stylelib_url', CONFIG['stylelib_url']).format(type=stype, name=name)
    ignore_cache = kwargs.get('ignore_cache', False)

    if not ignore_cache and CACHE.is_cached(stype, name):
        with open(CACHE.file_path(stype=stype, name=name), 'r') as f:
            content = remove_comments(f.read())
        logger.debug('loaded raw {} file from cache'.format(stype))
    else:
        try:
            logger.debug('trying urlopen for file {}'.format(data_url))
            with urlopen(data_url) as f:
                # get file content from specified url
                content = remove_comments(f.read().decode())
            logger.debug('loaded raw {} file from URL'.format(stype))
            CACHE.add(stype, name, content)
        except ValueError as e:  # data_url is not a valid url
            logger.debug('urlopen failed: {}'.format(str(e)))
            logger.debug('trying normal open now')
            try:
                with open(data_url) as f:
                    # get file content from file path instead
                    content = remove_comments(f.read())
                logger.debug('loaded raw {} file from disk'.format(stype))
            except IOError:
                raise FileNotFoundError('could not open file {}'.format(data_url))
        except HTTPError:
            raise

    try:
        logger.debug('converting file content to Python dict')
        # convert file content to python dict
        return json.loads(content)
    except json.JSONDecodeError:
        raise


def get(name, stype, **kwargs):
    """

    Parameters
    ----------
    name: str

    stype: str


    Raises
    ------
    ValueError:

    """
    stype = str(stype)

    params = {}
    if stype in MPLS_TYPES:
        params.update(__get(name, stype, **kwargs))
    else:
        raise ValueError('unexpected stype: {}! Must be any of {!r}'.format(stype, MPLS_TYPES))

    # color palette hack
    if params.get('axes.prop_cycle'):
        params['axes.prop_cycle'] = mpl.rcsetup.cycler('color', params['axes.prop_cycle'])

    return params


def rc(context=None, style=None, palette=None, **kwargs):
    params = {}
    if context:
        params.update(get(context, 'context', **kwargs))
    if style:
        params.update(get(style, 'style', **kwargs))
    if palette:
        params.update(get(palette, 'palette', **kwargs))
    return params


def use(*args, context=None, style=None, palette=None, **kwargs):
    """

    Parameters
    ----------
    args:

    context: str or None

    style: str or None

    palette: str or None

    kwargs:
    - reset

    Raises
    ------
    ValueError:

    """
    if kwargs.get('reset', False):
        styles = ['default', ]
    else:
        styles = []

    styles.extend(list(args))
    styles.append(rc(context=context, style=style, palette=palette, **kwargs))
    # apply mpls styles
    return mpl.style.use(styles)


def temp(*args, context=None, style=None, palette=None, **kwargs):
    """

    Parameters
    ----------
    args:

    context: str or None

    style: str or None

    palette: str or None

    kwargs:
    - reset

    Raises
    ------
    ValueError:

    """
    # apply specified matplotlib styles and reset if specified
    styles = list(args)
    styles.append(rc(context=context, style=style, palette=palette, **kwargs))
    return mpl.style.context(styles, after_reset=kwargs.get('reset'))

