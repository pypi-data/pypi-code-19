#!/usr/bin/env python
"""
Test module to check segrefine3dplot
"""
from EMAN2 import EMData
from filter import filt_table
import os
from projection import prj
from spring.csinfrastr.csdatabase import SpringDataBase, refine_base, RefinementCycleTable
from spring.csinfrastr.csproductivity import TestingDirectory
from spring.segment2d.segmentalign2d import SegmentAlign2d
from spring.segment3d.refine.sr3d_main import SegmentRefine3d
from spring.segment3d.segrefine3dinspect import SegRefine3dInspect, SegRefine3dInspectPar
from spring.segment3d.segrefine3dinspect_gui import SegRefine3dInspectCommonOperations
from spring.tests.csinfrastr.test_csreadinput import EndToEndTest
from spring.tests.segment3d.test_segclassreconstruct import TestSegClassReconstructPreparation
from utilities import model_gauss_noise


class TestSegRefine3dInspectPrepare(object):

    def simulate_fsc_line(self):
        ff = SegmentAlign2d().prepare_filter_function(False, 0.02, True, 0.08, self.pixelsize, self.segment_size)
        return ff

    def setup_segrefine3dinspect(self):
        if self.high_res_test:
            scale_factor = 2.0
            self.pixelsize /= scale_factor
            self.segment_size *= int(scale_factor)

        helix_volume = TestSegClassReconstructPreparation().generate_helical_volume(self.size_of_subunit_in_angstrom,
        self.pixelsize, self.segment_size, self.helix_radius_in_angstrom, self.helical_rise, self.helical_rotation)
        
        res_cutoff= 2 * self.pixelsize

        filter_coefficients = SegmentAlign2d().prepare_bfactor_coefficients(self.test_bfactor, self.pixelsize,
        self.segment_size, res_cutoff)
        
        helix_volume = filt_table(helix_volume, filter_coefficients.tolist())

        noise = model_gauss_noise(0.001, self.segment_size, self.segment_size, self.segment_size)
        helix_volume += noise
        helix_volume.write_image(self.helix_volume)

        ff = self.simulate_fsc_line()
        f_nt = SegmentRefine3d().make_fsc_line_named_tuple()

        self.test_fsc_file = SegmentRefine3d().write_out_fsc_line(f_nt(ff, ff, len(ff) * [None], len(ff) * [None]), 
        self.pixelsize, 'test_fsc.dat', 3)


class TestSegRefine3dInspect(TestSegRefine3dInspectPrepare, SegRefine3dInspect):
    def setup(self):
        self.testingdir = TestingDirectory(os.path.splitext(os.path.basename(__file__))[0])
        self.testingdir.create()

        self.helix_volume = 'helix_volume.hdf'
        self.processed_volume = 'test_processed_vol.hdf'
        self.size_of_subunit_in_angstrom = 50
        self.pixelsize = 5.0
        self.segment_size = 50
        self.helix_radius_in_angstrom = 70
        self.helical_rise = 10.0
        self.helical_rotation = 50.0
        self.test_bfactor = 300.0
        self.high_res_test = True
        self.setup_segrefine3dinspect()
        
        self.feature_set = SegRefine3dInspectPar()
        self.feature_set.parameters['Volume reconstruction']=self.helix_volume
        self.feature_set.parameters['Batch mode']=True#False#
        self.feature_set.parameters['Output volume name']= self.processed_volume
        
        self.feature_set.parameters['B-factor']=True
        self.feature_set.parameters['B-factor and resolution cutoff']=((-self.test_bfactor, 2.5 * self.pixelsize))
        self.feature_set.parameters['Signal-to-noise weighting']=True
        self.feature_set.parameters['FSC curve']=self.test_fsc_file
        self.feature_set.parameters['Pixel size in Angstrom']=self.pixelsize
        self.feature_set.parameters['Estimated helix inner and outer diameter in Angstrom']=((50, 200))
        self.feature_set.parameters['Real-space mask']=True
        self.feature_set.parameters['Mask type']='cylinder'
        self.feature_set.parameters['Layer-line Fourier filter']=True
        self.feature_set.parameters['Helical rise/rotation or pitch/number of units per turn choice']='rise/rotation'
        
        self.feature_set.parameters['Helical symmetry in Angstrom or degrees']=((self.helical_rise,
        self.helical_rotation))
        
        self.feature_set.parameters['Rotational symmetry']=1
        self.feature_set.parameters['Helix polarity']='apolar'
        
        self.feature_set.parameters['Long helix']=False
        self.feature_set.parameters['Helix length in Angstrom']=500
        self.feature_set.parameters['Swap handedness']=True
        
        super(TestSegRefine3dInspect, self).__init__(self.feature_set)
        
        
    def teardown(self):
        os.remove(self.helix_volume)
        os.remove(self.test_fsc_file)
        if self.batch_mode:
            os.remove(self.processed_volume)
        
        self.testingdir.remove()
        

