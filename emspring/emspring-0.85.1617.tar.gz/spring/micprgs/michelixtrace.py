# Author: Carsten Sachse 27-Oct-2013
# with significant contributions from Stefan Huber (2017) 
# Copyright: EMBL (2010 - 2016)
# License: see license.txt for details
""" 
Program to trace helices from micrographs
"""
from EMAN2 import EMUtil, EMData, EMNumPy, Util, periodogram
from filter import filt_gaussh
from fundamentals import window2d, rot_shift2D
import os
from spring.csinfrastr.csdatabase import SpringDataBase, base
from spring.csinfrastr.csfeatures import Features, FeaturesSupport
from spring.csinfrastr.cslogger import Logger
from spring.csinfrastr.csproductivity import Temporary, OpenMpi, DiagnosticPlot
from spring.csinfrastr.csreadinput import OptHandler
from spring.micprgs.micexam import MicrographExam
from spring.segment2d.segment import Segment
from spring.segment2d.segmentalign2d import SegmentAlign2d
from spring.segment2d.segmentexam import SegmentExam
from utilities import model_blank, image_decimate, model_circle

from scipy import ndimage, stats, signal
from tabulate import tabulate

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np


class MicHelixTracePar(object):
    """
    Class to initiate default dictionary with input parameters including help and range values and 
    status dictionary
    """

    def __init__(self):
        # package/program identity
        self.package = 'emspring'
        self.progname = 'michelixtrace'
        self.proginfo = __doc__
        self.code_files = [self.progname]

        self.mictrace_features = Features()
        self.feature_set = self.mictrace_features.setup(self)

        self.define_parameters_and_their_properties()
        self.define_program_states()

    def define_parameters_and_their_properties(self):
        self.feature_set = self.mictrace_features.set_inp_multiple_micrographs(self.feature_set)
        self.feature_set = self.mictrace_features.set_output_plot_pattern(self.feature_set, self.progname + \
                                                                          '_diag.pdf')

        self.feature_set = self.set_helix_reference(self.feature_set)
        self.feature_set = self.mictrace_features.set_pixelsize(self.feature_set)
        self.feature_set = self.mictrace_features.set_power_tile_size(self.feature_set, size=700)
        self.feature_set = self.mictrace_features.set_tile_overlap(self.feature_set, percent=80)
        self.feature_set = self.mictrace_features.set_binning_option(self.feature_set, default=True)
        self.feature_set = self.mictrace_features.set_binning_factor(self.feature_set, binfactor=8)
        self.feature_set = self.mictrace_features.set_helix_width(self.feature_set)
        self.feature_set = self.set_a_threshold(self.feature_set)
        self.feature_set = self.set_helix_length(self.feature_set)
        self.feature_set = self.set_order_fit(self.feature_set)

        self.feature_set = self.mictrace_features.set_in_or_exclude_curvature_option(self.feature_set)
        self.feature_set = self.mictrace_features.set_in_or_exclude_curvature(self.feature_set)
        self.feature_set = self.mictrace_features.set_persistence_length_cutoff(self.feature_set)

        self.feature_set = self.mictrace_features.set_mpi(self.feature_set)
        self.feature_set = self.mictrace_features.set_ncpus_scan(self.feature_set)
        self.feature_set = self.mictrace_features.set_temppath(self.feature_set)

    def define_program_states(self):
        self.feature_set.program_states['orient_reference_power_with_overlapping_powers'] = 'Find orientations of ' + \
                                                                                            'by matching power spectra.'
        self.feature_set.program_states['find_translations_by_projecting'] = 'Find translations by projecting ' + \
                                                                             'along helix.'
        self.feature_set.program_states[
            'perform_connected_component_analysis_including_hought'] = 'Extract individual helices ' + \
                                                                       'by connected component analysis.'

    def set_helix_reference(self, feature_set):
        inp1 = 'Helix reference'
        feature_set.parameters[inp1] = 'helix_reference.hdf'
        feature_set.properties[inp1] = feature_set.file_properties(1, ['spi', 'hdf', 'img', 'hed'], 'getFile')
        feature_set.hints[inp1] = 'Helix reference: long rectangular straight box of helix to be traced. ' + \
                                  FeaturesSupport().add_accepted_file_formats_to_hint(feature_set, inp1)

        feature_set.level[inp1] = 'beginner'

        return feature_set

    def set_helix_length(self, feature_set):
        inp9 = 'Minimum and maximum helix length'
        feature_set.parameters[inp9] = tuple((700, 1500))
        feature_set.hints[inp9] = 'Sets the minimum and maximum allowed helix length in Angstrom. ' + \
                                  'Too short values can lead to contaminations being recognized as helices ' + \
                                  'Too large values can be too stringent, especially for overlapping or ' + \
                                  'highly bent helices. Longer helices will be split in half. ' + \
                                  'Maximum helix length is recommended to be at least double of minimum helix length. '
        feature_set.properties[inp9] = feature_set.Range(100, 4000, 1)
        feature_set.level[inp9] = 'expert'

        return feature_set

    def set_a_threshold(self, feature_set):
        inp9 = 'Alpha threshold'
        feature_set.parameters[inp9] = float(0.001)
        feature_set.hints[inp9] = 'Cross correlations will be evaluated based on a exponential distribution. ' + \
                                  'p-values above significance threshold alpha will be considered. ' + \
                                  'Increase threshold if helix tracing too promiscuous. Otherwise use with caution.'
        feature_set.properties[inp9] = feature_set.Range(0, 1, 0.00001)
        feature_set.level[inp9] = 'expert'

        return feature_set

    def set_order_fit(self, feature_set):
        inp9 = 'Order fit'
        feature_set.parameters[inp9] = int(2)
        feature_set.hints[inp9] = 'Order of polynomial fit the coordinates of detected helix (1=linear, ' + \
                                  '2=quadratic, 3=cubic ...). Can be used as a further restraint.'
        feature_set.properties[inp9] = feature_set.Range(1, 19, 1)
        feature_set.level[inp9] = 'expert'

        return feature_set


