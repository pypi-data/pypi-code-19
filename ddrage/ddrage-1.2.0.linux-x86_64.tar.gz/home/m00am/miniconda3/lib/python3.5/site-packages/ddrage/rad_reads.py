# -*- coding: utf-8 -*-
"""This module contains all classes that model reads or parts of reads.

This includes the ProtoRead class and its derivatives,
which model the p5 and p7 part of a whole RAD read.

The RADRead class models a mate pair of p5 and p7 read.
The mates are modeled by ProtoRead objects (see above).
"""
import random
import copy
import numpy as np

from functools import partial

from .generation import random_seq, generate_qualities
from . import output
from . import mutation_model
from .mutation_model import mut_application_order, mut_position

# Resolve IUPAC ambiguity codes
valid_iupac_char = {
    "A": lambda: "A",
    "C": lambda: "C",
    "G": lambda: "G",
    "T": lambda: "T",
    "R": partial(random.choice, ("A","G")),
    "Y": partial(random.choice, ("C","T")),
    "S": partial(random.choice, ("C","G")),
    "W": partial(random.choice, ("A","T")),
    "K": partial(random.choice, ("G","T")),
    "M": partial(random.choice, ("A","C")),
    "B": partial(random.choice, ("C","G","T")),
    "D": partial(random.choice, ("A","G","T")),
    "H": partial(random.choice, ("A","C","T")),
    "V": partial(random.choice, ("A","C","G")),
    "N": partial(random.choice, ("A","C","G","T")),

    65: lambda: 65,
    67: lambda: 67,
    71: lambda: 71,
    84: lambda: 84,
    82: partial(random.choice, (65,71)),
    89: partial(random.choice, (67,84)),
    83: partial(random.choice, (67,71)),
    87: partial(random.choice, (65,84)),
    75: partial(random.choice, (71,84)),
    77: partial(random.choice, (65,67)),
    66: partial(random.choice, (67,71,84)),
    68: partial(random.choice, (65,71,84)),
    72: partial(random.choice, (65,67,84)),
    86: partial(random.choice, (65,67,71)),
    78: partial(random.choice, (65,67,71,84)),
    }
# This is queried to make sure, that SNPs really change the
# perceived base. For example a C -> C SNP can not be reasonably detected.
not_this = mutation_model.not_this


