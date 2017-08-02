#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

"""
test_meshtools.py

Unit tests for meshtools
"""

__author__  = 'Paul K. Korir, PhD'
__email__   = 'pkorir@ebi.ac.uk'
__date__    = '2016-06-14'


import sys
import unittest
from math import floor, ceil
from converters.meshtools import get_meshes, cut_meshes, create_rois
from readers.sffreader import get_data, get_aux_data


class TestMeshtools_Mesh(unittest.TestCase):
    """Tests on the Mesh class"""
    def test_mesh_from_meshList_amira_surf(self):
        """Test on converting meshList from Amira .surf to Mesh"""
        desc, seg, col, alp = get_data('sff/sff_data/test_meshList_amira_surf.sff')
        mesh = get_meshes(seg, col, alp, form=desc)[0]
        self.assertTrue(mesh.GetNumberOfPoints() > 0)
        self.assertTrue(mesh.GetNumberOfCells() > 0)
    
    def test_mesh_from_meshList_imod(self):
        """Test on converting meshList from IMOD to Mesh"""
        desc, seg, col, alp = get_data('sff/sff_data/test_meshList_imod.sff')
        mesh = get_meshes(seg, col, alp, form=desc)[0]
        self.assertTrue(mesh.GetNumberOfPoints() > 0)
        self.assertTrue(mesh.GetNumberOfCells() > 0)
    
    def test_mesh_from_contourList(self):
        """Test on converting contourList to Mesh"""
        desc, seg, col, alp = get_data('sff/sff_data/test_contourList.sff')
        mesh = get_meshes(seg, col, alp, form=desc)[0]
        self.assertTrue(mesh.GetNumberOfPoints() > 0)
        self.assertTrue(mesh.GetNumberOfCells() > 0)
    
    def test_mesh_from_shapePrimtiive(self):
        """Test on converting shapePrimitive to Mesh"""
        desc, seg, col, alp = get_aux_data('sff/sff_data/test_shapePrimitive.sff', aux='shapePrimitiveList')
        mesh = get_meshes(seg, col, alp, form=desc)[0]
        self.assertTrue(mesh.GetNumberOfPoints() > 0)
        self.assertTrue(mesh.GetNumberOfCells() > 0)
    

class TestMeshtools_MeshCutter(unittest.TestCase):
    """Tests on the MeshCutter class that produces contours"""
    def test_contours_from_meshList_amira_surf(self):
        """Test that we produce valid contours"""
        # the contours must be
        # - of a certain number
        # - all three orientations
        #
        desc, seg, col, alp = get_data('sff/sff_data/test_meshList_amira_surf.sff')
        meshes = get_meshes(seg, col, alp, form=desc)
        cut_mesh = next(cut_meshes(meshes))
        
        # the number of contours
        x_contour_count = cut_mesh['x'].GetNumberOfPolys()
        y_contour_count = cut_mesh['y'].GetNumberOfPolys()
        z_contour_count = cut_mesh['z'].GetNumberOfPolys()
        
        self.assertEqual(x_contour_count, 515)
        self.assertEqual(y_contour_count, 431)
        self.assertEqual(z_contour_count, 312)
    
    def test_contours_from_meshList_imod(self):
        """Test that we produce valid contours"""
        # the contours must be
        # - of a certain number
        # - all three orientations
        #
        desc, seg, col, alp = get_data('sff/sff_data/test_meshList_imod.sff')
        meshes = get_meshes(seg, col, alp, form=desc)
        cut_mesh = next(cut_meshes(meshes))
        
        # the number of contours
        x_contour_count = cut_mesh['x'].GetNumberOfPolys()
        y_contour_count = cut_mesh['y'].GetNumberOfPolys()
        z_contour_count = cut_mesh['z'].GetNumberOfPolys()
        
        self.assertEqual(x_contour_count, 240)
        self.assertEqual(y_contour_count, 178)
        self.assertEqual(z_contour_count, 47)
    
    def test_contours_from_contourList(self):
        """Test that we produce valid contours"""
        # the contours must be
        # - of a certain number
        # - all three orientations
        #
        desc, seg, col, alp = get_data('sff/sff_data/test_contourList.sff')
        meshes = get_meshes(seg, col, alp, form=desc)
        cut_mesh = next(cut_meshes(meshes)) # get next from generator
        
        # determine mesh bounds
        mesh = meshes[0]
        Xmin, Xmax, Ymin, Ymax, Zmin, Zmax = mesh.GetBounds()
        
        # the number of contours
        x_contour_count = cut_mesh['x'].GetNumberOfPolys()
        y_contour_count = cut_mesh['y'].GetNumberOfPolys()
        z_contour_count = cut_mesh['z'].GetNumberOfPolys()
        
        self.assertEqual(x_contour_count, 89)
        self.assertEqual(y_contour_count, 55)
        self.assertEqual(z_contour_count, 46)
    
    def test_contours_from_shapePrimitive(self):
        """Test that we produce valid contours"""
        # the contours must be
        # - of a certain number
        # - all three orientations
        #
        desc, seg, col, alp = get_aux_data('sff/sff_data/test_shapePrimitive.sff', aux='shapePrimitiveList')
        meshes = get_meshes(seg, col, alp, form=desc)
        cut_mesh = next(cut_meshes(meshes))
        
        # determine mesh bounds
        mesh = meshes[0]
        Xmin, Xmax, Ymin, Ymax, Zmin, Zmax = mesh.GetBounds()
        
        # the number of contours
        x_contour_count = cut_mesh['x'].GetNumberOfPolys()
        y_contour_count = cut_mesh['y'].GetNumberOfPolys()
        z_contour_count = cut_mesh['z'].GetNumberOfPolys()
        
        self.assertTrue(595 <= x_contour_count <= 610)
        self.assertTrue(565 <= y_contour_count <= 590)
        self.assertTrue(500 <= z_contour_count <= 520)


