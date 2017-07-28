from . import _seqlib
import pysam

class BWAWrapper(_seqlib.BWAWrapper):
    def makeIndex(self, namesToSeqs):
        super().makeIndex(namesToSeqs, list(namesToSeqs.keys()))
        
    def align(self, seq, quality=None, read_name=None, secondary_hit_cutoff=0.9, max_secondary=10):
        alns = super().align(seq, 
                             secondary_hit_cutoff=secondary_hit_cutoff,
                             max_secondary=max_secondary,
                             hardclip=False)

        pysam_alns = []

        for seqlib_aln in alns:
            pysam_aln = pysam.AlignedSegment()
            pysam_aln.reference_id = seqlib_aln.ChrID()
            pysam_aln.reference_start = seqlib_aln.Position()
            pysam_aln.cigarstring = seqlib_aln.CigarString()

            if quality is not None:
                pysam_aln.quality = quality
            if read_name is not None:
                pysam_aln.query_name = read_name

            pysam_aln.query_sequence = seqlib_aln.Sequence()
            pysam_aln.is_reverse = seqlib_aln.ReverseFlag()

            # print()
            # print(seq)
            # print("seqlib:", seqlib_aln)
            # print("pysam:", pysam_aln)

            
            pysam_alns.append(pysam_aln)

        return pysam_alns
