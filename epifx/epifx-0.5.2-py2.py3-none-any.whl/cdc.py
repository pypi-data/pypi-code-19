from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals

import datetime
import numpy as np
from pypfilt.summary import dtype_date, Table, Monitor
import pypfilt.text

from . import obs


# TODO: add CDC-specific tables here
# [x] percentage-positive in 0.1% bins from 0,0.1 to 13,NA
#     [x] for 1,2,3,4 weeks ahead
#     [x] for season peak
# [x] percentage-positive point estimate
#     [x] for 1,2,3,4 weeks ahead  --> median in forecast
#     [x] for season peak  --> calculate by stepping over intervals
# [x] peak week in weekly bins from 40,41 to 20,21
# [x] peak week point estimate --> calculate by stepping over intervals
# [ ] season onset week in weekly bins from 40,41 to 20,21
#     [ ] defined as exceeding a threshold (PARAMETER)
# [x] season onset week point estimate
#     [x] defined as exceeding a threshold (PARAMETER)
#         --> calculate by stepping over intervals


def add_tables(params, peak_monitor, tbls):
    """Add CDC-specific tables to a list of tables."""
    thresh_monitor = ThresholdMonitor(params['epifx']['cdc_threshold'])
    tbls.extend([
        PeakTimeHist(peak_monitor),
        PeakSizeHist(peak_monitor),
        SizeHist(peak_monitor),
        ThresholdHist(thresh_monitor),
    ])


def start_of_week(year, week):
    # https://wwwn.cdc.gov/nndss/document/MMWR_week_overview.pdf
    # Weeks span Sunday - Saturday.
    # If Jan 1 is a Sun-Wed, the calendar week including Jan 1 is week #1.
    # If Jan 1 is a Thu-Sat, the calendar week including Jan 1 is the
    # final week of the previous year.
    # https://ibis.health.state.nm.us/resource/MMWRWeekCalendar.html
    if week < 1 or week > 53:
        raise ValueError("invalid week: {}".format(week))

    jan1 = datetime.datetime.strptime("{:4d}-01-01".format(year),
                                      "%Y-%m-%d")
    sun1 = datetime.datetime.strptime("{:4d} 1 0".format(year),
                                      "%Y %U %w")
    diff = (sun1 - jan1).days

    if diff == 0:
        # Jan 1 is a Sunday; week 1 includes Jan 1.
        wk1_start = jan1
    elif diff >= 4:
        # Jan 1 is Mon-Wed; week 1 includes Jan 1.
        wk1_start = sun1 - datetime.timedelta(7)
    else:
        # Jan 1 is Thu-Sat; week 1 does not include Jan 1.
        wk1_start = sun1

    # Check that week 1 does not start too early or too late.
    if wk1_start.year < year:
        if wk1_start.month < 12 or wk1_start.day < 29:
            raise ValueError("week 1 of {} starts too early: {}".format(
                year, wk1_start))
    else:
        if wk1_start.month > 1 or wk1_start.day > 4:
            raise ValueError("week 1 of {} starts too late: {}".format(
                year, wk1_start))

    start = wk1_start + (week - 1) * datetime.timedelta(7)
    if week == 53:
        # Check whether this year comprises 53 weeks.
        if start.year > year or (start.month == 12 and start.day > 28):
            raise ValueError("{} does not contain 53 weeks".format(year))

    return start


def end_of_week(year, week):
    return start_of_week(year, week) + datetime.timedelta(6)


def week_bins(year, start_week=40, end_week=20):
    """
    Return a list of tuples ``(week_num, start_date, end_date)``.
    """
    week_num = start_week
    week_begins = start_of_week(year, week_num)
    until = start_of_week(year + 1, end_week)
    delta = datetime.timedelta(days=7)
    bins = []
    while week_begins <= until:
        bins.append((week_num, week_begins, week_begins + delta))
        week_num += 1
        try:
            week_begins = start_of_week(year, week_num)
        except ValueError:
            year = year + 1
            week_num = 1
            week_begins = start_of_week(year, week_num)
    return bins