class RADRead:
    """This class models a paired-end RAD read."""
    
    def __init__(self, protoread_p5, protoread_p7, individual_name, meta_info):
        """Create a new read from two protoreads.
        
        Arguments:
            protoread_p5 (ProtoReadP5): p5 part of the read
            protoread_p7 (ProtoReadP7): p7 part of the read
            individual_name (str): The name of the individuals this read
                originates from.
            meta_info (list): List of operations that have been executed on
                this read. This can include mutations, copies, ...
        """
        self.protoread_p5 = protoread_p5
        self.protoread_p7 = protoread_p7
        self.individual_name = individual_name
        self.meta_info = meta_info

    @classmethod
    def from_p7_protoread(cls, bc_p5, spacer_p5, individual_name, overhang_p5,
                          rec_site_p5, sequence_p5, protoread_p7, gc_content,
                          length, meta_info):
        """Create a new read from an existing p7 protoread.

        Arguments:
            bc_p5 (str): The p5 barcode used to create this read.
            spacer_p5 (str): The p5 spacer used to create this read.
            individual_name (str): The name of the individual this read
                originates from.
            overhang_p5 (str): The overhang of the p5 enzyme.
            rec_site_p5 (str): The restriction site of the p5 enzyme.
            sequence_p5 (str): The p5 read sequence
            protoread_p7 (ProtoReadP7): A proto read for the p7 side of the
                read pair.
            gc_content (float): GC content of the simulated sequence.
            length (int): Target length of the finished read. Most of the
                time 100 for Illumina sequencers.
            meta_info (list): List of operations that have been executed on
                this read. This can include mutations, copies, ...

        Returns:
            RADRead: build from the p7 read and the p5 fragments.
        """
        pp5 = ProtoReadp5(bc_p5, spacer_p5, overhang_p5, rec_site_p5, length, gc_content, sequence=sequence_p5)
        pp7 = copy.deepcopy(protoread_p7)
        return cls(pp5, pp7, individual_name, meta_info)

    @classmethod
    def mutated_copy(cls, template_read, allele):
        """Copy an existing read and add mutations from a random allele from the Mutation Model.

        All sequences will be copied using copy.deepcopy,
        no changes are made to the template_read.

        Arguments:
            template_read (RadRead): A RADRead object to copy.
            allele (Allele): An allele object describing the desired mutation.

        Returns:
            RADRead: Copy of the input with added mutations and the used allele.
        """
        # extract parts of read that are needed for the costructor
        protoread_p5 = copy.deepcopy(template_read.protoread_p5)
        protoread_p7 = copy.deepcopy(template_read.protoread_p7)
        individual_name = copy.deepcopy(template_read.individual_name)
        meta_info = copy.deepcopy(template_read.meta_info)
        # create carbon copy of the template read
        mutated_read = cls(protoread_p5, protoread_p7, individual_name, meta_info)
        # apply the alleles mutations
        mutated_read.apply_allele(allele)
        return mutated_read

    def seqs(self):
        """Return the two sequences of the reads without any barcodes etc."""
        return self.protoread_p5.sequence, self.protoread_p7.sequence

    def __getitem__(self, key):
        """Access positions in the read sequences.

        Arguments:
            key (tuple): Tuple of (mate, pos), where mate is 0 (p5) or 1 (p7),
                and pos is a reads position as integer.
        """
        mate, pos = key
        if mate == 0:
            return self.protoread_p5.sequence[pos]
        elif mate == 1:
            return self.protoread_p7.sequence[pos]
        else:
            raise ValueError("Key must be a tuple (mate, pos) where mate is 0 (p5) or 1(p7) and pos a vlaid position in the sequence.")

    def __setitem__(self, key, item):
        """Access positions in the read sequences.

        Arguments:
            key (tuple): Tuple of (mate, pos), where mate is 0 (p5) or 1 (p7),
                and pos is a reads position as integer.
            item (byte): A charatcer as integer.
        """
        mate, pos = key
        if mate == 0:
            mutable_seq = bytearray(self.protoread_p5.sequence)
            mutable_seq[pos] = item
            self.protoread_p5.sequence = bytes(mutable_seq)
        elif mate == 1:
            mutable_seq = bytearray(self.protoread_p7.sequence)
            mutable_seq[pos] = item
            self.protoread_p7.sequence = bytes(mutable_seq)
        else:
            raise ValueError("Key must be a tuple (mate, pos) where mate is 0 (p5) or 1(p7) and pos a valid position in the sequence.")

    def finalize_dbr(self):
        """Replace IUPAC ambiguity code in the DBR with bases."""
        finalized_dbr = []
        # find all non-ACGT chars and replace them
        for base in self.protoread_p7.dbr_seq:
            finalized_dbr.append(valid_iupac_char[base]())
        self.protoread_p7.dbr_seq = bytes(finalized_dbr)

    def add_meta_info(self, info):
        """Add one or more items to the meta info list."""
        if isinstance(info, str):
            self.meta_info.append(info)
        else:
            self.meta_info.extend(info)

    def apply_allele(self, allele):
        """Apply the mutations of the given allele to this read pair.

        Arguments:
            allele (Allele): An Allele object from a mutation model.
                This should be selected by using the random_allele
                method of Mutation Model.
        """
        # sort and apply mutations of the allele 
        # by application order (first SNPs, then indels, last NAs)
        # 
        # When applying indels: keep a steady tab on offsets due to prior indels.
        # 
        # handling of annotation offsets etc. happens in mutation_model.fastq_header_annotation
        p5_indel_offset = 0
        p7_indel_offset = 0
        for mutation in sorted(allele.mutations, key=mut_application_order):
            if type(mutation) is mutation_model.SNPMutation:
                # make sure the order is upheld
                if p5_indel_offset != 0 or p7_indel_offset != 0:
                    raise ValueError("Trying to apply indels before SNPs.")
                # pick protoread to apply the mutation to.
                # Reminder: a RADRead consists of two protoreads (p5 and p7)
                if mutation.mate == 0:
                    self.protoread_p5.apply_snp(mutation.pos, mutation.base_from, mutation.base_to)
                elif mutation.mate == 1:
                    self.protoread_p7.apply_snp(mutation.pos, mutation.base_from, mutation.base_to)
                else:
                    raise ValueError("Mate should be 0 (p5) or 1 (p7), not {}".format(mutation.mate))

            elif type(mutation) == mutation_model.InsertMutation:
                # handle insertions, update indel_offset
                if mutation.mate == 0:
                    self.protoread_p5.apply_insertion(mutation.pos + p5_indel_offset, mutation.seq)
                    p5_indel_offset += len(mutation.seq)
                elif mutation.mate == 1:
                    self.protoread_p7.apply_insertion(mutation.pos + p5_indel_offset, mutation.seq)
                    p7_indel_offset += len(mutation.seq)
                else:
                    raise ValueError("Mate should be 0 (p5) or 1 (p7), not {}".format(mutation.mate))

            elif type(mutation) == mutation_model.DeletionMutation:
                # handle deletions, update indel_offset
                if mutation.mate == 0:
                    del_seq = self.protoread_p5.apply_deletion(mutation.pos + p7_indel_offset, mutation.length)
                    mutation.del_seq = del_seq
                    p5_indel_offset -= mutation.length
                elif mutation.mate == 1:
                    del_seq = self.protoread_p7.apply_deletion(mutation.pos + p7_indel_offset, mutation.length)
                    mutation.del_seq = del_seq
                    p7_indel_offset -= mutation.length
                else:
                    raise ValueError("Mate should be 0 (p5) or 1 (p7), not {}".format(mutation.mate))

            elif type(mutation) == mutation_model.P7NAMutation:
                # handle NAs
                self.protoread_p7.apply_na(mutation.seq)

            else:
                # make sure no invalid mutation type is used (silently)
                raise ValueError("Invalid mutation type {} in allele {}".format(type(mutation), allele))
        # calculate offset due to prefixes for annotation entries
        p5_prefix_length = self.protoread_p5.prefix_length
        p7_prefix_length = self.protoread_p7.prefix_length
        # update annotation data, add information about added SNPs
        p5_annotation, p7_annotation = allele.fastq_header_annotations(p5_prefix_length, p7_prefix_length)
        annotation_str = "mutations:'{}'".format(",".join(p5_annotation + p7_annotation))
        self.add_meta_info(annotation_str)

    def fastq_entry(self):
        """Create a FASTQ entry that can be written to file.
        
        Returns:
            tuple: Containing a read tuple that can be written to file for
            both p5 and p7 read. Each read tuple contains the sequence as str,
            the name as bytes and the quality values as bytes.
        """
        p5_name, p7_name = output.assemble_casava_line(self.protoread_p7.barcode, self.meta_info)
        p5_seq, p5_qvs = self.protoread_p5.fastq_entry()
        p7_seq, p7_qvs = self.protoread_p7.fastq_entry()
        return (p5_seq, p5_name, p5_qvs), (p7_seq, p7_name, p7_qvs)

    def add_seq_errors(self, prob_seq_error):
        """ Add sequencing errors to both mate pairs / protoreads.

        Arguments:
            prob_seq_error (float): Probability for a sequencing error per base.

        Returns:
            None: Added error positions are saved in seq_errors attribute
            as a pair (p5_errors, p7_errors).
        """
        self.protoread_p5.add_seq_errors(prob_seq_error)
        self.protoread_p7.add_seq_errors(prob_seq_error)
        self.seq_errors = (self.protoread_p5.seq_errors, self.protoread_p7.seq_errors, self.protoread_p7.barcode_seq_errors)
        self.add_meta_info("p5_seq_errors:'"+";".join(map(str, self.seq_errors[0]))+"'")
        self.add_meta_info("p7_seq_errors:'"+";".join(map(str, self.seq_errors[1]))+"'")
        if self.protoread_p7.barcode_seq_errors:
            self.add_meta_info("p7_barcode_seq_errors:'"+";".join(map(str, self.seq_errors[2]))+"'")

    def fix_lengths(self, mutation_model):
        """Make sure the length of the reed is conserved after applying mutations.

        Arguments:
            mutation_model (MutationModel): The mutation model used for the locus.
        """
        self.protoread_p5.fix_length(
            mutation_model.spare_sequence_p5,
            mutation_model.spare_sequence_p5_spacer,
            mutation_model.max_p5_spacer_len,
        )
        self.protoread_p7.fix_length(mutation_model.spare_sequence_p7)


