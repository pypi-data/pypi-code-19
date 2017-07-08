#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for the global co-registration module of AROSICS."""


import unittest
import shutil
import os

# custom
from .cases import test_cases
from arosics import COREG
from geoarray import GeoArray


class COREG_GLOBAL_init(unittest.TestCase):
    """Test case on object initialization of COREG_LOCAL."""

    def setUp(self):
        self.ref_path = test_cases['INTER1']['ref_path']
        self.tgt_path = test_cases['INTER1']['tgt_path']
        self.coreg_kwargs = test_cases['INTER1']['kwargs_global']
        self.coreg_kwargs['wp'] = test_cases['INTER1']['wp_inside']


    def test_coreg_init_from_disk(self):
        self.CRL = COREG(self.ref_path, self.tgt_path, **self.coreg_kwargs)

    def test_coreg_init_from_inMem_GeoArray(self):
        # get GeoArray instances
        self.ref_gA = GeoArray(self.ref_path)
        self.tgt_gA = GeoArray(self.tgt_path)

        # assure the raster data are in-memory
        self.ref_gA.to_mem()
        self.tgt_gA.to_mem()

        # get instance of COREG_LOCAL object
        self.CRL = COREG(self.ref_gA, self.tgt_gA, **self.coreg_kwargs)



class CompleteWorkflow_INTER1_S2A_S2A(unittest.TestCase):
    """Test case for the complete workflow of global co-registration based on two Sentinel-2 datasets, one with
    ~25% cloud cover, the other one without any clouds. The subsets cover the S2A tiles only partly (nodata areas
    are present).
    """

    def setUp(self):
        self.ref_path = test_cases['INTER1']['ref_path']
        self.tgt_path = test_cases['INTER1']['tgt_path']
        self.coreg_kwargs = test_cases['INTER1']['kwargs_global']

    def tearDown(self):
        """Delete output."""
        dir_out = os.path.dirname(self.coreg_kwargs['path_out'])
        if os.path.isdir(dir_out):
            shutil.rmtree(dir_out)

    def test_calculation_of_tie_point_grid(self):
        # get instance of COREG_LOCAL object
        CR = COREG(self.ref_path, self.tgt_path, **self.coreg_kwargs)

        # calculate global X/Y shift
        CR.calculate_spatial_shifts()

        # test shift correction and output writer
        CR.correct_shifts()

        self.assertTrue(os.path.exists(self.coreg_kwargs['path_out']),
                        'Output of global co-registration has not been written.')
