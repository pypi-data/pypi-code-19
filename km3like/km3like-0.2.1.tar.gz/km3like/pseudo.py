"""Pseudo experiment utils.

Assumes pandas/numpy.
"""
from km3astro.random import random_date, random_azimuth


class ScrambledBootstrap(object):
    """Resample a dataframe's events, and add random azimuth/time.

    ``(energy, zenith) -> (energy, zenith, azimuth, time)``

    Methods
    -------
    sample(n_evts=1000, weights=None)
        Generate random samples

    Examples
    --------
    >>> n_rows = 5
    >>> ingred = pd.DataFrame({
        'zenith': np.random.uniform(high=np.pi, size=n_rows),
        'energy': np.randomuniform(low=1, high=100, size=n_rows),
    })
    >>> scramboot = ScrambledBootstrap(ingred)
    >>> sampled_events = scramboot.sample(100)
    """
    def __init__(self, ingred_df, weight_col=None):
        """
        Parameters
        ----------
        ingred_df : pd.DataFrame-like
            the ingredient dataframe. required to have columns 'zenith'
            and 'energy'
        weight_col: string [default: None]
            Column holding the event weights (if existing).
            Must be specified in order to use weighting in the sampling later!
        """
        self._check_required_columns(ingred_df)
        self.ingred_df = ingred_df
        if weight_col is not None:
            if weight_col not in ingred_df.columns:
                raise KeyError(
                    "Column '{}' not in Dataframe!".format(weight_col))
        self.weight_col = weight_col

    def sample(self, n_evts=1000, weighted=False):
        """
        Parameters
        ----------
        n_evts : integer [default: 1000]
            Number of events to generate
        weighted: bool [default: False]
            Select input events according to their weights?
            Must have specified the weights column to init before!
        """
        wgt = None
        if weighted:
            if self.weight_col is None:
                raise ValueError(
                    'Weight column not specified! Cannot use weights!')
            wgt = self.ingred_df[self.weight_col]

        samp = self.ingred_df.sample(n_evts, weights=wgt, replace=True)
        samp['time'] = random_date(n_evts, astropy_time=False)
        samp['azimuth'] = random_azimuth(n_evts)
        return samp

    def _check_required_columns(self, df):
        required_columns = [
            'zenith',
            'energy',
        ]
        for col in required_columns:
            if col not in df.columns:
                raise KeyError(
                    "Required column '{}' not in dataframe!".format(col))