class ProtoRead:
    """This class models one part of a paired-end RAD-Read.

    This is an abstract base class for p5 and p7 proto reads.
    """

    def apply_snp(self, pos, old_base, new_base):
        """Add a single SNP to the sequence.
    
        Arguments:
            pos (int): Position of the SNP
            old_base (int): Old base (as ascii code / char)
            new_base (int): New base (as ascii code / char).
        """
        mutated_seq = bytearray(self.sequence)
        mutated_seq[pos] = new_base
        self.sequence = bytes(mutated_seq)

    def apply_insertion(self, pos, insert_seq):
        """Add an insertion mutation to the sequence.

        Arguments:
            pos (int): Sequence position of the insert. This postion has to be
                already corrected for shifts/ offsets due to other indels.
            insert_seq (bytes): Sequence to insert.
        """
        prefix = self.sequence[:pos]
        suffix = self.sequence[pos:]
        self.sequence = prefix + insert_seq + suffix

    def apply_deletion(self, pos, deletion_length):
        """Add a deletion mutation to the sequence.

        Arguments:
            pos (int): Sequence position of the deletion. This postion has to be
                already corrected for shifts/ offsets due to other indels.
            deletion_length (int): Length of the sequence to be deleted.

        Returns:
            bytes: The deleted sequence.
        """
        prefix = self.sequence[:pos]
        del_seq = self.sequence[pos:pos + deletion_length]
        suffix = self.sequence[pos + deletion_length:]
        self.sequence = prefix + suffix
        return del_seq

    def apply_na(self, na_seq):
        """Add a different (null allele) sequence to the read.

        Arguments:
            na_seq (bytes): Null allele sequence to be substituted for the
                original read sequence.
        """
        self.sequence = na_seq

    def fastq_entry(self):
        """Create a fastq entry for this read that can be written to file.
        
        Returns:
            tuple: Containing the read sequence as string and the quality value
            as bytes.
        """
        return self.joined_sequence(), generate_qualities()


