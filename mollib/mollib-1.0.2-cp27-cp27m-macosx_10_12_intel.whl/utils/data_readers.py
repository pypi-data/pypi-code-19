"""
Generic data readers utility functions.
"""
from collections import OrderedDict
import re
import logging

from .interactions import validate_label, _re_interaction_str, sort_func


_re_data = re.compile(r'^\s*' +
                      _re_interaction_str +
                      r'\s+'
                      r'(?P<value>[\d\-\+\.]+[eE]?[\d\-\+]*)'
                      r'\s*'
                      r'(?P<error>[\d\-\+\.]*[eE]?[\d\-\+]*)')


def read_data_string(string, one_atom_cls=None, two_atom_cls=None):
    """Read data from a generic data string.

    Parameters
    ----------
    string: str or list of str
        Either a (multiline) string or a list of strings.
    one_atom_cls: suclassed Datum class (:class:`mollib.utils.Datum`), optional
        The class to use for values of single-atom interactions, like '14N'.
    two_atom_cls: suclassed Datum class (:class:`mollib.utils.Datum`), optional
        The class to use for values of two-atom interactions, like '14N-H'


    .. note::

        The format of the file is as follows:

        ::

            # Interaction   Value (Hz)   Error (optional)
            14N-H           -14.5        0.1
            15N-H             3.5
            A.16N-H          -8.5        0.2  # larger error

            A.16H-A.15C       0.5        0.1
            B.16H-B.15C       0.5        0.1

            # Single atom values
            5C                112         1
            6C               -250


    Returns
    -------
    data: dict
        A dict with the data. 
        - **key**: interaction labels (str). ex: '14N-H'
        - **value**: Datum objects (subclasses of :obj:`mollib.utils.Datum`)
    """
    # Convert the string into a list of lines, if it isn't already.
    if not isinstance(string, list):
        string = string.splitlines()

    # Prepare the returned data list
    data = OrderedDict()

    # Find all of the matches and produce a generator
    matches = (m for l in string for m in [_re_data.search(l)] if m)

    # iterate over the matches and pull out the data.
    for match in matches:
        d = match.groupdict()
        logging.debug("read_data_string match: " + str(d))

        interaction_key = validate_label(d['interaction'])
        value = float(d['value'])
        error = float(d['error'] if d['error'] else 0.0)

        # Add the Datum to the data list. If the interaction_label has a '-'
        # character, then it is referring the multiple atoms and must be a
        # residual dipolar coupling (RDC). Otherwise, it's a residual
        # anisotropic chemical shift (RACS).
        hyphen_count = interaction_key.count('-')
        if hyphen_count == 1 and two_atom_cls is not None:
            data[interaction_key] = two_atom_cls(value=value, error=error)
        elif hyphen_count == 0 and one_atom_cls is not None:
            data[interaction_key] = one_atom_cls(value=value, error=error)
        else:
            continue

    return data


def get_error(label, data, settings=None):
    """Return the error for the given datum point.

    Parameters
    ----------
    label: str
        interaction label
    data: dict
        The experimental/observed datum point (:obj:`mollib.utils.Datum`).

        - **key**: interaction labels, str
        - **value**: :obj:`mollib.utils.Datum`
    settings: module or None, optional
        A module with a 'default_error' dict.
        
        - **key**: interaction type
        - **value**: default error (float)

    Returns
    -------
    error: float
        The interaction's error.
    """
    # Use the data point's error, if it's specified. (i.e. it's not None or
    # equal to zero.)
    if (label in data and data[label].error is not None and
                data[label].error != 0.0):
        return data[label].error

    # Otherwise fetch a default value
    interaction_type = sort_func(label)[0]
    if settings is not None and interaction_type in settings.default_error:
        return settings.default_error[interaction_type]

    interaction_type_rev = '-'.join(interaction_type.split('-')[::-1])
    if settings is not None and interaction_type_rev in settings.default_error:
        return settings.default_error[interaction_type_rev]

    # Finally, see if there's a default value for the bond type.
    # The bond_type converts 'CA-CB' into 'C-C'

    if settings is not None and interaction_type:
        bond_type = '-'.join([i[0] for i in interaction_type.split('-')])
        if bond_type in settings.default_error:
            return settings.default_error[bond_type]

    msg = ("The default error for the interaction type '{}' was not "
           "found for '{}'")
    logging.info(msg.format(interaction_type, label))

    return 1.0
