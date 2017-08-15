"""
Calculate statistics between predicted and experimental data.
"""
import copy
from math import sqrt
from collections import OrderedDict

from scipy.stats import linregress

from .data_readers import get_error
from .interactions import sort_func
from .markdown import MDTable


def calc_stats(expt, calc, fit_linear=False, settings=None):
    """Calculate fit statistics between an experimental data set and a
    calculated data set.
    
    Parameters
    ----------
    expt: dict
        A dict with the experimental data. 
        
        - **key**: interaction labels (str). ex: '14N-H'
        - **value**: Datum objects (subclasses of :obj:`mollib.utils.Datum`)
    calc: dict
        A dict with the calculated data.
        
        - **key**: interaction labels (str). ex: '14N-H'
        - **value**: Datum objects (subclasses of :obj:`mollib.utils.Datum`) or
          floats.
    settings: module or None, optional
        A module with a 'default_error' dict. These are used to retrieve default
        errors for experimental measurements, if errors aren't specified.
        
        - **key**: interaction type
        - **value**: default error (float)
    
    Returns
    -------
    stats: :obj:`collections.OrderedDict`
        The calculated statistics (ordered) dict.
        
          - 'chi2': The chi^2 of the fit, float
          - 'rmsd': The root-mean square of the fit, float
          - 'count': The number of interactions fit, int
    
    Examples
    --------
    >>> from mollib.utils.data_types import Datum
    >>> expt = {'1': Datum(value=1.0, error=0.2),
    ...         '2': Datum(value=2.0,),
    ...         '3': Datum(value=3.0, error=1.0),
    ...         }
    >>> calc = {'1': Datum(value=1.1,),
    ...         '2': Datum(value=2.2,),
    ...         '3': Datum(value=3.3),
    ...            }
    >>> stats = calc_stats(expt, calc)
    >>> for k,v in stats.items():
    ...     print(k, "{:.1f}".format(v))
    chi2 0.4
    rmsd 0.3
    count 3.0
    >>> stats = calc_stats(expt, calc)  # conduct a lin. regression before stats
    >>> stats = calc_stats(expt, calc, fit_linear=True)
    >>> for k,v in stats.items():
    ...     print(k, "{:.1f}".format(v))
    chi2 0.0
    rmsd 0.0
    count 3.0
    linear slope 1.1
    linear intercept 0.0
    linear R^2 1.0
    """
    # Initialize parameters
    stats = OrderedDict()
    fit_params = OrderedDict()

    # Conduct the fits, if needed
    if fit_linear:
        # Get the data points
        keys = expt.keys()
        x = [getattr(expt[k], 'value', expt[k]) for k in keys if k in calc]
        y = [getattr(calc[k], 'value', calc[k]) for k in keys if k in calc]

        # Conduct the linear regression
        slope, intercept, r, p, stderr = linregress(x, y)
        fit_params['linear slope'] = slope
        fit_params['linear intercept'] = intercept
        fit_params['linear R^2'] = r ** 2

        # Modify the calculated values.
        for label, datum in calc.items():
            if hasattr(datum, 'value'):
                datum.value -= intercept
                datum.value /= slope
            else:
                datum -= intercept
                datum /= slope
                calc[label] = datum

    # Calculate the stats
    chi2, rss, count = calc_chi2(expt, calc, settings)

    stats['chi2'] = chi2
    if count > 2:
        stats['rmsd'] = sqrt(rss / (count - 1))
    stats['count'] = count

    stats.update(fit_params)

    return stats


def calc_chi2(expt, calc, settings=None):
    """Calculate the chi^2 and residual sum squared between an experimental data
    set and a calculated data set.
    
    Parameters
    ----------
    expt: dict
        A dict with the experimental data. 
        
        - **key**: interaction labels (str). ex: '14N-H'
        - **value**: Datum objects (subclasses of :obj:`mollib.utils.Datum`)
    calc: dict
        A dict with the calculated data.
        
        - **key**: interaction labels (str). ex: '14N-H'
        - **value**: Datum objects (subclasses of :obj:`mollib.utils.Datum`) or
          floats.
    settings: module or None, optional
        A module with a 'default_error' dict. These are used to retrieve default
        errors for experimental measurements, if errors aren't specified. If
        settings aren't specified, the get_error default is 1.0.
        
        - **key**: interaction type
        - **value**: default error (float)
    
    Returns
    -------
    chi2, rss, count: float, float, int
        The residual sum squared and the number of points used in the 
        calculation.
        
        .. math::
        
            \chi^2 = \sum_i \dfrac{(expt(i) - calc(i))^2}{error(i)^2}
            
            rss = \sum_i (expt(i) - calc(i))^2
        
    Examples
    --------
    >>> from mollib.utils.data_types import Datum
    >>> expt = {'1': Datum(value=1.0, error=0.2),
    ...         '2': Datum(value=2.0,),
    ...         '3': Datum(value=3.0, error=1.0),
    ...         }
    >>> calc = {'1': Datum(value=1.1,),
    ...         '2': Datum(value=2.2,),
    ...         '3': Datum(value=3.3),
    ...            }
    >>> chi2, rss, count = calc_chi2(expt, calc)
    >>> print(count)
    3
    >>> print("{:.2f}".format(chi2))
    0.38
    >>> print("{:.2f}".format(rss))
    0.14
    """
    count = 0
    rss = 0.
    chi2 = 0

    for label, value in expt.items():
        if label not in calc:
            continue

        # Get the values
        e_value = getattr(expt[label], 'value', expt[label])
        c_value = getattr(calc[label], 'value', calc[label])

        # Get the errors
        e_error = get_error(label, expt, settings)

        # Calculate the RSS and chi2
        residual_2 = (e_value - c_value) ** 2
        chi2 += residual_2 / e_error ** 2
        rss += residual_2
        count += 1

    return chi2, rss, count


def print_values(expt, calc):
    """Print the experimental and calculated values in a table.
    
    Parameters
    ----------
    expt: dict
        A dict with the experimental data. 
        
        - **key**: interaction labels (str). ex: '14N-H'
        - **value**: Datum objects (subclasses of :obj:`mollib.utils.Datum`)
    calc: dict
        A dict with the calculated data.
        
        - **key**: interaction labels (str). ex: '14N-H'
        - **value**: Datum objects (subclasses of :obj:`mollib.utils.Datum`) or
          floats.
    """
    sorted_keys = sorted(expt.keys(), key=sort_func)

    x = [getattr(expt[k], 'value', expt[k]) for k in sorted_keys if k in calc]
    y = [getattr(calc[k], 'value', calc[k]) for k in sorted_keys if k in calc]

    table = MDTable('expt', 'calc')

    for i,j in zip(x,y):
        table.add_row(i,j)

    print(table.content())