class ProtoReadp5(ProtoRead):
    """This class models the p5 side of a paired-end RAD read."""
    
    def __init__ (self, barcode_p5, spacer_p5, overhang_p5, rec_site_p5,
                  length, gc_content, sequence):
        """Create a single end p5 read.

        Arguments:
            barcode_p5 (str): The barcode sequence.
            spacer_p5 (str): The spacer sequence.
            overhang_p5 (bytes): The overhang sequence of the p5 enzyme.
            rec_site_p5 (bytes): The restriction site sequence of the p5 enzyme.
            length (int): The total length of the read. Most of the time this
                will be 100 for Illumina sequencers.
            gc_content (float): GC content of the simulated sequence. 
            sequence (bytes): The read sequence. If no sequence is given a random
                read sequence will be generated, that does not contain the
                p5 restriction site.
        """
        self.barcode = barcode_p5
        self.spacer = spacer_p5
        self.overhang = overhang_p5
        self.rec_site = rec_site_p5
        self.length = length
        self.prefix_length = len(self.barcode) + len(self.spacer) + len(self.overhang)
        self.sequence = sequence
    
    def joined_sequence(self):
        """Return the complete read sequence."""
        return b"".join((self.barcode, self.spacer, self.overhang, self.sequence))

    @staticmethod
    def p5_prefix_length(barcode, spacer, overhang):
        """Compute the total length of a p5 prefix from the given fragemnts.

        Arguments:
            barcode (str or bytes): barcode sequence
            spacer (str or bytes): spacer sequence
            overhang (str or bytes): overhang sequence

        Returns:
            int: Length of the p5 prefix.
        """
        return len(barcode)+len(spacer)+len(overhang)

    def fragment_lengths(self):
        """The individual length of all fragments. This is EXACTLY only the sum of its parts."""
        return tuple(map(len, (self.barcode, self.spacer, self.overhang, self.sequence)))

    def total_length(self):
        """The total length of all fragments. This is EXACTLY only the sum of its parts."""
        return sum(map(len, (self.barcode, self.spacer, self.overhang, self.sequence)))

    def add_seq_errors(self, prob_seq_error):
        """Add sequencing errors to all positions in the read with given probability.

        Note:
            Each position in the read, including barcodes, dbr, etc. has a change of
            prob_seq_error to be a sequencing error.
        
        Arguments:
            prob_seq_error (float): Probability for a sequencing base error.

        Returns:
            None: The sequences are changed in place. The sequencing error positions are saved
            in each read objects seq_errors attribute.
        """
        errors = np.random.random(self.total_length()) < prob_seq_error
        
        # get lengths for the split. The last length has to be excluded, because the last slice in split
        # will run to the end. If the last element is added, there would be an empty slice at the
        # end of the split.
        err_barcode, err_spacer, err_overhang, err_seq = np.split(errors, np.cumsum(self.fragment_lengths()[:-1]))
        
        # create and overwrite 
        self.barcode = bytes((random.choice(not_this[base]) if error else base for base, error in zip(self.barcode, err_barcode)))
        self.spacer = bytes((random.choice(not_this[base]) if error else base for base, error in zip(self.spacer, err_spacer)))
        self.overhang = bytes((random.choice(not_this[base]) if error else base for base, error in zip(self.overhang, err_overhang)))
        self.sequence = bytes((random.choice(not_this[base]) if error else base for base, error in zip(self.sequence, err_seq)))

        # np.where returns a tuple with one element so it needs unpacking
        self.seq_errors = np.where(errors == True)[0].tolist()

    def fix_length(self, locus_spare_seq, length_var_spare_seq, max_len_spacer):
        """Make sure the length of the read is unchanged after mutations have been added.

        Arguments:
            locus_spare_seq (bytes): Sequence after the truncation point at
                the locus. This should be held either in the mutation model
                as part of locus.
            length_var_spare_seq (bytes): Spare sequence due to different 
                length p5 spacer sizes.
            max_len_spacer (int): Length of the longest used spacer sequence.
                This is used to compute how many bases can be taken from the
                spacer spare sequence ('pushed out bases').
        """
        length_difference = self.length - self.total_length()

        if length_difference > 0:
            # read has been shorted by deletions -> fill it up

            # check if the read has been shortened by a longer spacer seqeunce
            # long spacer seqeunces inhabit read positions and push genomic seqeunce bases
            # 'out of the read'
            spacer_shortening = max_len_spacer - len(self.spacer)

            if spacer_shortening > 0:
                # take as many bases from the 'pushed out bases' as needed
                take_from_spacer_spare = max_len_spacer - len(self.spacer)
                if take_from_spacer_spare:
                    # this test is necessary to avoid picking seq[-0:]
                    # which is the whole spacer spare sequence
                    # The multiplication with -1 is to take abses from the rear
                    # end of the spacer spare seq, since the front end bases
                    # have not been pushed out and are still in the sequence
                    lvar_padding = length_var_spare_seq[-1 * take_from_spacer_spare:]
                    self.sequence += lvar_padding[:length_difference]
                if length_difference > spacer_shortening:
                    # if the length difference could not be fixed solely with bases
                    # from the spacer spare sequnce, take bases from the locus spare sequence
                    # to reach the full length
                    self.sequence += locus_spare_seq[:length_difference-spacer_shortening]
            else:
                # no 'pushed out bases' are present.
                # directly proceed to locus spare sequence
                self.sequence += locus_spare_seq[:length_difference]

        elif length_difference < 0:
            # read has been elongated by insertions, truncate it
            # by removing the trailing bases from the sequence
            # This slice works because length_difference is a negative value at this point
            self.sequence = self.sequence[:length_difference]


