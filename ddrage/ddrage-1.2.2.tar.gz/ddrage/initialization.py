# -*- coding: utf-8 -*-
"""This module handles the creation of perfect loci from which genotypes
etc. will be derived.
"""
from .rad_locus import RADLocus
from .rad_reads import ProtoReadp7


def create_perfect_loci(individuals, args):
    """Create perfect loci to prime the simulation process.

    Later, in different parts of the pipeline, mutations, copies, and other
    modifications will be added to the reads at the loci.

    Arguments:
        individuals (list of individuals): Containing tuples containing barcode pairs,
            spacers, individual name etc. for an individual. For details on the 
            specification see the note below.
        args (Argparse.Namespace): Containing the following parameters:
            nr_loci (int): Number of loci to be created.
            dbr_seq (bytes): Sequence of the degenerate base region in IUPAC ambiguity code.
            p5_overhang (bytes): Overhang created by the p5 restriction enzyme.
            p5_rec_site (bytes): Recognition site of the p5 restriction enzyme.
            p7_overhang (bytes): Overhang created by the p7 restriction enzyme.
            p7_rec_site (bytes): Recognition site of the p5 restriction enzyme.
            read_length (int): Total length of the reads.
            prob_seq_error (float): Probability of a sequencing base error.
            diversity (float): Genetic diversity at this locus. Given as the lambda
                parameter for the zero-truncated poisson distribution that regulates
                the number of alleles per mutationModel.
            gc_content (float): GC content of the simulated sequence.

    Returns:
        tuple(list, dict): A list containing RADLocus objects and a dictionary
        containing the used configuration used to create the loci.

    Note:
        The structure of an individual entry (used as first input parameter) is as follows:
        ::

            (p5_barcode, p7_barcode), (p5_spacer, p7_spacer, individual_name, *meta_info) = individual
    """
    # get p7 barcode and spacer which is the same for all individuals
    (_, p7_bc), (_, p7_spacer, *_) = individuals[0]
    
    # create one p7 sequence for each locus
    p7_reads = [
        ProtoReadp7(
            p7_bc,
            p7_spacer,
            args.dbr,
            args.p7_overhang,
            args.p7_rec_site,
            args.gc_content,
            args.read_length,)
        for _ in range(args.nr_loci)]
    
    # intialize loci using a list of individuals and the p7 protoreads created above
    all_loci = []
    for locus_name, p7_read in enumerate(p7_reads):
        # the locus number from the enumeration is used as a locus name / identifier later
        locus = RADLocus(individuals, p7_read, locus_name, args)
        all_loci.append(locus)
    # save the used configuration. this will be used in the statistics and output files
    conf = {
        "nr of individuals": len(individuals),
        "nr of loci": args.nr_loci,
        "read length": args.read_length,
        "dbr sequence": args.dbr,
        "p7 barcode": p7_bc,
        "p5 recognition site": args.p5_rec_site,
        "p7 recogintion site": args.p7_rec_site,
        "p5 overhang": args.p5_overhang,
        "p7 overhang": args.p7_overhang,
        "prob. seq error": args.prob_seq_error,
        "individuals": str([i[1][2] for i in individuals]),
        "individual names": [str(i[1][2]) for i in individuals],
        "diversity parameter": args.diversity,
    }
    return all_loci, conf


def create_perfect_hrl_loci(args, individuals, nr_hrl_loci):
    """Create a locus containing only template reads for HRLs.

    Note:
        This function does not assemble a conf, as the HRL reads
        are only added as postprocessing and it is not needed there.

    Arguments:
        args (Argparse Namespace):
        individuals (list of individuals): Containing tuples containing barcode pairs,
            spacers, individual name etc. for an individual. For details on the 
            specification see the note below.
        nr_hrl_loci (int): How many HC loci will be cretaed.

    Returns:
        list: A list of perfect loci that are ready to receive Hrl treatment.
    """
    # sort individuals to match 
    individuals = sorted(individuals, key=lambda x: x[1][2])

    # get p7 barcode and spacer which is the same for all individuals
    (_, p7_bc), (_, p7_spacer, *_) = individuals[0]
    
    # create one p7 sequence for each locus
    p7_reads = [ProtoReadp7(p7_bc, p7_spacer, args.dbr, args.p7_overhang, args.p7_rec_site, args.gc_content, args.read_length) for _ in range(nr_hrl_loci)]
    
    # intialize loci using a list of individuals and the p7 proto-reads created above
    hrl_loci = []
    for locus_name, p7_read in enumerate(p7_reads):
        locus = RADLocus(individuals, p7_read, "HRL_{}".format(locus_name), args)
        hrl_loci.append(locus)

    return hrl_loci