class PeakTimeHist(Table):
    """
    Record the peak time predictions in weekly bins.

    :param peak_monitor: an instance of :class:`.PeakMonitor`.
    :param name: the name of the table in the output file.
    """

    def __init__(self, peak_monitor, name='cdc_peak_time'):
        Table.__init__(self, name)
        self.__monitor = peak_monitor

    def monitors(self):
        return [self.__monitor]

    def dtype(self, params, obs_list):
        self.__params = params
        self.__all_obs = obs_list
        start_year = min(o['date'] for o in obs_list).year
        self.__bins = week_bins(start_year)
        self.__obs_types = sorted(set((o['unit'], o['period'])
                                      for o in obs_list))
        # Encode units into bytes, for HDF5 storage.
        self.__obs_units = {o['unit']: pypfilt.text.to_bytes(o['unit'])
                            for o in obs_list}
        ulen = max(len(bs) for unit, bs in self.__obs_units.items())
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        fs_date = dtype_date('fs_date')
        week_num = ('week_num', np.int8)
        prob = ('prob', np.float64)
        return [unit, period, fs_date, week_num, prob]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        if forecasting:
            return len(self.__bins) * n_sys
        else:
            return 0

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        pass

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        fs_date_bs = pypfilt.text.to_bytes(fs_date)

        for (u, p) in obs_types:
            u_bs = self.__obs_units[u]
            peak_dates = self.__monitor.peak_date[u, p]
            peak_weights = self.__monitor.peak_weight[u, p]
            for (wk_num, wk_start, wk_end) in self.__bins:
                mask = np.logical_and(peak_dates >= wk_start,
                                      peak_dates < wk_end)
                prob = np.sum(peak_weights[mask])
                row = (u_bs, p, fs_date_bs, wk_num, prob)
                insert_fn(row)


class PeakSizeHist(Table):
    """
    Record the peak size predictions in bins.

    :param peak_monitor: an instance of :class:`.PeakMonitor`.
    :param name: the name of the table in the output file.
    """

    def __init__(self, peak_monitor, name='cdc_peak_size'):
        Table.__init__(self, name)
        self.__monitor = peak_monitor
        self.__bins = [[x / 1000, (x + 1) / 1000] for x in range(131)]
        self.__bins[-1][1] = 1

    def monitors(self):
        return [self.__monitor]

    def dtype(self, params, obs_list):
        self.__params = params
        self.__all_obs = obs_list
        self.__obs_types = sorted(set((o['unit'], o['period'])
                                      for o in obs_list))
        # Encode units into bytes, for HDF5 storage.
        self.__obs_units = {o['unit']: pypfilt.text.to_bytes(o['unit'])
                            for o in obs_list}
        ulen = max(len(bs) for unit, bs in self.__obs_units.items())
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        fs_date = dtype_date('fs_date')
        pcnt_min = ('pcnt_min', np.float64)
        pcnt_max = ('pcnt_max', np.float64)
        prob = ('prob', np.float64)
        return [unit, period, fs_date, pcnt_min, pcnt_max, prob]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        if forecasting:
            return len(self.__bins) * n_sys
        else:
            return 0

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        pass

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        fs_date_bs = pypfilt.text.to_bytes(fs_date)

        for (u, p) in obs_types:
            u_bs = self.__obs_units[u]
            peak_sizes = self.__monitor.peak_size[u, p]
            peak_weights = self.__monitor.peak_weight[u, p]
            for (frac_min, frac_max) in self.__bins:
                mask = np.logical_and(peak_sizes >= frac_min,
                                      peak_sizes < frac_max)
                prob = np.sum(peak_weights[mask])
                row = (u_bs, p, fs_date_bs, frac_min * 100, frac_max * 100,
                       prob)
                insert_fn(row)