class MicHelixTrace(object):
    """
    * Class that holds functions for examining micrograph quality

    * __init__ Function to read in the entered parameter dictionary and load micrograph

    #. Usage: MicrographExam(pardict)
    #. Input: pardict = OrderedDict of program parameters
    """

    def __init__(self, parset=None):
        self.log = Logger()
        if parset is not None:
            self.feature_set = parset
            p = self.feature_set.parameters

            self.infile = p['Micrographs']
            self.outfile = p['Diagnostic plot pattern']

            self.micrograph_files = Features().convert_list_of_files_from_entry_string(self.infile)
            self.reference_file = p['Helix reference']
            self.helixwidth = p['Estimated helix width in Angstrom']

            self.ori_pixelsize = p['Pixel size in Angstrom']
            self.tile_size_A = p['Tile size power spectrum in Angstrom']
            self.tile_overlap = p['Tile overlap in percent']
            self.binoption = p['Binning option']
            self.binfactor = p['Binning factor']
            if self.binfactor == 1 and self.binoption is True:
                self.binoption = False

            self.a_threshold = p['Alpha threshold']
            self.min_helix_length, self.max_helix_length = p['Minimum and maximum helix length']
            self.order_fit = p['Order fit']

            self.straightness_selection = p['Straightness select option']
            self.straightness_in_or_exclude = p['Include or exclude straight helices']
            self.pers_cutoff = p['Persistence length cutoff in micrometer']

            self.temppath = p['Temporary directory']
            self.mpi_option = p['MPI option']
            self.cpu_count = p['Number of CPUs']

    def delete_gold_particles(self, mic_1d, thr=0.001):
        norm_distribution = stats.norm

        med = np.median(mic_1d)
        mad = np.median(np.absolute(mic_1d - med)) * 1.4826

        p_values = norm_distribution.cdf(mic_1d, med, mad)

        mic_trunc = np.zeros(mic_1d.size)
        mic_trunc[p_values < thr] = 1

        return mic_trunc

    def preprocess_micrograph(self, mic, pixelsize):
        mic = filt_gaussh(mic, 0.02, pad=True)  # This is absolutely necessary. No idea why.
        # Otherwise artefacts
        mic_np = np.copy(EMNumPy.em2numpy(mic))
        size_y = mic_np.shape[0]

        # Highpass Filter
        highpass_length = int(np.around(size_y / 10.))
        mic_np_pad = np.pad(mic_np, highpass_length, 'reflect')
        gaussian_1d = signal.gaussian(size_y, highpass_length)
        gaussian_mask = np.outer(gaussian_1d, gaussian_1d)
        gaussian_mask /= gaussian_mask.sum()
        mic_np_blur = signal.fftconvolve(mic_np_pad, gaussian_mask, mode='same')
        mic_np -= mic_np_blur[highpass_length:mic_np_blur.shape[0] - highpass_length, \
                  highpass_length:mic_np_blur.shape[1] - highpass_length]

        # Gold particles
        mic_1d = mic_np.ravel()
        maskk = self.delete_gold_particles(mic_1d)
        mask = maskk.reshape(mic_np.shape)
        inv_mask = np.invert(mask.astype(dtype=np.bool))

        mic_trunc = mic_np * inv_mask
        mic_trunc = self.mask_micrograph_edges(mic_trunc, pixelsize * 2.0)
        mic_thres = EMNumPy.numpy2em(np.copy(mic_trunc))

        return mic_thres

    def prepare_power_from_reference(self, reference_file):
        reference = EMData()
        reference.read_image(reference_file)
        reference.process_inplace('normalize')

        if self.binoption:
            reference = image_decimate(reference, self.binfactor, fit_to_fft=False)
            pixelsize = self.ori_pixelsize * float(self.binfactor)
        else:
            pixelsize = self.ori_pixelsize

        overlap_percent = 90.0
        step_size = int(reference.get_ysize() * (100.0 - overlap_percent) / 100.0)
        tile_size_pix = int(self.tile_size_A / pixelsize)
        tile_size_pix = Segment().determine_boxsize_closest_to_fast_values(tile_size_pix)
        ref_size = reference.get_ysize()

        if ref_size < tile_size_pix:
            msg = 'Chosen reference size ({0} Angstrom) is smaller than specified '.format(int(ref_size * pixelsize)) + \
                  'tile size of {0} Angstrom. Please increase reference or decrease tile size.'.format(self.tile_size_A)
            raise ValueError(msg)

        y_positions = np.arange(0, reference.get_ysize() - tile_size_pix, step_size)

        if reference.get_xsize() < tile_size_pix:
            reference = Util.pad(reference, tile_size_pix, ref_size, 1, 0, 0, 0, 'average')
        if reference.get_xsize() > tile_size_pix:
            reference = Util.window(reference, tile_size_pix, ref_size, 1, 0, 0, 0)

        if len(y_positions) > 0:
            reference_pw = model_blank(tile_size_pix, tile_size_pix)
            for each_y in y_positions:
                wi_ref = window2d(reference, tile_size_pix, tile_size_pix, 'l', 0, int(each_y))
                reference_pw += periodogram(wi_ref)
        else:
            wi_ref = Util.window(reference, tile_size_pix, tile_size_pix, 1, 0, 0, 0)
            reference_pw = periodogram(wi_ref)

        circle_mask = -1 * model_circle(3, tile_size_pix, tile_size_pix) + 1
        reference_pw *= circle_mask

        ref_profile = SegmentExam().project_helix(reference)

        reference = np.copy(EMNumPy.em2numpy(reference))

        return reference_pw, ref_profile, tile_size_pix, reference

    def compute_step_size(self, tile_size, overlap):
        step = int(tile_size - tile_size * overlap / 100.0)
        return step

    def determine_xy_center_grid(self, tile_size, overlap, x_size, y_size):
        """
        >>> from spring.micprgs.michelixtrace import MicHelixTrace
        >>> MicHelixTrace().determine_xy_center_grid(15, 50, 50, 100)
        array([[(7.0, 7.0), (7.0, 14.0), (7.0, 21.0), (7.0, 28.0), (7.0, 35.0),
                (7.0, 42.0), (7.0, 49.0), (7.0, 56.0), (7.0, 63.0), (7.0, 70.0),
                (7.0, 77.0), (7.0, 84.0), (7.0, 91.0)],
               [(14.0, 7.0), (14.0, 14.0), (14.0, 21.0), (14.0, 28.0),
                (14.0, 35.0), (14.0, 42.0), (14.0, 49.0), (14.0, 56.0),
                (14.0, 63.0), (14.0, 70.0), (14.0, 77.0), (14.0, 84.0),
                (14.0, 91.0)],
               [(21.0, 7.0), (21.0, 14.0), (21.0, 21.0), (21.0, 28.0),
                (21.0, 35.0), (21.0, 42.0), (21.0, 49.0), (21.0, 56.0),
                (21.0, 63.0), (21.0, 70.0), (21.0, 77.0), (21.0, 84.0),
                (21.0, 91.0)],
               [(28.0, 7.0), (28.0, 14.0), (28.0, 21.0), (28.0, 28.0),
                (28.0, 35.0), (28.0, 42.0), (28.0, 49.0), (28.0, 56.0),
                (28.0, 63.0), (28.0, 70.0), (28.0, 77.0), (28.0, 84.0),
                (28.0, 91.0)],
               [(35.0, 7.0), (35.0, 14.0), (35.0, 21.0), (35.0, 28.0),
                (35.0, 35.0), (35.0, 42.0), (35.0, 49.0), (35.0, 56.0),
                (35.0, 63.0), (35.0, 70.0), (35.0, 77.0), (35.0, 84.0),
                (35.0, 91.0)],
               [(42.0, 7.0), (42.0, 14.0), (42.0, 21.0), (42.0, 28.0),
                (42.0, 35.0), (42.0, 42.0), (42.0, 49.0), (42.0, 56.0),
                (42.0, 63.0), (42.0, 70.0), (42.0, 77.0), (42.0, 84.0),
                (42.0, 91.0)]], dtype=object)

        """
        edge_x0 = edge_y0 = tile_size / 2
        edge_x1 = x_size - edge_x0
        edge_y1 = y_size - edge_y0

        step = self.compute_step_size(tile_size, overlap)

        x_array = np.arange(edge_x0, edge_x1, step)
        y_array = np.arange(edge_y0, edge_y1, step)

        xy_center_grid = np.zeros((x_array.size, y_array.size), dtype=tuple)
        for each_x_id, each_x in enumerate(x_array):
            for each_y_id, each_y in enumerate(y_array):
                xy_center_grid[each_x_id][each_y_id] = (np.ceil(each_x), np.ceil(each_y))

        return xy_center_grid

    def generate_stack_of_overlapping_images_powers(self, mic, tile_size, overlap):

        x_size = mic.get_xsize()
        y_size = mic.get_ysize()

        xy_center_grid = self.determine_xy_center_grid(tile_size, overlap, x_size, y_size)

        xy_table = tabulate(xy_center_grid.ravel(), ['x_coordinate', 'y_coordinate'])
        # self.log.ilog('The following x, y coordinates are the centers of the tiles of ' + \
        # 'the binned micrograph:\n{0}'.format(xy_table))

        pw_stack = os.path.join(self.tempdir, 'pw_stack.hdf')
        img_stack = os.path.join(self.tempdir, 'img_stack.hdf')
        circle = -1 * model_circle(3, tile_size, tile_size) + 1
        for each_id, (each_x, each_y) in enumerate(xy_center_grid.ravel()):
            upper_x = each_x - tile_size / 2
            upper_y = each_y - tile_size / 2
            img = window2d(mic, tile_size, tile_size, "l", upper_x, upper_y)
            img = np.copy(EMNumPy.em2numpy(img))
            gaussian_kernel = signal.gaussian(img.shape[0], tile_size / 2.0)
            gaussian_kernel_2d = np.outer(gaussian_kernel, gaussian_kernel)
            img *= gaussian_kernel_2d
            img = EMNumPy.numpy2em(np.copy(img))
            pw = periodogram(img) * circle
            img.write_image(img_stack, each_id)
            pw.write_image(pw_stack, each_id)

        return img_stack, pw_stack, xy_center_grid

    def orient_reference_power_with_overlapping_powers(self, pw_stack, ref_power, xy_center_grid):
        self.log.fcttolog()

        image_dimension = ref_power.get_xsize()
        polar_interpolation_parameters, ring_weights = SegmentAlign2d().prepare_empty_rings(1, image_dimension / 2 - 2,
                                                                                            1)

        cimage = SegmentAlign2d().make_rings_and_prepare_cimage_header(image_dimension, polar_interpolation_parameters,
                                                                       ring_weights, ref_power)

        x_range = y_range = 0.0
        translation_step = 1.0
        shift_x = shift_y = 0
        center_x = center_y = image_dimension / 2 + 1
        full_circle_mode = 'F'
        pw_img_count = EMUtil.get_image_count(pw_stack)

        pw_img = EMData()
        angles = []
        peaks = []
        for each_pw_id in list(range(pw_img_count)):
            pw_img.read_image(pw_stack, each_pw_id)

            [angt, sxst, syst, mirror, xiref, peakt] = Util.multiref_polar_ali_2d(pw_img, [cimage], x_range,
                                                                                  y_range, translation_step,
                                                                                  full_circle_mode,
                                                                                  polar_interpolation_parameters,
                                                                                  center_x + shift_x,
                                                                                  center_y + shift_y)

            angles.append(angt)
            peaks.append(peakt)

        angles = np.array(angles).reshape(xy_center_grid.shape)
        peaks = np.array(peaks).reshape(xy_center_grid.shape)

        angle_table = tabulate(angles)
        peaks_table = tabulate(peaks)

        self.log.ilog('The following angles were assigned to the tiles:\n{0}'.format(angle_table))
        self.log.ilog('The following peaks were found for the tiles:\n{0}'.format(peaks_table))

        return angles, peaks

    def find_translations_by_projecting(self, angles, xy_centers, img_stack, ref, mic, tilesize, overlap_percent):
        self.log.fcttolog()

        image_dimension = ref.shape[1]

        step = self.compute_step_size(tilesize, overlap_percent)

        fl_centers = xy_centers.ravel()
        rhos = np.zeros(fl_centers.shape)
        thetas = np.zeros(fl_centers.shape)
        circle = model_circle(image_dimension / 2, image_dimension, image_dimension)
        cross_corr = []
        for each_id, each_angle in enumerate(angles.ravel()):
            img = EMData()
            img.read_image(img_stack, each_id)
            img = rot_shift2D(circle * img, each_angle)
            img = np.copy(EMNumPy.em2numpy(img))
            # img = np.pad(img, img.shape[0]//2, mode='constant')
            cc_prof_2d = signal.fftconvolve(img, ref, mode='same') / img.size
            gaussian_kernel = signal.gaussian(cc_prof_2d.shape[1], step / 1.0)  # TODO: what value here
            cc_prof_2d *= np.outer(gaussian_kernel, gaussian_kernel)

            max_shift = np.argmax(cc_prof_2d)
            max_shift_y, max_shift_x = np.unravel_index(max_shift, cc_prof_2d.shape)
            cross_corr.append(cc_prof_2d[max_shift_y, max_shift_x])
            max_shift_y -= img.shape[0] / 2.0
            max_shift_x -= img.shape[1] / 2.0
            # self.log.ilog("xshift: %s // yshift: %s" % (max_shift_x, max_shift_y))

            x_coord = fl_centers[each_id][0]
            y_coord = fl_centers[each_id][1]
            rhos[each_id] = x_coord * np.cos(np.deg2rad(each_angle)) + \
                            y_coord * np.sin(np.deg2rad(each_angle)) + max_shift_x
            thetas[each_id] = each_angle

        rhos = rhos.reshape(angles.shape)
        thetas = thetas.reshape(angles.shape)
        cross_corr = np.array(cross_corr).reshape(angles.shape)

        table_rhos = tabulate(rhos)
        table_thetas = tabulate(thetas)
        self.log.ilog('Lines were determined according to equation: rho = x * cos(theta) + y * sin(theta).')
        self.log.ilog('The following rhos were determined:\n{0}'.format(table_rhos))
        self.log.ilog('The following thetas were determined:\n{0}'.format(table_thetas))

        return rhos, thetas, cross_corr

    def perform_thresholding_of_ccmap(self, overlap_cc, a_threshold):
        y_size, x_size = overlap_cc.shape

        #   # Preparation of z-values (CC_values)
        # z_values = np.arctanh(overlap_cc.ravel())
        z_values = overlap_cc.ravel()
        z_values_fitting = overlap_cc[overlap_cc != 0]
        # z_values_fitting = np.sort(z_values_fitting)
        # z_values_fitting = z_values_fitting[0:int(0.999*z_values_fitting.size)]


        #   # Median to estimate lambda
        scale = np.median(z_values_fitting) / np.log(2)
        fitfunction = stats.expon
        params = [0, scale]
        p_values = 1 - fitfunction.cdf(z_values, *params)

        #   # Least squares curve fitting to histogram

        # hist, bin_edges = np.histogram(z_values_fitting, bins=200)
        # hist = hist / float(z_values_fitting.size)
        # bins = (bin_edges[1:]+bin_edges[0:-1])/2.0
        # # bins = bin_edges[0:-1]

        # def exponential(x, form):
        #     return form * np.exp(-form * x)

        # popt, pcov = curve_fit(exponential, bins, hist, p0=0.01)
        # fitfunction = stats.expon
        # params = [0, popt]

        # self.log.ilog("HistVals %s // BinVals %s"%(np.array_str(hist), np.array_str(bins)))
        # self.log.ilog("Fitting parameters are %s"%popt)
        # self.log.ilog("CovarianceMatrix is %s" % np.array_str(pcov))

        # p_values = 1-fitfunction.cdf(z_values, *params)


        #   # Maximum Likelihood Fitting

        # fitfunction = stats.expon #expon
        # params = fitfunction.fit(z_values_fitting, floc=0)
        # p_values = 1-fitfunction.cdf(z_values, *params)



        #   # FDR Procedure

        #   p_ids_sorted = np.argsort(p_values)
        #   sort_p_values = np.sort(p_values)
        #   pixel_count = len(p_values)
        #   ids = np.arange(1, pixel_count + 1)

        #   thres_line = q_threshold * ids / float(pixel_count)
        #   safe_q_threshold = max(0, q_threshold - 0.25)
        #   thres_line[thres_line < safe_q_threshold] = safe_q_threshold

        #   thres_map = np.zeros(pixel_count)
        #   thres_map[p_ids_sorted[sort_p_values <= thres_line]] = 1
        #   thres_map = thres_map.reshape((y_size, x_size))


        #   # Thresholding
        pixel_count = len(p_values)
        thres_map = np.zeros(pixel_count)
        thres_map[p_values <= a_threshold] = 1
        thres_map = thres_map.reshape((y_size, x_size))

        return thres_map, fitfunction, params

    def build_binary_image_of_segmented_helices(self, rhos, thetas, cross_corr, xy_center_grid, mic, tilesize,
                                                overlap_percent):
        x_size, y_size = mic.get_xsize(), mic.get_ysize()
        overlap_cc = np.zeros((y_size, x_size))

        fl_rhos = rhos.ravel()
        fl_thetas = thetas.ravel()
        fl_cc = cross_corr.ravel()

        tiledistance = tilesize * (1 - overlap_percent / 100)

        for each_id, (each_x, each_y) in enumerate(xy_center_grid.ravel()):
            each_fl_cc = fl_cc[each_id]

            lower_x = each_x - tilesize / 2
            upper_x = min(x_size, each_x + tilesize / 2)

            lower_y = each_y - tilesize / 2
            upper_y = min(y_size, each_y + tilesize / 2)

            each_angle = fl_thetas[each_id]

            point_count = tilesize
            if 45 <= each_angle < 135 or 225 <= each_angle < 315:
                xx = np.linspace(lower_x, upper_x, point_count)
                yy = (fl_rhos[each_id] - xx * np.cos(np.deg2rad(each_angle))) / np.sin(np.deg2rad(each_angle))

                yyy = yy[(lower_y <= yy) & (yy < upper_y)]
                xxx = xx[(lower_y <= yy) & (yy < upper_y)]
            else:
                yy = np.linspace(lower_y, upper_y, point_count)
                xx = (fl_rhos[each_id] - yy * np.sin(np.deg2rad(each_angle))) / np.cos(np.deg2rad(each_angle))

                yyy = yy[(lower_x <= xx) & (xx < upper_x)]
                xxx = xx[(lower_x <= xx) & (xx < upper_x)]

            yyy = np.round(yyy).astype(dtype=np.int16)
            xxx = np.round(xxx).astype(dtype=np.int16)
            each_fl_cc_blur = each_fl_cc * signal.gaussian(len(yyy), tiledistance / 2.0)
            for i, (each_xx, each_yy) in enumerate(zip(xxx, yyy)):
                thick = max(1, int(np.around(y_size / 1000.)))  # TODO right thickness when too good grid
                overlap_cc[each_yy - thick:each_yy + 1 + thick, each_xx - thick:each_xx + 1 + thick] += each_fl_cc_blur[
                    i]
                # TODO bug here, gap in line

        overlap_cc = ndimage.median_filter(overlap_cc, 3)
        overlap_count = tilesize / float(self.compute_step_size(tilesize, overlap_percent))
        overlap_cc /= overlap_count * 16.0

        histogram_bin = np.histogram(overlap_cc)
        table_cc = tabulate([np.append('cc_bin', histogram_bin[1]), np.append('pixel_count', histogram_bin[0])])

        cc_summary = tabulate([[np.min(overlap_cc), np.max(overlap_cc), np.average(overlap_cc), np.std(overlap_cc)]],
                              ['min', 'max', 'average', 'stdev'])

        self.log.ilog('The following weighted cross correlations were determined:\n{0}'.format(table_cc))
        self.log.ilog('Cross correlation summary:\n{0}'.format(cc_summary))

        return overlap_cc

    def get_lookup_table_for_bwmorph_thin(self):
        G123_LUT = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1,
                             0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0,
                             1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0,
                             0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1,
                             0, 0, 0], dtype=np.bool)

        G123P_LUT = np.array([0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0,
                              1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0,
                              0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0,
                              1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1,
                              0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                              0, 0, 0], dtype=np.bool)

        return G123_LUT, G123P_LUT

    def bwmorph_thin(self, image, n_iter=None):
        """
        Perform morphological thinning of a binary image
        
        Parameters
        ----------
        image : binary (M, N) ndarray
            The image to be thinned.
        
        n_iter : int, number of iterations, optional
            Regardless of the value of this parameter, the thinned image
            is returned immediately if an iteration produces no change.
            If this parameter is specified it thus sets an upper bound on
            the number of iterations performed.
        
        Returns
        -------
        out : ndarray of bools
            Thinned image.
        
        See also
        --------
        skeletonize
        
        Notes
        -----
        This algorithm [1]_ works by making multiple passes over the image,
        removing pixels matching a set of criteria designed to thin
        connected regions while preserving eight-connected components and
        2 x 2 squares [2]_. In each of the two sub-iterations the algorithm
        correlates the intermediate skeleton image with a neighborhood mask,
        then looks up each neighborhood in a lookup table indicating whether
        the central pixel should be deleted in that sub-iteration.
        
        References
        ----------
        .. [1] Z. Guo and R. W. Hall, "Parallel thinning with
               two-subiteration algorithms," Comm. ACM, vol. 32, no. 3,
               pp. 359-373, 1989.
        .. [2] Lam, L., Seong-Whan Lee, and Ching Y. Suen, "Thinning
               Methodologies-A Comprehensive Survey," IEEE Transactions on
               Pattern Analysis and Machine Intelligence, Vol 14, No. 9,
               September 1992, p. 879
        
        Examples
        --------
        >>> from spring.micprgs.michelixtrace import MicHelixTrace
        >>> m = MicHelixTrace()
        >>> square = np.zeros((7, 7), dtype=np.uint8)
        >>> square[1:-1, 2:-2] = 1
        >>> square[0,1] =  1
        >>> square
        array([[0, 1, 0, 0, 0, 0, 0],
               [0, 0, 1, 1, 1, 0, 0],
               [0, 0, 1, 1, 1, 0, 0],
               [0, 0, 1, 1, 1, 0, 0],
               [0, 0, 1, 1, 1, 0, 0],
               [0, 0, 1, 1, 1, 0, 0],
               [0, 0, 0, 0, 0, 0, 0]], dtype=uint8)
        >>> skel = m.bwmorph_thin(square)
        >>> skel.astype(np.uint8)
        array([[0, 1, 0, 0, 0, 0, 0],
               [0, 0, 1, 0, 0, 0, 0],
               [0, 0, 0, 1, 0, 0, 0],
               [0, 0, 0, 1, 0, 0, 0],
               [0, 0, 0, 1, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0],
               [0, 0, 0, 0, 0, 0, 0]], dtype=uint8)
        """
        # check parameters
        if n_iter is None:
            n = -1
        elif n_iter <= 0:
            raise ValueError('n_iter must be > 0')
        else:
            n = n_iter

        # check that we have a 2d binary image, and convert it
        # to uint8
        skel = np.array(image).astype(np.uint8)

        if skel.ndim != 2:
            raise ValueError('2D array required')
        if not np.all(np.in1d(image.flat, (0, 1))):
            raise ValueError('Image contains values other than 0 and 1')

        # neighborhood mask
        mask = np.array([[8, 4, 2],
                         [16, 0, 1],
                         [32, 64, 128]], dtype=np.uint8)

        # iterate either 1) indefinitely or 2) up to iteration limit
        G123_LUT, G123P_LUT = self.get_lookup_table_for_bwmorph_thin()
        while n != 0:
            before = np.sum(skel)  # count points before thinning

            # for each subiteration
            for lut in [G123_LUT, G123P_LUT]:
                # correlate image with neighborhood mask
                N = ndimage.correlate(skel, mask, mode='constant')
                # take deletion decision from this subiteration's LUT
                D = np.take(lut, N)
                # perform deletion
                skel[D] = 0

            after = np.sum(skel)  # coint points after thinning

            if before == after:
                # iteration had no effect: finish
                break

            # count down to iteration limit (or endlessly negative)
            n -= 1

        return skel.astype(np.bool)

    """
    # here's how to make the LUTs
    def nabe(n):
        return np.array([n>>i&1 for i in range(0,9)]).astype(np.bool)
    def hood(n):
        return np.take(nabe(n), np.array([[3, 2, 1],
                                          [4, 8, 0],
                                          [5, 6, 7]]))
    def G1(n):
        s = 0
        bits = nabe(n)
        for i in (0,2,4,6):
            if not(bits[i]) and (bits[i+1] or bits[(i+2) % 8]):
                s += 1
        return s==1
                
    g1_lut = np.array([G1(n) for n in range(256)])
    def G2(n):
        n1, n2 = 0, 0
        bits = nabe(n)
        for k in (1,3,5,7):
            if bits[k] or bits[k-1]:
                n1 += 1
            if bits[k] or bits[(k+1) % 8]:
                n2 += 1
        return min(n1,n2) in [2,3]
    g2_lut = np.array([G2(n) for n in range(256)])
    g12_lut = g1_lut & g2_lut
    def G3(n):
        bits = nabe(n)
        return not((bits[1] or bits[2] or not(bits[7])) and bits[0])
    def G3p(n):
        bits = nabe(n)
        return not((bits[5] or bits[6] or not(bits[3])) and bits[4])
    g3_lut = np.array([G3(n) for n in range(256)])
    g3p_lut = np.array([G3p(n) for n in range(256)])
    g123_lut  = g12_lut & g3_lut
    g123p_lut = g12_lut & g3p_lut
    """

    def set_up_branch_point_response(self):
        """
        >>> from spring.micprgs.michelixtrace import MicHelixTrace
        >>> m = MicHelixTrace()
        >>> b = m.set_up_branch_point_response() #doctest: +NORMALIZE_WHITESPACE
        >>> assert b == m.get_branch_point_response()
        """
        features = [np.array([[0, 1, 0],
                              [1, 1, 1],
                              [0, 0, 0]]),
                    np.array([[0, 1, 0],
                              [1, 1, 0],
                              [0, 0, 1]]),
                    np.array([[0, 0, 1],
                              [0, 1, 0],
                              [1, 0, 1]]),
                    np.array([[1, 0, 1],
                              [0, 1, 0],
                              [0, 1, 0]]),
                    np.array([[0, 0, 1],
                              [1, 1, 0],
                              [1, 1, 0]]),
                    np.array([[0, 1, 0],
                              [1, 1, 1],
                              [0, 0, 1]]),
                    np.array([[0, 1, 0],
                              [1, 1, 1],
                              [0, 1, 0]])
                    ]

        features = [np.rot90(each_feature, each_rot) for each_feature in features for each_rot in list(range(4))]

        mask = self.get_mask()

        feature_values = list(set([ndimage.correlate(each_feature, mask)[1, 1] for each_feature in features]))
        feature_values.sort()

        return feature_values

    def get_branch_point_response(self):
        return [277, 293, 297, 298, 313, 325, 329, 330, 334, 337, 338, 340, 362, 392, 400, 401, 402, 408, 416, 418, 420,
                422, 423, 424, 482]

    def get_mask(self):
        mask = np.array([[1, 2, 4],
                         [126, 256, 8],
                         [64, 32, 16]])

        return mask

    def get_rid_of_branchpoints_and_crossings(self, thres_map, helix_width):
        skel = self.bwmorph_thin(thres_map)
        #         skel_thick = ndimage.binary_dilation(skel, structure=np.ones((3,3))).astype(skel.dtype)
        #         skel = self.bwmorph_thin(skel_thick)
        #         ax3 = plt.subplot2grid((2, 2), (1,0), rowspan=1, colspan=1)
        #         ax3.imshow(skel, cmap='gray', interpolation='nearest', origin='lower')

        branch_point_response = self.get_branch_point_response()
        mask = self.get_mask()

        N = ndimage.correlate(skel.astype(np.uint16), mask, mode='constant')

        branch_points = np.in1d(N.ravel(), branch_point_response)
        helix_radius = np.ceil(helix_width / 2.0) // 2 * 2 + 1
        dilate_kernel = self.model_circle(helix_radius, helix_radius, 2 * helix_radius, 2 * helix_radius)
        if np.sum(branch_points) > 0:
            branch_points_img = branch_points.reshape((skel.shape))

            branch_points_img = ndimage.binary_dilation(branch_points_img, structure=dilate_kernel)
            skel *= np.invert(branch_points_img)


        #         ax4 = plt.subplot2grid((2, 2), (1,1), rowspan=1, colspan=1)
        #         ax4.imshow(skel, cmap='gray', interpolation='nearest', origin='lower')
        #         plt.show()

        return skel

    def model_circle(self, radius_y, radius_x, ydim, xdim, center_y=None, center_x=None):
        """
        >>> from spring.micprgs.michelixtrace import MicHelixTrace
        >>> m = MicHelixTrace()
        >>> m.model_circle(3, 5, 10, 12)
        array([[ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  0.,  0.],
               [ 0.,  0.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  0.],
               [ 0.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.],
               [ 0.,  0.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  0.],
               [ 0.,  0.,  0.,  1.,  1.,  1.,  1.,  1.,  1.,  1.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  1.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]])
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]])

        >>> m.model_circle(3, 3, 10, 12, -1, 1)
        array([[ 1.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 1.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]])
        """
        if center_y is None:
            center_y = ydim / 2
        if center_x is None:
            center_x = xdim / 2

        y, x = np.ogrid[-center_y:ydim - center_y, -center_x:xdim - center_x]
        mask = (x / float(radius_x)) ** 2 + (y / float(radius_y)) ** 2 <= 1

        circle = np.zeros((ydim, xdim))
        circle[mask] = 1

        return circle

    def model_square(self, length_y, length_x, ydim, xdim, center_y=None, center_x=None):
        """
        >>> from spring.micprgs.michelixtrace import MicHelixTrace
        >>> m = MicHelixTrace()
        >>> m.model_square(6, 3, 10, 12)
        array([[ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]])

        >>> m.model_square(6, 6, 10, 12, -1, 1)
        array([[ 1.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 1.,  1.,  1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.],
               [ 0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.,  0.]])
        """
        if center_y is None:
            center_y = ydim / 2
        if center_x is None:
            center_x = xdim / 2

        h_length_y = length_y / 2.0
        h_length_x = length_x / 2.0

        square = np.zeros((ydim, xdim))
        square[max(0, center_y - h_length_y):min(ydim, center_y + h_length_y),
        max(0, center_x - h_length_x):min(xdim, center_x + h_length_x)] = 1

        return square

    def mask_micrograph_edges(self, mic, pixelsize):
        ydim, xdim = mic.shape
        circle = self.model_circle(1.2 * ydim / 2, 1.2 * xdim / 2, ydim, xdim)
        min_dist_to_edge = np.ceil(0.5 * 25000 * 0.02 / pixelsize)
        circle *= self.model_square(ydim - 2 * min_dist_to_edge, xdim - 2 * min_dist_to_edge, ydim, xdim)
        mic *= circle.astype(mic.dtype)
        return mic

    def fit_and_create_coordinates_according_to_order(self, x, y, order_fit, step_coord):
        x_arg = np.argsort(x)
        x = x[x_arg]
        y = y[x_arg]
        _, uniqidx = np.unique(x, return_index=True)
        x = x[uniqidx]
        y = y[uniqidx]
        fine_x_coord = np.linspace(x[0], x[-1], int((x[-1] - x[0]) / step_coord))
        # fine_x_coord = np.arange(x[0], x[-1], step_coord)
        fitt = np.polyfit(x, y, order_fit)
        fine_y_coord = np.polyval(fitt, fine_x_coord)
        return fine_x_coord, fine_y_coord

    def compute_length_of_fit(self, fine_x_coord, fine_y_coord):
        if len(fine_x_coord) >= 2:
            lengths = np.sqrt((fine_x_coord[:-1] - fine_x_coord[1:]) ** 2 \
                              + (fine_y_coord[:-1] - fine_y_coord[1:]) ** 2)
            cum_length = np.concatenate(([0], np.cumsum(lengths)))
            length = cum_length[-1]
        else:
            cum_length, length = None, 0
        return cum_length, length

    def perform_connected_component_analysis(self, binary, tilesize, pixelsize, order_fit, min_length, max_length):
        label_im, label_count = ndimage.label(binary)

        self.log.ilog("LABEL_IM SHAPE %s x %s" % label_im.shape)

        feature_list = list(range(1, label_count + 1))

        step_coord_A = 70.0
        single_helices = []
        while len(feature_list) > 0:
            each_feature = feature_list[0]
            self.log.ilog("------START NEW HELIX FITTING---------: %s" % each_feature)
            slice_y, slice_x = ndimage.find_objects(label_im == each_feature)[0]
            height = int(slice_y.stop - slice_y.start)
            width = int(slice_x.stop - slice_x.start)

            roi = (label_im == each_feature)
            roi_thin = self.bwmorph_thin(roi)
            y, x = np.where(roi_thin == 1)
            y = y.astype(dtype=np.float64)
            x = x.astype(dtype=np.float64)

            self.log.ilog("PIXELSIZE " + str(pixelsize))
            self.log.ilog("X VALUES" + np.array_str(x))
            self.log.ilog("Y VALUES" + np.array_str(y))

            # For very small particles (e.g.) dirt, fitting below will fail
            if len(x) < 5:
                feature_list.remove(each_feature)
                continue

            # Fit polynomial
            if height >= width:
                fine_y_coord, fine_x_coord = self.fit_and_create_coordinates_according_to_order(y, x, order_fit,
                                                                                                step_coord_A / pixelsize)
            else:
                fine_x_coord, fine_y_coord = self.fit_and_create_coordinates_according_to_order(x, y, order_fit,
                                                                                                step_coord_A / pixelsize)

            # Accurately determine length of fitted polynomial
            cum_length, length = self.compute_length_of_fit(fine_x_coord, fine_y_coord)

            self.log.ilog("FINE X" + np.array_str(fine_x_coord))
            self.log.ilog("FINE Y" + np.array_str(fine_y_coord))
            self.log.ilog("------------- LENGTH: " + str(length))

            n_coords = len(fine_y_coord)

            # Too short helices will be thrown away
            if length <= (min_length / pixelsize):
                feature_list.remove(each_feature)
                self.log.ilog("HELIX %s TOO SHORT" % each_feature)
                continue

            # Too long helices will be split into 2 by determining midpoint and writing two new regions in label_im
            if length > (max_length / pixelsize):
                label_count_roi = 1
                deleter = np.zeros_like(roi)
                midpoint = int((np.abs(cum_length - length / 2.0)).argmin())
                mid_x = fine_x_coord[midpoint]
                mid_y = fine_y_coord[midpoint]
                deleter[mid_y, mid_x] = 1
                counter = 0  # For safety to avoid endless loops
                while label_count_roi < 2 and counter <= 12:
                    roi *= np.invert(deleter)
                    label_im_roi, label_count_roi = ndimage.label(roi)
                    deleter = ndimage.binary_dilation(deleter)
                if counter < 12:
                    # If by cutting, more than 2 parts are produced, look which are the biggest two pieces
                    labels, counts = np.unique(label_im_roi, return_counts=True)
                    biggest_labels = labels[1:][np.argsort(counts[1:])[::-1][0:2]]
                    for label in biggest_labels:
                        new_label = label_im.max() + 1
                        feature_list.append(new_label)
                        label_im[label_im_roi == label] = new_label  # Add cutted helix to label_im
                    feature_list.remove(each_feature)
                    self.log.ilog("HELIX %s SPLIT at POINT %s:%s" % (each_feature, mid_x, mid_y))
                    self.log.ilog("Added helices %s and %s" % (new_label, new_label - 1))
                    continue

            # Appending helix to list
            single_helices.append((fine_x_coord, fine_y_coord))
            self.log.ilog("HELIX %s APPENDED TO RESULT" % each_feature)
            #                 plt.imshow(roi_thin, cmap='gray', origin='lower', interpolation='nearest')
            #                 plt.plot(fine_x_coord / pixelsize, fine_y_coord / pixelsize, 'o')
            #                 plt.show()

            feature_list.remove(each_feature)

        return single_helices

    def filter_according_to_persistence_length(self, helices, pers_lengths, pers_cutoff):
        if self.straightness_in_or_exclude in ['include']:
            filt_helices = [(each_id, helices[each_id]) for each_id, each_pers_length in enumerate(pers_lengths)
                            if each_pers_length > pers_cutoff]
            pers_lengths = pers_lengths[pers_lengths > pers_cutoff]
        if self.straightness_in_or_exclude in ['exclude']:
            filt_helices = [(each_id, helices[each_id]) for each_id, each_pers_length in enumerate(pers_lengths)
                            if each_pers_length <= pers_cutoff]
            pers_lengths = pers_lengths[pers_lengths <= pers_cutoff]

        if len(filt_helices) > 0:
            filt_helix_ids, helices = zip(*filt_helices)
            helix_ids = list(range(len(pers_lengths)))
            excl_helices = set(helix_ids).symmetric_difference(set(filt_helix_ids))

            if len(excl_helices) > 0:
                msg = 'A total of {0} helices were excluded '.format(len(excl_helices)) + \
                      '(helix_ids: {0}) based on the specified '.format(', '.join([str(hel) for hel in excl_helices])) + \
                      'persistence length cutoff {0} micrometers.'.format(pers_cutoff)

                self.log.ilog(msg)

        return helices, pers_lengths

    def compute_persistence_length(self, helices, pixelsize):
        if self.order_fit == 1:
            pers_lengths = [1.0 for x_coord, y_coord in helices]
        elif self.order_fit > 1:
            s = Segment()
            pers_lengths = [1e+6 * s.compute_persistence_length_m_from_coordinates_A(x_coord * pixelsize,
                                                                                     y_coord * pixelsize)
                            for x_coord, y_coord in helices]
            helix_ids = list(range(len(pers_lengths)))
            msg = tabulate(zip(helix_ids, pers_lengths), ['helix', 'persistence length in micrometers'])
            self.log.ilog(msg)

        return np.array(pers_lengths)

    def remove_ticks_and_scale_correctly(self, ax3, mic_np):
        ax3.set_xticks([])
        ax3.set_yticks([])
        ax3.set_xlim([0, mic_np.shape[1]])
        ax3.set_ylim([0, mic_np.shape[0]])

        return ax3

    def visualize_traces_in_diagnostic_plot_verbose(self, infile, outfile, overlap_cc, binary, helices, mic, ref,
                                                    cross_corr,
                                                    combi_score, rho, angles, peaks, xy_center_grid, fitfunct,
                                                    fitparams, skel,
                                                    pers_lengths):
        mic.read_image(infile)
        mic_np = np.copy(EMNumPy.em2numpy(mic))

        michelixtrace_plot = DiagnosticPlot()
        self.fig = michelixtrace_plot.add_header_and_footer(self.feature_set, infile, outfile)

        ax1 = michelixtrace_plot.plt.subplot2grid((2, 5), (0, 0), colspan=1, rowspan=1)  # Overl_CC
        ax2 = michelixtrace_plot.plt.subplot2grid((2, 5), (1, 0), colspan=1, rowspan=1)  # Binary CC
        ax2_hist = michelixtrace_plot.plt.subplot2grid((2, 5), (0, 1), colspan=1, rowspan=1)  # Overl_CC Hist
        ax2_hist_trans = michelixtrace_plot.plt.subplot2grid((2, 5), (1, 1), colspan=1, rowspan=1)  # Overl_CC Hist
        ax3 = michelixtrace_plot.plt.subplot2grid((2, 5), (0, 2), colspan=1, rowspan=1)  # Micrograph with helices
        ax4 = michelixtrace_plot.plt.subplot2grid((2, 5), (1, 2), colspan=1, rowspan=1)  # Reference Helix
        ax5 = michelixtrace_plot.plt.subplot2grid((2, 5), (0, 3), colspan=1, rowspan=1)  # Combi-Score 2DCC+AngleCC
        ax6 = michelixtrace_plot.plt.subplot2grid((2, 5), (1, 3), colspan=1, rowspan=1)  # Reconstruction Vectors
        ax7 = michelixtrace_plot.plt.subplot2grid((2, 5), (0, 4), colspan=1, rowspan=1)  # Helix Angles + AngleCC
        ax8 = michelixtrace_plot.plt.subplot2grid((2, 5), (1, 4), colspan=1, rowspan=1)  # 2DCC

        cc_im = ax1.imshow(overlap_cc, cmap=plt.cm.jet, origin='lower', interpolation='nearest')
        ax1 = self.remove_ticks_and_scale_correctly(ax1, mic_np)
        ax1.set_title('Overlapping Cross Correlation %sx%s' % overlap_cc.shape, fontsize=4)
        cax = self.fig.add_axes([0.005, 0.65, 0.01, 0.20])
        cbar = self.fig.colorbar(cc_im, cax)
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(4)

        ax2.set_title('Thresholded at alpha-value of {0}'.format(self.a_threshold), fontsize=4)
        bin_mask = np.ma.masked_where(binary < 0.5, -1 * binary)
        ax2.imshow(bin_mask, cmap=plt.cm.gray, origin='lower', interpolation='nearest')
        ax2 = self.remove_ticks_and_scale_correctly(ax2, mic_np)
        skel_mask = np.ma.masked_where(skel < 0.5, -1 * skel)
        ax2.imshow(skel_mask, cmap=plt.cm.autumn, origin='lower', interpolation='nearest')

        ax2_hist.set_title('Overlapping Cross Correlation Histogram', fontsize=4)
        ax2_hist.set_yscale('log', basey=10)
        n, bins, patches = ax2_hist.hist(overlap_cc[overlap_cc != 0].flatten(), 100, facecolor='green',
                                         linewidth=0.5, normed=True, log=True)
        ax2_hist.tick_params(axis='both', which='major', labelsize=4)
        x = np.linspace(overlap_cc.min(), overlap_cc.max(), 500)
        ax2_hist.plot(x, fitfunct.pdf(x, *fitparams), color='red')  # 1/float(bins[1]-bins[0]) *
        ax2_hist.set_ylim((10e-4, 1 / float(bins[1] - bins[0])))

        ax2_hist_trans.set_title('Overlapping Cross Correlation Histogram', fontsize=4)
        n, bins, patches = ax2_hist_trans.hist(overlap_cc[overlap_cc != 0].flatten(), 100, facecolor='green',
                                               linewidth=0.5, normed=True)
        ax2_hist_trans.tick_params(axis='both', which='major', labelsize=4)
        x = np.linspace(overlap_cc.min(), overlap_cc.max(), 500)
        ax2_hist_trans.plot(x, fitfunct.pdf(x, *fitparams), color='red')  # 1/float(bins[1]-bins[0]) *
        ax2_hist_trans.set_ylim((0, 1 / float(bins[1] - bins[0]) / 40.))

        ax3.imshow(mic_np, cmap=plt.cm.gray, origin='lower', interpolation='nearest')
        ax3.set_title('Micrograph with detected helices %sx%s' % mic_np.shape, fontsize=4)
        colors = plt.cm.rainbow(np.linspace(0, 1, len(helices)))[:, 0:3] / 2.0
        font = {'weight': 'bold', 'size': 3}
        for pers, c, (each_xcoord, each_ycoord) in zip(pers_lengths, colors, helices):
            ax3.plot(each_xcoord, each_ycoord, 'o', markersize=0.6, alpha=1, markeredgewidth=0.0, color=c)
            c_dark = c / 1.5
            xmean, ymean = each_xcoord.mean(), each_ycoord.mean()
            ax3.text(xmean, (ymean + each_ycoord.max()) / 2.0, "%.1f" % pers, color=c_dark, fontdict=font)

        ax3 = self.remove_ticks_and_scale_correctly(ax3, mic_np)

        ax4.imshow(ref, cmap=plt.cm.gray, origin='lower', interpolation='nearest')
        ax4.set_aspect('equal')
        ax4.set_title('Reference Helix', fontsize=4)
        ax4 = self.remove_ticks_and_scale_correctly(ax4, ref)

        cc_vals = ax5.imshow(combi_score.T, origin='lower', interpolation='nearest')
        ax5.set_title('Combi-Score 2DCC+AngleCC %sx%s' % cross_corr.shape, fontsize=4)
        ax5.set_xticks([])
        ax5.set_yticks([])
        cax = self.fig.add_axes([0.77, 0.65, 0.01, 0.20])
        cbar = self.fig.colorbar(cc_vals, cax)
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(4)

        reconst = ax6.imshow(overlap_cc, cmap=plt.cm.jet, origin='lower',
                             interpolation='nearest')  # extent=[-0.5, n-0.5, -0.5, m-0.5]
        X = np.array([i[0] for i in xy_center_grid.ravel()]).reshape(xy_center_grid.shape)
        Y = np.array([i[1] for i in xy_center_grid.ravel()]).reshape(xy_center_grid.shape)
        transparency = combi_score - combi_score.min()
        transparency = transparency / transparency.max()
        rgba_colors = [(1, 1, 1, a) for a in transparency.flatten()]
        ax6.scatter(X.flatten(), Y.flatten(), color=rgba_colors, s=0.5, linewidth=0)
        a1 = np.cos(np.deg2rad(angles)) * rho - X  # Vector AB from line-defining-point to all matrix points
        a2 = np.sin(np.deg2rad(angles)) * rho - Y  # Vector AB from line-defining-point to all matrix points
        AB = np.dstack([a1, a2])
        line_direction = np.dstack([np.cos(np.deg2rad(angles)), np.sin(np.deg2rad(angles))])
        length = np.einsum('ijk,ijk->ij', line_direction, AB)  # Dot product along last axis
        u = np.cos(np.deg2rad(angles)) * length / float(overlap_cc.shape[1])
        v = np.sin(np.deg2rad(angles)) * length / float(overlap_cc.shape[0])
        angles_plt = ax6.quiver(X, Y, u, v, linewidths=0.1, scale=1.0, alpha=0.5, color='white')
        ax6.set_title('Projection by Rho and Theta %sx%s' % angles.shape, fontsize=4)
        ax6.set_aspect(1.)
        ax6 = self.remove_ticks_and_scale_correctly(ax6, overlap_cc)
        ax6.set_xlim([-1, overlap_cc.shape[1] + 1])
        ax6.set_ylim([-1, overlap_cc.shape[0] + 1])
        cax = self.fig.add_axes([0.77, 0.25, 0.01, 0.20])
        cbar = self.fig.colorbar(reconst, cax)
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(4)

        x, y = np.arange(peaks.shape[0]), np.arange(peaks.shape[1])
        X, Y = np.meshgrid(x, y)
        peaks_plt = ax7.imshow(peaks.T, origin='lower', interpolation='nearest')
        u, v = np.cos(np.deg2rad(angles.T - 90)), np.sin(np.deg2rad(angles.T - 90))
        angles_plt = ax7.quiver(X, Y, u, v, linewidths=0.2, pivot='mid')
        ax7.set_title('Helix Angles and AngleCC-Scores %sx%s' % peaks.shape, fontsize=4)
        ax7.set_xticks([])
        ax7.set_yticks([])
        ax7.set_xlim(-0.5, peaks.shape[0] - 0.5)
        ax7.set_ylim(-0.5, peaks.shape[1] - 0.5)
        cax = self.fig.add_axes([0.971, 0.65, 0.01, 0.20])
        cbar = self.fig.colorbar(peaks_plt, cax)
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(4)

        rho_plot = ax8.imshow(cross_corr.T, origin='lower', interpolation='nearest')
        ax8.set_title('2D Cross-Corr %sx%s' % rho.shape, fontsize=4)
        ax8.set_xticks([])
        ax8.set_yticks([])
        cax = self.fig.add_axes([0.971, 0.25, 0.01, 0.20])
        cbar = self.fig.colorbar(rho_plot, cax)
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(4)

        plt.subplots_adjust(left=0.04, right=0.96, bottom=0.18, top=0.92)

        self.fig.savefig(outfile, dpi=600)

        return outfile

    def visualize_traces_in_diagnostic_plot(self, infile, outfile, overlap_cc, binary, helices, mic, ref, cross_corr,
                                            combi_score, rho, angles, peaks, xy_center_grid, fitfunct, fitparams, skel,
                                            pers_lengths):
        mic.read_image(infile)
        mic_np = np.copy(EMNumPy.em2numpy(mic))
        michelixtrace_plot = DiagnosticPlot()
        self.fig = michelixtrace_plot.add_header_and_footer(self.feature_set, infile, outfile)

        gs = gridspec.GridSpec(2, 4, width_ratios=[1, 1, 1.25, 1.25], height_ratios=[1, 1.7])

        ax1 = self.fig.add_subplot(gs[0, 0])  # Reconstruction
        ax2 = self.fig.add_subplot(gs[1, 1])  # Reference
        ax3 = self.fig.add_subplot(gs[0, 1])  # Thresholded
        ax4 = self.fig.add_subplot(gs[1, 0])  # Histogram
        ax5 = self.fig.add_subplot(gs[:, 2:])  # Micrograph

        reconst = ax1.imshow(overlap_cc, cmap=plt.cm.jet, origin='lower',
                             interpolation='nearest')  # extent=[-0.5, n-0.5, -0.5, m-0.5]
        X = np.array([i[0] for i in xy_center_grid.ravel()]).reshape(xy_center_grid.shape)
        Y = np.array([i[1] for i in xy_center_grid.ravel()]).reshape(xy_center_grid.shape)
        transparency = combi_score - combi_score.min()
        transparency = transparency / transparency.max()
        rgba_colors = [(1, 1, 1, a) for a in transparency.flatten()]
        ax1.scatter(X.flatten(), Y.flatten(), color=rgba_colors, s=0.5, linewidth=0)
        a1 = np.cos(np.deg2rad(angles)) * rho - X  # Vector AB from line-defining-point to all matrix points
        a2 = np.sin(np.deg2rad(angles)) * rho - Y  # Vector AB from line-defining-point to all matrix points
        AB = np.dstack([a1, a2])
        line_direction = np.dstack([np.cos(np.deg2rad(angles)), np.sin(np.deg2rad(angles))])
        length = np.einsum('ijk,ijk->ij', line_direction, AB)  # Dot product along last axis
        u = np.cos(np.deg2rad(angles)) * length / float(overlap_cc.shape[1])
        v = np.sin(np.deg2rad(angles)) * length / float(overlap_cc.shape[0])
        angles_plt = ax1.quiver(X, Y, u, v, linewidths=0.1, scale=1.0, alpha=0.5, color='white')
        ax1.set_title('Projection by Rho and Theta %sx%s' % angles.shape, fontsize=5)
        ax1.set_aspect(1.)
        ax1 = self.remove_ticks_and_scale_correctly(ax1, overlap_cc)
        ax1.set_xlim([-1, overlap_cc.shape[1] + 1])
        ax1.set_ylim([-1, overlap_cc.shape[0] + 1])
        cax = self.fig.add_axes([0.003, 0.695, 0.01, 0.22])
        cbar = self.fig.colorbar(reconst, cax)
        for t in cbar.ax.get_yticklabels():
            t.set_fontsize(4)

        ax2.imshow(ref, cmap=plt.cm.gray, origin='lower', interpolation='nearest')
        ax2.set_aspect('equal')
        ax2.set_title('Reference Helix', fontsize=5)
        ax2 = self.remove_ticks_and_scale_correctly(ax2, ref)

        ax3.set_title('Thresholded at alpha-value of {0}'.format(self.a_threshold), fontsize=5)
        bin_mask = np.ma.masked_where(binary < 0.5, -1 * binary)
        ax3.imshow(bin_mask, cmap=plt.cm.gray, origin='lower', interpolation='nearest')
        ax3 = self.remove_ticks_and_scale_correctly(ax3, mic_np)
        skel_mask = np.ma.masked_where(skel < 0.5, -1 * skel)
        ax3.imshow(skel_mask, cmap=plt.cm.autumn, origin='lower', interpolation='nearest')

        ax4.set_title('Projection Map Histrogram & Thresholding', fontsize=5)
        n, bins, patches = ax4.hist(overlap_cc[overlap_cc != 0].flatten(), 80, facecolor='grey',
                                    linewidth=0.0, normed=True)
        ax4.tick_params(axis='both', which='major', labelsize=4)
        x = np.linspace(overlap_cc.min(), overlap_cc.max(), 500)
        ax4.plot(x, fitfunct.pdf(x, *fitparams), color='red', linewidth=1,
                 label='Exp. Fit')  # 1/float(bins[1]-bins[0]) *
        cutoff = fitfunct.ppf(1 - self.a_threshold, *fitparams)
        ax4.axvline(cutoff, color='green', linewidth=1, label="alpha=%.2e" % self.a_threshold)

        colors_choice = {}
        colors_choice[-1.]='blue'
        colors_choice[1.]='orange'
        for each_d in colors_choice:
            alt_alpha = self.a_threshold * (10.0 ** each_d)
            alt_cutoff = fitfunct.ppf(1 - (alt_alpha), *fitparams)
            ax4.axvline(alt_cutoff, color=colors_choice[each_d], linewidth=0.5, linestyle=':', 
                        label="alpha=%.2e" % alt_alpha)

        ax4.text(1.5 * cutoff, 1 / float(bins[1] - bins[0]) / 20 * 0.9,
                 "cutoff=%.3e\nalpha=%.2e" % (cutoff, self.a_threshold), color='green', fontsize=5)
        ax4.set_ylim((0, 1 / float(bins[1] - bins[0]) / 20.))
        for b, p in zip(bins, patches):
            if b > cutoff:
                plt.setp(p, 'facecolor', 'green')
        legend = ax4.legend(fontsize=5, labelspacing=0.2, loc=7)

        ax5.imshow(mic_np, cmap=plt.cm.gray, origin='lower', interpolation='nearest')
        ax5.set_title('Micrograph with detected helices %sx%s. Numbers denote persistence length in um' % mic_np.shape,
                      fontsize=5)
        colors = plt.cm.hsv(np.linspace(0, 1, len(helices)))[:, 0:3]  # / 1.0
        font = {'weight': 'bold', 'size': 5}
        for pers, c, (each_xcoord, each_ycoord) in zip(pers_lengths, colors, helices):
            ax5.plot(each_xcoord, each_ycoord, 'o', markersize=2, alpha=1, markeredgewidth=0.0, color=c)
            c_dark = c / 5.0
            xmean, ymean = each_xcoord.mean(), each_ycoord.mean()
            ax5.text(xmean, ymean, "%.1f" % pers, color=c_dark, fontdict=font)
        ax5 = self.remove_ticks_and_scale_correctly(ax5, mic_np)

        plt.tight_layout()

        plt.subplots_adjust(left=0.045, right=0.99, bottom=0.21, top=0.93)

        self.fig.savefig(outfile, dpi=600)

    def write_boxfiles(self, helix_info, single_helices, each_mic, tilesize, pixelsize, helixwidth):

        overlap_name = os.path.splitext(os.path.basename(each_mic))[0]
        overlap_dir = os.path.join(os.path.abspath(os.curdir), overlap_name)
        mic_box = overlap_name + os.extsep + 'box'

        if not self.binoption:
            self.binfactor = 1

        s = Segment()
        s.segsizepix = tilesize
        for each_id, (each_xcoord, each_ycoord) in enumerate(single_helices):
            if each_id == 0:
                os.mkdir(overlap_dir)
            xcoord = each_xcoord * self.binfactor
            ycoord = each_ycoord * self.binfactor

            each_box = os.path.join(overlap_dir, overlap_name) + '_{0:03}'.format(each_id) + os.extsep + 'box'
            int_xcoord, int_ycoord, ipangle, curvature = \
                s.interpolate_coordinates(xcoord, ycoord, pixelsize, 70.0, helixwidth,
                                          each_box, new_stepsize=False)

            s.write_boxfile(int_xcoord, int_ycoord, tilesize, mic_box)

            helix_info = s.enter_helixinfo_into_helices_and_write_boxfiles(helix_info, each_mic, overlap_dir, each_box,
                                                                           ipangle, curvature,
                                                                           list(zip(xcoord, ycoord)),
                                                                           list(zip(int_xcoord, int_ycoord)))

        return helix_info

    def trace_helices_in_micrographs(self, micrograph_files, outfiles):
        ref_power, ref_profile, tilesize_pix, ref = self.prepare_power_from_reference(self.reference_file)

        helix_info = []
        for each_id, (each_mic, each_outfile) in enumerate(zip(micrograph_files, outfiles)):
            each_mic, pixelsize, tilesize_bin = MicrographExam().bin_micrograph(each_mic, self.binoption,
                                                                                self.binfactor, self.ori_pixelsize,
                                                                                self.tile_size_A, self.tempdir)

            mic = EMData()
            mic.read_image(each_mic)
            mic.process_inplace('normalize')

            mic = self.preprocess_micrograph(mic, pixelsize)
            mic.process_inplace('normalize')

            img_stack, pw_stack, xy_center_grid = self.generate_stack_of_overlapping_images_powers(mic, tilesize_pix,
                                                                                                   self.tile_overlap)

            angles, peaks = self.orient_reference_power_with_overlapping_powers(pw_stack, ref_power, xy_center_grid)

            rhos, thetas, cross_corr = self.find_translations_by_projecting(angles, xy_center_grid, img_stack,
                                                                            ref, mic, tilesize_pix, self.tile_overlap)

            # Normalise peak (=AngleCC) and cross_corr (=2DCC) within their 5 and 99 percentiles
            np.clip(cross_corr, np.percentile(cross_corr, 5), np.percentile(cross_corr, 99), cross_corr)
            peaks -= np.percentile(peaks, 5)
            peaks /= np.percentile(peaks, 99)
            np.clip(peaks, 0, 1, out=peaks)
            peaks *= cross_corr.max() - cross_corr.min()
            peaks += cross_corr.min()

            # Pointwise Minimum of both scores to be conservative
            combi_score = np.minimum(cross_corr, peaks)

            # Construct CC Image by projecting lines into an image using rho and theta and the combi_score
            overlap_cc = self.build_binary_image_of_segmented_helices(rhos, thetas, combi_score, xy_center_grid,
                                                                      mic, tilesize_pix, self.tile_overlap)

            # Some tweaking of the overlap_cc to get rid of noise
            overlap_cc = ndimage.filters.median_filter(overlap_cc, size=int(np.around(mic.get_xsize() / 200.0)))
            overlap_cc = ndimage.filters.gaussian_filter(overlap_cc, mic.get_xsize() / 500.0)

            # Threshold overlap_cc image
            binary, fitfunct, fitparams = self.perform_thresholding_of_ccmap(overlap_cc, self.a_threshold)

            # Some tweaking of the resulting binary image
            binary_denoised = ndimage.filters.median_filter(binary, size=3)
            smooth = int(np.around((self.helixwidth / pixelsize / 4.0)))
            X, Y = [np.arange(-smooth, smooth + 1)] * 2
            disk_mask = X[:, None] ** 2 + Y ** 2 <= smooth ** 2
            binary_smoothed = ndimage.binary_dilation(binary_denoised,
                                                      structure=disk_mask).astype(binary.dtype)
            skel_thick = self.get_rid_of_branchpoints_and_crossings(binary_smoothed, self.helixwidth / pixelsize)
            skel_thick = self.mask_micrograph_edges(skel_thick, pixelsize)
            skel_thick = ndimage.binary_dilation(skel_thick)

            # Find helices in binary image
            helices = self.perform_connected_component_analysis(skel_thick, tilesize_pix, pixelsize,
                                                                self.order_fit, self.min_helix_length,
                                                                self.max_helix_length)

            pers_lengths = self.compute_persistence_length(helices, pixelsize)
            if self.straightness_selection:
                helices, pers_lengths = self.filter_according_to_persistence_length(helices, pers_lengths,
                                                                                    self.pers_cutoff)

            # self.visualize_traces_in_diagnostic_plot_verbose(each_mic, each_outfile, overlap_cc, binary, helices, mic, ref,
            #                                          cross_corr, combi_score, rhos, angles, peaks, xy_center_grid,
            #                                          fitfunct, fitparams, skel_thick, pers_lengths)

            self.visualize_traces_in_diagnostic_plot(each_mic, each_outfile, overlap_cc, binary, helices, mic, ref,
                                                     cross_corr, combi_score, rhos, angles, peaks, xy_center_grid,
                                                     fitfunct, fitparams, skel_thick, pers_lengths)

            each_mic_name = micrograph_files[each_id]
            helix_info = self.write_boxfiles(helix_info, helices, each_mic_name, tilesize_pix, self.ori_pixelsize,
                                             self.helixwidth)

            os.remove(img_stack)
            os.remove(pw_stack)
            if self.binoption:
                os.remove(each_mic)

        return helix_info

    def enter_helixinfo_into_springdb(self, helix_info):
        s = Segment()
        s.pixelsize = self.ori_pixelsize
        s.stepsize = 70.0
        s.averaging_option = False
        s.ctfcorrect_option = False
        s.segsizepix = self.tile_size_A / self.ori_pixelsize

        session = SpringDataBase().setup_sqlite_db(base)
        session = s.enter_helix_info_into_segments_and_helix_tables(helix_info, session)

    def trace_helices(self):
        if len(self.micrograph_files) < self.cpu_count:
            self.cpu_count = len(self.micrograph_files)
            self.feature_set.parameters['Number of CPUs'] = self.cpu_count
        OpenMpi().setup_and_start_mpi_version_if_demanded(self.mpi_option, self.feature_set, self.cpu_count)
        self.tempdir = Temporary().mktmpdir(self.temppath)

        outfiles = Features().rename_series_of_output_files(self.micrograph_files, self.outfile)

        helix_info = self.trace_helices_in_micrographs(self.micrograph_files, outfiles)

        self.enter_helixinfo_into_springdb(helix_info)

        os.rmdir(self.tempdir)
        self.log.endlog(self.feature_set)


def main():
    # Option handling
    parset = MicHelixTracePar()
    mergeparset = OptHandler(parset)

    ######## Program
    micrograph = MicHelixTrace(mergeparset)
    micrograph.trace_helices()


if __name__ == '__main__':
    main()
