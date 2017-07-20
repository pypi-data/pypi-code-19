"""
BSD 3-Clause License

Copyright (c) 2017, Gilberto Pastorello
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

pynts.visalization: graphic tools for timeseries data

@author: Gilberto Pastorello
@contact: gzpastorello@lbl.gov
@date: 2017-07-17
"""
import os
import logging
import numpy
import matplotlib
import platform

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib import pyplot, gridspec
from scipy import stats

from pynts import PyntsError

if platform.system() == 'Darwin':
    matplotlib.use('macosx')
matplotlib.rcParams['path.simplify'] = False  # removes smoothing, forces plotting all points

_log = logging.getLogger(__name__)


def plot_comparison(timestamp_list, data1, data2, label1='data1', label2='data2', title='data1 x data2', basename=None, show=True):
    """
    Plot comparison between two datasets with same temporal resolution
    (same number of elements and corresponding timestamps)    
    
    :param timestamp_list: list of timestamps (datetime objects)
    :type timestamp_list: list
    :param data1: data for first data set to be compared
    :type data1: numpy.ndarray
    :param data2: data for second data set to be compared
    :type data2: numpy.ndarray
    :param label1: label for first data set
    :type label1: str
    :param label2: label for second data set
    :type label2: str
    :param title: plot title
    :type title: str
    :param basename: filename (path) to be used to save figure
    :type basename: str
    :param show: flag indicating if interactive plot should be shown
    :type show: bool
    """

    # mask of comparable data points on both datasets
    mask = ~numpy.isnan(data1) & ~numpy.isnan(data2)

    # if nothing to compare, plot is meaningless
    if not numpy.any(mask):
        _log.error("Nothing to plot '{b}', '{l1}', '{l2}'".format(b=basename, l1=label1, l2=label2))
        return

    # main figure setup
    figure = pyplot.figure()
    figure.set_figwidth(16)
    figure.set_figheight(12)
    canvas = FigureCanvasAgg(figure)

    gs = gridspec.GridSpec(18, 3)
    gs.update(left=0.06, right=0.98, top=0.88, bottom=0.05, wspace=0.18, hspace=0.40)

    # main timeseries
    axis_main = pyplot.subplot(gs[0:7, :])
    axis_main.set_title(title, x=0.5, y=1.30)
    p1, = axis_main.plot_date(timestamp_list, data1, linewidth=1.0, linestyle='', marker='.', markersize=3, color='#8080ff', markeredgecolor='#8080ff', alpha=1.0)
    p2, = axis_main.plot_date(timestamp_list, data2, linewidth=1.0, linestyle='', marker='.', markersize=3, color='#ff8080', markeredgecolor='#ff8080', alpha=1.0)
    legend = axis_main.legend([p1, p2], [label1, label2], numpoints=1, markerscale=8.0, fancybox=True)
    legend.get_frame().set_alpha(0.7)
    legend.get_frame().set_edgecolor('none')
    axis_main.xaxis.tick_top()
    for t in axis_main.get_xmajorticklabels():
        t.set(rotation=90)
    props1 = dict(boxstyle='round', facecolor='#d8d8ff', edgecolor='none', alpha=0.7)
    props2 = dict(boxstyle='round', facecolor='#ffe5e5', edgecolor='none', alpha=0.7)
    msg1 = '{v}: $mean={a}$  $median={d}$  $std={s}$  $N={n}$'.format(v=label1, a=numpy.nanmean(data1), d=numpy.nanmedian(data1), s=numpy.nanstd(data1), n=numpy.sum(~numpy.isnan(data1)))
    msg2 = '{v}: $mean={a}$  $median={d}$  $std={s}$  $N={n}$'.format(v=label2, a=numpy.nanmean(data2), d=numpy.nanmedian(data2), s=numpy.nanstd(data2), n=numpy.sum(~numpy.isnan(data2)))
    axis_main.text(0.02, 0.94, msg1, transform=axis_main.transAxes, fontsize=11, fontweight='bold', color='#8080ff', bbox=props1)
    axis_main.text(0.02, 0.86, msg2, transform=axis_main.transAxes, fontsize=11, fontweight='bold', color='#ff8080', bbox=props2)
    tmin, tmax = axis_main.get_xlim()

    # gaps
    axis_avail = pyplot.subplot(gs[7, :])
    xmin, xmax = numpy.nanmin(data1), numpy.nanmax(data1)
    ymin, ymax = numpy.nanmin(data2), numpy.nanmax(data2)
    vmin, vmax = min(xmin, ymin), max(xmax, ymax)
    m1 = numpy.isnan(data1)
    m2 = numpy.isnan(data2)
    axis_avail.vlines(timestamp_list, ymin=m1 * vmin, ymax=m1 * vmax, linewidth=0.1, color='blue', alpha=0.5)
    axis_avail.vlines(timestamp_list, ymin=m2 * vmin, ymax=m2 * vmax, linewidth=0.1, color='red', alpha=0.5)
    axis_avail.set_ylabel('gaps')
    axis_avail.set_ylim(ymin, ymax)
    axis_avail.tick_params(bottom='off', top='off', left='off', right='off', labelleft='off', labelbottom='off')
    if numpy.sum(m1) + numpy.sum(m2) == 0:
        axis_avail.text(0.5, 0.25, 'NO GAPS', transform=axis_avail.transAxes, fontsize=16, color='black')
    axis_avail.set_xlim(tmin, tmax)

    # difference
    axis_diff = pyplot.subplot(gs[8:11, :])
    axis_diff.axhline(linewidth=0.7, linestyle='-', color='black')
    data_zero = numpy.zeros_like(data1)
    data_diff = data1 - data2
    axis_diff.fill_between(timestamp_list, data_zero, data_diff, where=data_diff >= data_zero, color='#8080ff', alpha=1.0)
    axis_diff.fill_between(timestamp_list, data_zero, data_diff, where=data_diff <= data_zero, color='#ff8080', alpha=1.0)
    axis_diff.set_ylabel('difference')
    axis_diff.tick_params(labelbottom='off')
    axis_diff.set_xlim(tmin, tmax)
    yticks = axis_diff.get_yticks().tolist()
    yticks = [abs(i) for i in yticks]
    axis_diff.set_yticklabels(yticks)

    # regression
    gradient, intercept, r_value, p_value, std_err = stats.linregress(data1[mask], data2[mask])
    rsq = r_value * r_value
    ymin_r, ymax_r = (gradient * xmin + intercept, gradient * xmax + intercept)
    diff = (vmax - vmin) * 0.1
    vmin, vmax = vmin - diff, vmax + diff
    axis_regr = pyplot.subplot(gs[11:, 0])
    axis_regr.plot((vmin, vmax), (vmin, vmax), linestyle='-', linewidth=1, marker='', markersize=4, color='black', markeredgecolor='black', alpha=1.0)
    axis_regr.plot(data1, data2, linewidth=1.0, linestyle='', marker='.', markersize=3, color='#559977', markeredgecolor='#559977', alpha=1.0)
    axis_regr.plot((xmin, xmax), (ymin_r, ymax_r), linestyle='-', linewidth=1, marker='', markersize=4, color='red', markeredgecolor='red', alpha=1.0)
    axis_regr.set_xlim(vmin, vmax)
    axis_regr.set_ylim(vmin, vmax)
    axis_regr.set_xlabel(label1)
    axis_regr.set_ylabel(label2)
    axis_regr.text(0.9, 0.96, '1:1', transform=axis_regr.transAxes, fontsize=10, color='black')
    props = dict(boxstyle='round', facecolor='#eae3dd', edgecolor='none', alpha=0.7)
    msgr = '$y={g:.4f}*x {sig} {i:.4f}$\n$r^2={r:.4f}$'.format(r=rsq, g=gradient, i=abs(intercept), sig=('-' if intercept < 0 else '+'))
    axis_regr.text(0.04, 0.88, msgr, transform=axis_regr.transAxes, fontsize=12, color='#997755', bbox=props)

    # histogram (density)
    axis_hist = pyplot.subplot(gs[11:, 1])
    hist_range = [vmin, vmax]
    h1, bins1, patches1 = axis_hist.hist(data1, bins=80, histtype='stepfilled', range=hist_range, normed=True, color='blue', edgecolor='none', alpha=0.5, label=label1)
    h2, bins2, patches2 = axis_hist.hist(data2, bins=80, histtype='stepfilled', range=hist_range, normed=True, color='red', edgecolor='none', alpha=0.5, label=label2)
    axis_hist.set_ylabel('probability density')
    legend = axis_hist.legend(fancybox=True)
    legend.get_frame().set_alpha(0.7)
    legend.get_frame().set_edgecolor('none')
    for leg in legend.legendHandles:
        leg.set_edgecolor('none')

    # histogram (cumulative density)
    axis_cumden = pyplot.subplot(gs[11:, 2])
    hist_range = [vmin, vmax]
    h1, bins1, patches1 = axis_cumden.hist(data1, bins=200, cumulative=True, histtype='stepfilled', range=hist_range, normed=True, color='blue', edgecolor='none', alpha=0.5, label=label1)
    h2, bins2, patches2 = axis_cumden.hist(data2, bins=200, cumulative=True, histtype='stepfilled', range=hist_range, normed=True, color='red', edgecolor='none', alpha=0.5, label=label2)
    axis_cumden.set_ylim(0.0, 1.0)
    axis_cumden.set_ylabel('cumulative probability density')
    legend = axis_cumden.legend(loc='lower right', fancybox=True)
    legend.get_frame().set_alpha(0.7)
    legend.get_frame().set_edgecolor('none')
    for leg in legend.legendHandles:
        leg.set_edgecolor('none')

    # save figure
    if basename:
        if ('{l1}' in basename) and ('{l2}' in basename):
            figure_filename = os.path.abspath((basename + '.png').format(l1=label1, l2=label2))
        else:
            figure_filename = os.path.abspath('{b}__{l1}_{l2}.png'.format(b=basename, l1=label1, l2=label2))
        canvas.print_figure(figure_filename, dpi=100)
        _log.info("Saved '{f}'".format(f=figure_filename))

    # show interactive figure
    if show:
        pyplot.show()

    pyplot.close(figure)


if __name__ == '__main__':
    raise PyntsError('Not executable')