class TestSegRefine3dInspectMain(TestSegRefine3dInspect):
    def do_test_case_sr3di1(self):
        self.launch_inspection_of_reconstruction()
        
        projection_parameters = [[0., 90., 270., 0., 0.]]
        if self.batch_mode:
            vol = EMData()
            vol.read_image(self.helix_volume)
            prj(vol, projection_parameters, self.helix_volume)
            vol.read_image(self.processed_volume)
            prj(vol, projection_parameters, self.processed_volume)


class TestSegRefine3dInspectMore(TestSegRefine3dInspect):

    def setup_fsc_in_refinement_db(self):
        ff = self.simulate_fsc_line()
        fsc_file = os.path.splitext(self.test_fsc_file)[0] + os.extsep + 'db'
        self.feature_set.parameters['FSC curve'] = fsc_file
        ref_session = SpringDataBase().setup_sqlite_db(refine_base, fsc_file)
        ref_cycle = RefinementCycleTable()
        ref_cycle.fsc = list(ff)
        ref_session.add(ref_cycle)
        ref_session.commit()
        
        return fsc_file


    def do_test_case_sr3di2(self):
        """
        * Segrefine3dinspect: Test structure mask and long helix option including db fsc read
        """
        fsc_file = self.setup_fsc_in_refinement_db()

        self.feature_set.parameters['Mask type']='structure'
        self.feature_set.parameters['Long helix']=True
        super(TestSegRefine3dInspect, self).__init__(self.feature_set)

        self.launch_inspection_of_reconstruction()
        
        os.remove(fsc_file)
        
        
    def do_test_case_sr3di3(self):
        """
        * Segrefine3dinspect: No real-space mask chosen 
        """
        self.feature_set.parameters['Real-space mask']=False
        self.feature_set.parameters['Long helix']=True
        super(TestSegRefine3dInspect, self).__init__(self.feature_set)
         
        self.launch_inspection_of_reconstruction()
         
    def do_test_case_sr3di4(self):
        """
        * Segrefine3dinspect: Swap handedness without Layer-line Fourier filter
        """
        self.feature_set.parameters['Layer-line Fourier filter']=False
        self.feature_set.parameters['Swap handedness']=True
         
        super(TestSegRefine3dInspect, self).__init__(self.feature_set)
     
        self.launch_inspection_of_reconstruction()

        
    def do_test_case_sr3di5(self):
        """
        * Segrefine3dinspect: Work with higher resolution volumes to fit B-factor
        """
        self.high_res_test = True
        super(TestSegRefine3dInspect, self).__init__(self.feature_set)
     
        self.launch_inspection_of_reconstruction()


    def do_test_case_sr3di6(self):
        """
        * Segrefine3dinspect: Work with input of long volumes and pad to square 
        """

        super(TestSegRefine3dInspect, self).__init__(self.feature_set)

        vol = EMData()
        vol.read_image(self.helix_volume)
        vol = SegRefine3dInspectCommonOperations().prepare_long_helix(vol, self.helix_length, self.helixwidth,
        self.pixelsize, self.helical_symmetry, self.rotational_symmetry, self.polar_helix)
        
        vol.write_image(self.helix_volume)
        self.launch_inspection_of_reconstruction()
     

class TestSegRefine3dInspectEndToEnd(TestSegRefine3dInspect):
    def do_end_to_end_test_sp_inputfile(self):
        EndToEndTest().do_end_to_end_inputfile(self.feature_set)
 

    def do_end_to_end_test_sp_prompt(self):
        EndToEndTest().do_end_to_end_prompt(self.feature_set)
        
    
def main():
    tsr3dp = TestSegRefine3dInspectMain()
    tsr3dp.setup()
    tsr3dp.do_test_case_sr3di1()
        
if __name__ == '__main__':
    main()
