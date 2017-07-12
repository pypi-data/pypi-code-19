# Author: Carsten Sachse 03-Nov-2013
# Copyright: EMBL (2010 - 2016)
# License: see license.txt for details

from spring.csinfrastr.csproductivity import OpenMpi
from spring.micprgs.micctfdetermine_mpi import ScanMpi
from spring.micprgs.michelixtrace import MicHelixTrace, MicHelixTracePar
from spring.segment2d.segment_mpi import SegmentMpi


class MicHelixTraceMpi(MicHelixTrace, ScanMpi):

    def trace_helices(self):
        self.startup_scan_mpi_programs()
        
        if self.micrograph_files != []:
            helix_info = self.trace_helices_in_micrographs(self.micrograph_files, self.outfiles)
        
        self.comm.barrier()
        helix_info = SegmentMpi().gather_distributed_helices_to_root(self.comm, helix_info)
            
        if self.rank == 0:
            self.enter_helixinfo_into_springdb(helix_info)

        self.end_scan_mpi_programs()

def main():
    parset = MicHelixTracePar()
    reduced_parset = OpenMpi().start_main_mpi(parset)
    
    ####### Program
    micrograph = MicHelixTraceMpi(reduced_parset)
    micrograph.trace_helices()


if __name__ == '__main__':
    main()