class SizeHist(Table):
    """
    Record the predicted size in the next 1-4 weeks in bins.

    :param peak_monitor: an instance of :class:`.PeakMonitor`.
    :param name: the name of the table in the output file.
    """

    def __init__(self, peak_monitor, name='cdc_next_size'):
        Table.__init__(self, name)
        self.__monitor = peak_monitor
        self.__bins = [[x / 1000, (x + 1) / 1000] for x in range(131)]
        self.__bins[-1][1] = 1
        self.__weeks_ahead = 4

    def monitors(self):
        return [self.__monitor]

    def dtype(self, params, obs_list):
        self.__params = params
        self.__all_obs = obs_list
        self.__obs_types = sorted(set((o['unit'], o['period'])
                                      for o in obs_list))
        # Encode units into bytes, for HDF5 storage.
        self.__obs_units = {o['unit']: pypfilt.text.to_bytes(o['unit'])
                            for o in obs_list}
        ulen = max(len(bs) for unit, bs in self.__obs_units.items())
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        fs_date = dtype_date('fs_date')
        ahead = ('weeks_ahead', np.int8)
        pcnt_min = ('pcnt_min', np.float64)
        pcnt_max = ('pcnt_max', np.float64)
        prob = ('prob', np.float64)
        return [unit, period, fs_date, ahead, pcnt_min, pcnt_max, prob]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        if forecasting:
            return len(self.__bins) * n_sys * self.__weeks_ahead
        else:
            return 0

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        exp_obs = self.__monitor.expected_obs
        fs_date_bs = pypfilt.text.to_bytes(fs_date)
        want_dates = [fs_date + datetime.timedelta(days=7 * wk)
                      for wk in [1, 2, 3, 4]]

        for (unit, period) in obs_types:
            exp_sys = exp_obs[(unit, period)]
            unit_bs = self.__obs_units[unit]
            for date, ix, _ in dates:
                if date in want_dates:
                    expect = exp_sys[ix, :]
                    wts = weights[ix, :]
                    ahead = (date - fs_date).days / 7
                    for (frac_min, frac_max) in self.__bins:
                        mask = np.logical_and(expect >= frac_min,
                                              expect < frac_max)
                        prob = np.sum(wts[mask])
                        row = (unit_bs, period, fs_date_bs, ahead,
                               frac_min * 100, frac_max * 100, prob)
                        insert_fn(row)