class TestMeshtools_rois(unittest.TestCase):
    """Tests on the create_rois function"""
    def test_create_rois_from_meshList_amira_surf(self):
        """Test that we can populate the ROI object from a Amira .surf meshList"""
        desc, seg, col, alp = get_data('sff/sff_data/test_meshList_amira_surf.sff')
        meshes = get_meshes(seg, col, alp, form=desc)
        roi = create_rois(meshes)
                
        self.assertTrue(hasattr(roi, 'segment'))
        self.assertTrue(hasattr(roi.segment[0], 'colour'))
        self.assertTrue(hasattr(roi.segment[0], 'xContours'))
        self.assertTrue(hasattr(roi.segment[0], 'yContours'))
        self.assertTrue(hasattr(roi.segment[0], 'zContours'))
        self.assertTrue(hasattr(roi.segment[0].xContours, 'contour'))
        self.assertTrue(hasattr(roi.segment[0].yContours, 'contour'))
        self.assertTrue(hasattr(roi.segment[0].zContours, 'contour'))
        self.assertTrue(hasattr(roi.segment[0].xContours.contour[0], 'p'))
        self.assertTrue(hasattr(roi.segment[0].yContours.contour[0], 'p'))
        self.assertTrue(hasattr(roi.segment[0].zContours.contour[0], 'p'))
        map(lambda X: self.assertTrue(hasattr(roi.segment[0].xContours.contour[0].p[0], X)), ['id', 'x', 'y', 'z'])
        map(lambda X: self.assertTrue(hasattr(roi.segment[0].yContours.contour[0].p[0], X)), ['id', 'x', 'y', 'z'])
        map(lambda X: self.assertTrue(hasattr(roi.segment[0].zContours.contour[0].p[0], X)), ['id', 'x', 'y', 'z'])
        self.assertTrue(len(roi.segment[0].xContours.contour[0].p) > 0)
        self.assertTrue(len(roi.segment[0].yContours.contour[0].p) > 0)
        self.assertTrue(len(roi.segment[0].zContours.contour[0].p) > 0)
    
    def test_create_rois_from_meshList_imod(self):
        """Test that we can populate the ROI object from a IMOD meshList"""
        desc, seg, col, alp = get_data('sff/sff_data/test_meshList_imod.sff')
        meshes = get_meshes(seg, col, alp, form=desc)
        roi = create_rois(meshes)
                
        self.assertTrue(hasattr(roi, 'segment'))
        self.assertTrue(hasattr(roi.segment[0], 'colour'))
        self.assertTrue(hasattr(roi.segment[0], 'xContours'))
        self.assertTrue(hasattr(roi.segment[0], 'yContours'))
        self.assertTrue(hasattr(roi.segment[0], 'zContours'))
        self.assertTrue(hasattr(roi.segment[0].xContours, 'contour'))
        self.assertTrue(hasattr(roi.segment[0].yContours, 'contour'))
        self.assertTrue(hasattr(roi.segment[0].zContours, 'contour'))
        self.assertTrue(hasattr(roi.segment[0].xContours.contour[0], 'p'))
        self.assertTrue(hasattr(roi.segment[0].yContours.contour[0], 'p'))
        self.assertTrue(hasattr(roi.segment[0].zContours.contour[0], 'p'))
        map(lambda X: self.assertTrue(hasattr(roi.segment[0].xContours.contour[0].p[0], X)), ['id', 'x', 'y', 'z'])
        map(lambda X: self.assertTrue(hasattr(roi.segment[0].yContours.contour[0].p[0], X)), ['id', 'x', 'y', 'z'])
        map(lambda X: self.assertTrue(hasattr(roi.segment[0].zContours.contour[0].p[0], X)), ['id', 'x', 'y', 'z'])
        self.assertTrue(len(roi.segment[0].xContours.contour[0].p) > 0)
        self.assertTrue(len(roi.segment[0].yContours.contour[0].p) > 0)
        self.assertTrue(len(roi.segment[0].zContours.contour[0].p) > 0)
    
    def test_create_rois_from_contourList(self):
        """Test that we can populate the ROI object from a contourList"""
        desc, seg, col, alp = get_data('sff/sff_data/test_contourList.sff')
        meshes = get_meshes(seg, col, alp, form=desc)
        roi = create_rois(meshes)
        
        self.assertTrue(hasattr(roi, 'segment'))
        self.assertTrue(hasattr(roi.segment[0], 'colour'))
        self.assertTrue(hasattr(roi.segment[0], 'xContours'))
        self.assertTrue(hasattr(roi.segment[0], 'yContours'))
        self.assertTrue(hasattr(roi.segment[0], 'zContours'))
        self.assertTrue(hasattr(roi.segment[0].xContours, 'contour'))
        self.assertTrue(hasattr(roi.segment[0].yContours, 'contour'))
        self.assertTrue(hasattr(roi.segment[0].zContours, 'contour'))
        self.assertTrue(hasattr(roi.segment[0].xContours.contour[0], 'p'))
        self.assertTrue(hasattr(roi.segment[0].yContours.contour[0], 'p'))
        self.assertTrue(hasattr(roi.segment[0].zContours.contour[0], 'p'))
        map(lambda X: self.assertTrue(hasattr(roi.segment[0].xContours.contour[0].p[0], X)), ['id', 'x', 'y', 'z'])
        map(lambda X: self.assertTrue(hasattr(roi.segment[0].yContours.contour[0].p[0], X)), ['id', 'x', 'y', 'z'])
        map(lambda X: self.assertTrue(hasattr(roi.segment[0].zContours.contour[0].p[0], X)), ['id', 'x', 'y', 'z'])
        self.assertTrue(len(roi.segment[0].xContours.contour[0].p) > 0)
        self.assertTrue(len(roi.segment[0].yContours.contour[0].p) > 0)
        self.assertTrue(len(roi.segment[0].zContours.contour[0].p) > 0)
    
    def test_create_rois_from_shapePrimitive(self):
        """Test that we can populate the ROI object from a shapePrimitive"""
        desc, seg, col, alp = get_aux_data('sff/sff_data/test_shapePrimitive.sff', aux='shapePrimitiveList')
        meshes = get_meshes(seg, col, alp, form=desc)
        roi = create_rois(meshes)
                
        self.assertTrue(hasattr(roi, 'segment'))
        self.assertTrue(hasattr(roi.segment[0], 'colour'))
        self.assertTrue(hasattr(roi.segment[0], 'xContours'))
        self.assertTrue(hasattr(roi.segment[0], 'yContours'))
        self.assertTrue(hasattr(roi.segment[0], 'zContours'))
        self.assertTrue(hasattr(roi.segment[0].xContours, 'contour'))
        self.assertTrue(hasattr(roi.segment[0].yContours, 'contour'))
        self.assertTrue(hasattr(roi.segment[0].zContours, 'contour'))
        self.assertTrue(hasattr(roi.segment[0].xContours.contour[0], 'p'))
        self.assertTrue(hasattr(roi.segment[0].yContours.contour[0], 'p'))
        self.assertTrue(hasattr(roi.segment[0].zContours.contour[0], 'p'))
        map(lambda X: self.assertTrue(hasattr(roi.segment[0].xContours.contour[0].p[0], X)), ['id', 'x', 'y', 'z'])
        map(lambda X: self.assertTrue(hasattr(roi.segment[0].yContours.contour[0].p[0], X)), ['id', 'x', 'y', 'z'])
        map(lambda X: self.assertTrue(hasattr(roi.segment[0].zContours.contour[0].p[0], X)), ['id', 'x', 'y', 'z'])
        self.assertTrue(len(roi.segment[0].xContours.contour[0].p) > 0)
        self.assertTrue(len(roi.segment[0].yContours.contour[0].p) > 0)
        self.assertTrue(len(roi.segment[0].zContours.contour[0].p) > 0)
        
        