class ProtoReadp7(ProtoRead):
    """This class models the p7 side of a paired-end RAD read."""

    def __init__ (self, barcode_p7, spacer_p7, dbr_seq, overhang_p7,
                  rec_site_p7, gc_content, length):
        """Create a single end p7 read with a random sequence.

        Arguments:
            barcode_p7 (str): The barcode sequence.
            spacer_p7 (str): The spacer sequence.
            dbr_seq (bytes): The DBR sequence in IUPAC ambiguity code. This 
                will later be finalized.
            overhang_p7 (bytes): The overhang sequence of the p7 enzyme.
            rec_site_p7 (bytes): The restriction site sequence of the p7 enzyme.
            gc_content (float): GC content of the simulated sequence.
            length (int): The total length of the read. Most of the time this
                will be 100 for Illumina sequencers.
        """
        self.barcode = barcode_p7
        self.spacer = spacer_p7
        self.dbr_seq = dbr_seq
        self.overhang = overhang_p7
        self.rec_site = rec_site_p7

        self.length = length
        self.prefix_length = len(self.spacer) + len(self.dbr_seq) + len(self.overhang)
        self.sequence = random_seq(length-self.prefix_length, p=gc_content, excluded_motif=self.rec_site)

    def fragments(self):
        """Return the read fragments in order."""
        return self.spacer, self.dbr_seq, self.overhang, self.sequence

    def joined_sequence(self):
        """Return the complete read sequence."""
        return b"".join((self.spacer, self.dbr_seq, self.overhang, self.sequence))

    def fragment_lengths(self):
        """The individual length of all fragments. This is EXACTLY only the sum of its parts."""
        return tuple(map(len, (self.spacer, self.dbr_seq, self.overhang, self.sequence)))

    def total_length(self):
        """The total length of all fragments. This is EXACTLY only the sum of its parts."""
        return sum(map(len, (self.spacer, self.dbr_seq, self.overhang, self.sequence)))

    def add_seq_errors(self, prob_seq_error):
        """Add sequencing errors to all positions in the read with given probability.

        Note:
            Each position in the read, including barcodes, dbr, etc. has a change of
            prob_seq_error to be a sequencing error.
        
        Arguments:
            prob_seq_error (float): Probability for a sequencing base error.

        Returns:
            None: The sequences are changed in place. The sequencing error positions are saved
            in each read objects seq_errors attribute.
        """
        errors = np.random.random(self.total_length()) < prob_seq_error
        
        # get lengths for the split. The last length has to be excluded, because the last slice in split
        # will run to the end. If the last element is added, there would be an empty slice at the
        # end of the split.
        err_spacer, err_dbr, err_overhang, err_seq = np.split(errors, np.cumsum(self.fragment_lengths()[:-1]))
        
        # create and overwrite
        self.spacer = bytes((random.choice(not_this[base]) if error else base for base, error in zip(self.spacer, err_spacer)))
        self.dbr_seq = bytes((random.choice(not_this[base]) if error else base for base, error in zip(self.dbr_seq, err_dbr)))
        self.overhang = bytes((random.choice(not_this[base]) if error else base for base, error in zip(self.overhang, err_overhang)))
        self.sequence = bytes((random.choice(not_this[base]) if error else base for base, error in zip(self.sequence, err_seq)))

        # create and overwrite p7 barcode
        err_barcode = np.random.random(len(self.barcode)) < prob_seq_error
        self.barcode = bytes((random.choice(not_this[base]) if error else base for base, error in zip(self.barcode, err_barcode)))

        # np.where returns a tuple with one element so it needs unpacking
        self.seq_errors = np.where(errors == True)[0].tolist()
        self.barcode_seq_errors = np.where(err_barcode == True)[0].tolist()

    def fix_length(self, spare_seq):
        """Make sure the length of the read is unchanged after mutations have been added.

        Arguments:
            spare_seq (bytes): Sequence after the truncation point at
                the locus. This should be held either in the mutation model
                as part of locus.
        """
        length_difference = self.length - self.total_length()
        if length_difference > 0:
            # read has been shorted by deletions -> fill it up
            self.sequence += spare_seq[:length_difference]
        elif length_difference < 0:
            # read has been elongated by insertions, truncate it
            # by removing the trailing bases from the sequence
            # This slice works because length_difference is a negative value at this point
            self.sequence = self.sequence[:length_difference]