class ThresholdMonitor(Monitor):
    """Record when expected observations exceed a specific threshold."""

    exceed_date = None
    """
    A dictionary that maps observation systems to the date when each particle
    exceeded the specific threshold: ``exceed_date[(unit, period)]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    exceed_weight = None
    """
    A dictionary that maps observation systems to the weight of each
    particle at the time that it exceeded the threshold:
    ``exceed_weight[(unit, period)]``.

    Note that this is **only** valid for tables to inspect in the
    ``finished()`` method, and **not** in the ``add_rows()`` method.
    """

    def __init__(self, threshold):
        self.__run = None
        self.__threshold = threshold

    def prepare(self, params, obs_list):
        self.__params = params
        self.__obs_types = sorted(set((o['unit'], o['period'])
                                      for o in obs_list))
        self.peak_obs = {u_p: (0, None) for u_p in self.__obs_types}
        for o in obs_list:
            key = (o['unit'], o['period'])
            if o['value'] > self.peak_obs[key][0]:
                self.peak_obs[key] = (o['value'], o['date'])

    def begin_sim(self, start_date, end_date, n_days, n_sys, forecasting):
        if self.__run is None or self.__run != (start_date, end_date):
            # For each particle, record the weight and peak time.
            num_px = self.__params['size']
            self.__run = (start_date, end_date)
            self.exceed_date = {k: np.empty(num_px, dtype='O')
                                for k in self.__obs_types}
            self.exceed_weight = {k: np.zeros(num_px)
                                  for k in self.__obs_types}
            self.prev_obs = {k: np.zeros(num_px)
                             for k in self.__obs_types}
        elif self.__run is not None and self.__run == (start_date, end_date):
            pass
        else:
            self.__run = None
            self.exceed_date = None
            self.exceed_weight = None
            self.prev_obs = None

    def monitor(self, hist, weights, fs_date, dates, obs_types):
        # Do nothing more if there are no dates to summarise.
        num_dates = len(dates)
        if num_dates == 0:
            return

        # Calculate the infection probabilities at every date, for every
        # observation period.
        pr_inf = {}
        pr_inf_fn = self.__params['model'].pr_inf
        periods = set([p for (_, p) in obs_types])

        for p in periods:
            # Calculate the probability of infection over the observation
            # period, and record the current and previous state vectors at
            # each date.
            pr_inf[p] = np.zeros((num_dates, hist.shape[1]))
            curr = np.zeros((num_dates, hist.shape[1], hist.shape[2]))
            prev = np.zeros((num_dates, hist.shape[1], hist.shape[2]))

            for date, ix, hist_ix in dates:
                curr = hist[hist_ix]
                n_back = self.__params['steps_per_day'] * p
                prev = pypfilt.earlier_states(hist, hist_ix, n_back)
                pr_inf = pr_inf_fn(prev, curr)
                # Record the expected observations.
                valid_types = [(u, pd) for (u, pd) in obs_types if p == pd]
                for (u, p) in valid_types:
                    vals = obs.expect(self.__params, u, p, pr_inf, prev, curr)
                    mask = np.logical_and(
                        vals >= self.__threshold,
                        self.prev_obs[u, p] < self.__threshold)
                    self.exceed_date[u, p][mask] = date
                    self.exceed_weight[u, p][mask] = weights[ix, mask]
                self.prev_obs[u, p] = vals


class ThresholdHist(Table):
    """
    Record when the expected observations exceed a specific threshold.

    :param thresh_monitor: an instance of :class:`.ThresholdMonitor`.
    :param name: the name of the table in the output file.
    """

    def __init__(self, thresh_monitor, name='cdc_onset_week'):
        Table.__init__(self, name)
        self.__monitor = thresh_monitor

    def monitors(self):
        return [self.__monitor]

    def dtype(self, params, obs_list):
        self.__params = params
        self.__all_obs = obs_list
        start_year = min(o['date'] for o in obs_list).year
        self.__bins = week_bins(start_year)
        self.__obs_types = sorted(set((o['unit'], o['period'])
                                      for o in obs_list))
        # Encode units into bytes, for HDF5 storage.
        self.__obs_units = {o['unit']: pypfilt.text.to_bytes(o['unit'])
                            for o in obs_list}
        ulen = max(len(bs) for unit, bs in self.__obs_units.items())
        unit = ('unit', 'S{}'.format(ulen))
        period = ('period', np.int8)
        fs_date = dtype_date('fs_date')
        week_num = ('week_num', np.int8)
        prob = ('prob', np.float64)
        return [unit, period, fs_date, week_num, prob]

    def n_rows(self, start_date, end_date, n_days, n_sys, forecasting):
        if forecasting:
            self.__end_date = end_date
            return len(self.__bins) * n_sys
        else:
            self.__end_date = None
            return 0

    def add_rows(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        pass

    def finished(self, hist, weights, fs_date, dates, obs_types, insert_fn):
        fs_date_bs = pypfilt.text.to_bytes(fs_date)
        for (u, p) in obs_types:
            u_bs = self.__obs_units[u]
            dates = self.__monitor.exceed_date[u, p]
            # Dates are None where the threshold was never exceeded.
            none_mask = np.equal(dates, None)
            dates[none_mask] = self.__end_date
            weights = self.__monitor.exceed_weight[u, p]
            for (wk_num, wk_start, wk_end) in self.__bins:
                mask = np.logical_and(dates >= wk_start, dates < wk_end)
                prob = np.sum(weights[mask])
                row = (u_bs, p, fs_date_bs, wk_num, prob)
                insert_fn(row)
