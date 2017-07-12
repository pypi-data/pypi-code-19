# -*- coding: utf-8 -*-
"""RAGE - ddRAD generator is a python program to simulate ddRADseq data.

Rage creates a set of FASTQ files that can be analyzed and a ground truth file
in which all simulated effects are logged.

The simulated reads contain the most commonly encountered deviations in ddRAD data:
    - both heterozygouos and homozygous mutations consisting of SNPs, indels and null alleles
    - missing information for single individuals
    - singleton reads (for example by contamination during library preparation)
    - reads from highly repetitive loci (lumberjack stacks)
    - variable coverage
    - PCR copies
    - reads affected by imcomplete digestion
    - sequencing errors

All simulated effects contained in a read are logged in the FASTQ name line.
Additionally a ground truth file is written next to the created FASTQ files.

The FASTQ files are written in order of read creation and need to be shuffled.
Files written in creation order will provide an easier view on the
available data when looking at the file. Beware that this might create
abnormally easy instances for the further analysis process.
"""
import argparse

from .initialization import create_perfect_loci
from .postprocessors import SingletonGenerator
from .postprocessors import HighlyRepetitiveLocusGenerator as HRLGenerator
from .distributions import validate_probability_parameters, initialize_coverage_generators
from .generation import initialize_quality_model
from . import barcodes
from . import output


def all_seqs_to_bytes(args):
    """Convert all sequences (overhangs, recognition sites) to bytes."""
    def to_bytes(seq):
        if isinstance(seq, bytes):
            return seq
        else:
            return seq.encode()
    args.dbr = to_bytes(args.dbr)
    args.p5_overhang = to_bytes(args.p5_overhang)
    args.p7_overhang = to_bytes(args.p7_overhang)
    args.p5_rec_site = to_bytes(args.p5_rec_site)
    args.p7_rec_site = to_bytes(args.p7_rec_site)


def validate_sequence_parameters(args, individuals):
    """Assert that the sequence parameters are valid.

    Arguments:
        args (argparse.Namespace): User parameters.
        individuals (iterable of tuples): Individuals list returned by barcodes module.

    Raises:
        ValueError if the p5 overhang is not a suffix of the p5 recognition site.
        ValueError if the p7 overhang is not a suffix of the p7 recognition site.
        ValueError if the sum of the p5 auxilliary seqeunces is smaller than the 
             read length. I.e. no read length is left to fill with genomic sequence.
        ValueError if the sum of the p7 auxilliary seqeunces is smaller than the 
             read length. I.e. no read length is left to fill with genomic sequence.
    """
    all_seqs_to_bytes(args)
    # check rec sites and overhangs are subsets of each other
    if not args.p5_rec_site.endswith(args.p5_overhang):
        raise ValueError("P5 overhang '{}' is not a suffix of the recignition site '{}'.".format(args.p5_overhang.decode(), args.p5_rec_site.decode()))
    if not args.p7_rec_site.endswith(args.p7_overhang):
        raise ValueError("P7 overhang '{}' is not a suffix of the recignition site '{}'.".format(args.p7_overhang.decode(), args.p7_rec_site.decode()))
    # get barcode lengths and spacer lengths
    barcodes, other = zip(*individuals)
    p5_bcs, _ = zip(*barcodes)
    p5_spacers, p7_spacers, *_ = zip(*other)
    longest_p5_bc = max((len(bc) for bc in p5_bcs))
    longest_p5_spacer = max((len(spacer) for spacer in p5_spacers))
    longest_p7_spacer = max((len(spacer) for spacer in p7_spacers))

    p5_aux_length = longest_p5_bc + longest_p5_spacer + len(args.p5_overhang)
    if args.read_length <= p5_aux_length + 1:
        raise ValueError("Read length is smaller than sum of p5 auxiliary sequences ({}).".format(p5_aux_length))

    p7_aux_length = longest_p7_spacer + len(args.dbr) + len(args.p7_overhang)
    if args.read_length <= p7_aux_length + 1:
        raise ValueError("Read length is smaller than sum of p7 auxiliary sequences ({}).".format(p7_aux_length))


def main():
    """Handle main flow of read generation.

    This includes:
        * Picking barcode pairs (i.e. individuals)
        * create initial set of perfect loci; i.e. a read for all
          (loci x individuals) grouped in RADLocus objects
        * Add deviations / modifications to all loci
        * Write reads to file
    """
    argument_parser = get_argument_parser()
    args = argument_parser.parse_args()

    print("Simulating reads from {} individuals at {} loci with a coverage of {}.".format(args.nr_individuals, args.nr_loci, args.cov))

    if args.verbosity >= 1:
        print("Initialization")
    ############################################################################
    # Initialization Phase
    ############################################################################
    if args.verbosity >= 1:
        print("Picking individuals.")
    barcode_set = barcodes.select_barcode_set(args.barcode_set)

    # pick a number of individuals with the same p7 barcode
    # and prepare them for processing
    individuals, p7_bc, individuals_matrix = barcodes.pick_individuals(args.nr_individuals)
    individuals = sorted(individuals, key=lambda x: x[1][2])
    validate_sequence_parameters(args, individuals)

    # Prepare generators for coverage values
    initialize_coverage_generators(args)
    # initialize the quality generator
    initialize_quality_model(path=args.quality_model, read_length=args.read_length)
    # if an event profile was given, i.e. a list of probabilities for
    # locus event types, make sure it sums up to one and is a dict
    validate_probability_parameters(args)
    
    if args.verbosity >= 1:
        print("Initializing loci.")

    # create perfect read pairs and use them to initialize empty locus objects
    loci, conf = create_perfect_loci(individuals, args)
    # save statistics information for later use
    # also safe config information for output files
    conf['target coverage (d_s)'] = args.cov
    conf['used coverage model'] = args.coverage_model
    conf['barcode set'] = barcode_set
    conf['individuals matrix'] = individuals_matrix
    stats = output.Stats({
        "nr_total_valid_reads": 0,
        "nr_total_reads": 0,
        "nr_valid_pcr_copies": 0,
    })

    # create filepaths, namelines, assemble fastq entry objects
    # these have to be generators to enable stream processing
    paths = output.generate_file_name(p7_bc, args.output_path_prefix, name=args.name)

    ############################################################################
    # Simulation Phase
    ############################################################################
    # pick event types, create reads, write them to file
    ticksize = 20 if len(loci) >= 20 else 1
    if args.verbosity >= 1:
        print("Simulating loci:")

    for i, locus in enumerate(loci, 1):
        # show progress
        if args.verbosity >= 1 and i % (len(loci) // ticksize) == 0:
            print(" {:>7}/{:>7}".format(i, len(loci)))

        # add modifications to the reads (SNPs, Indels, null alleles, dropout, ...)
        # pick the event type and create read coverage
        locus.simulate_individual_events(args)

        # create fastq entries and write them to file
        final_reads_fastq = locus.fastq_entries()
        output.append_to_fastq_files(final_reads_fastq, path_p5=paths.p5, path_p7=paths.p7)

        # update statistics information that will be used for the output files
        stats.nr_total_valid_reads += len(locus)
        stats.nr_valid_pcr_copies += locus.nr_pcr_copies

        # remove the most memory-filling parts of the locus object,
        # i.e. the generated reads, to save memory, but keep
        # the locus object and all of its derived values for later use
        locus.burn()

    ############################################################################
    # Postprocessing Phase
    ############################################################################
    # write ground truth files, as all valid read information is ready at this point
    # writes: _1.tsv and _2.tsv files and _gt.tsv file
    if args.verbosity >= 1:
        print("Writing ground truth file.")
    output.write_ground_truth(loci, paths, args)

    # generate obscuring reads (singletons, HRL reads)
    # specify a blocksize for writing obscuring reads to file
    # this prevents lots of small writing accesses to the disc
    blocksize = 100000
    # create list of singleton reads that do not belong to any locus.
    # they come with a finalized dbr etc. and PCR copies,
    # but only a coverage of one.
    if args.verbosity >= 1:
        print("Simulating singletons.")
    singleton_gen = SingletonGenerator(individuals, args)
    for singletons in singleton_gen.read_blocks(blocksize):
        fastq_singletons = [read.fastq_entry() for read in singletons]
        output.append_to_fastq_files(fastq_singletons, path_p5=paths.p5, path_p7=paths.p7)

    # create a list of HRL reads that form giant loci
    hrl_gen = HRLGenerator(individuals, args)
    if args.verbosity >= 1:
        print("Simulating HRLs.")
    for hrl_reads in hrl_gen.read_blocks(blocksize):
        fastq_hrl_reads = [read.fastq_entry() for read in hrl_reads]
        output.append_to_fastq_files(fastq_hrl_reads, path_p5=paths.p5, path_p7=paths.p7)
    output.append_hrls_to_ground_truth(hrl_gen, paths)

    # assemble some statistic values for the statistics file
    if args.verbosity >= 1:
        print("Gathering data for statistics.")
    stats.singletons = singleton_gen.nr_singletons
    stats.singleton_pcr_copies = singleton_gen.nr_pcr_copies
    stats.total_singleton_reads = stats.singletons + stats.singleton_pcr_copies
    stats.nr_hrl_loci = hrl_gen.nr_hrl_loci
    stats.hrl_reads = hrl_gen.nr_hrl_reads
    stats.hrl_pcr_copies = hrl_gen.nr_pcr_copies
    stats.total_hrl_reads = stats.hrl_reads + stats.hrl_pcr_copies
    stats.nr_total_reads = stats.nr_total_valid_reads + stats.total_singleton_reads + stats.total_hrl_reads

    # write annotation and statistics files
    if args.verbosity >= 1:
        print("Writing logs and statistics.")
    output.assemble_statistic_data(stats, conf, args, loci)
    output.write_annotation_file(stats, conf, args, paths.annotation)
    output.write_user_output(stats, conf, args, paths)
    output.assemble_overview_data(stats, conf, args, paths, loci)


def get_argument_parser():
    """ Create an argument parser."""
    description_text = "RAGE -- the ddRAD generator -- simulates ddRADseq datasets, comprising reads (FASTQ files) and ground truth (YAML file)."

    parser = argparse.ArgumentParser(
        description=description_text)

    # naming and paths
    names_group = parser.add_argument_group("Naming Parameters")
    names_group.add_argument(
        "--name",
        help="Name for the dataset that will be used in the filename. If none is given, the name 'RAGEdataset' will be used.",
        action="store",
        dest="name",
        default=None,
        )

    names_group.add_argument(
        "-o", "--output",
        help="Prefix of the output path. At this point a folder will be created that contains all output files created by RAGE.",
        action="store",
        dest="output_path_prefix",
        default="",
        )

    # Main dataset parameters
    dataset_group = parser.add_argument_group("Dataset Parameters")
    dataset_group.add_argument(
        "-n", "--nr-individuals",
        help="Number of individuals in the result. Default: 3",
        action="store",
        dest="nr_individuals",
        type=int,
        default=3,
        )

    dataset_group.add_argument(
        "-l", "--nr-loci",
        help="Number of loci for which reads will be created. Default: 3",
        action="store",
        dest="nr_loci",
        type=int,
        default=3,
        )

    dataset_group.add_argument(
        "-r", "--read-length",
        help="Total sequence length of the reads (including overhang, barcodes, etc.). Default: 100",
        action="store",
        dest="read_length",
        type=int,
        default=100,
        )

    dataset_group.add_argument(
        "-c", "--coverage",
        help="Expected coverage that will be created by normal duplication and mutations. The exact coverage value is determined using a probabilistic process. Default: 30",
        action="store",
        dest="cov",
        type=int,
        default=30,
        )

    dataset_group.add_argument(
        "--hrl-number",
        help="Number of Highly Repetitive Loci (HRLs) that will be added, given as fraction of total locus size. Example: ``-l 100 --hrl-number 0.1`` for 10 HRLs. Default: 0.05",
        action="store",
        dest="hrl_number",
        default=0.05,
        )

    dataset_group.add_argument(
        "--diversity",
        help="Parameter for the number of genotypes created per locus. This will be used as parameter for a Poisson distribution. Default: 1.0, increase for more alleles / genotypes per locus.",
        action="store",
        dest="diversity",
        type=float,
        default=1.0,
        )

    dataset_group.add_argument(
        "--gc-content",
        help="GC content of the generated sequences. Default: 0.5",
        action="store",
        dest="gc_content",
        type=float,
        default=0.5,
        )

    dataset_group.add_argument(
        "-q", "--quality-model",
        help="Path to a quality model file (.qmodel). A qmodel file contains a probability vector for each read position. For details, please refer to the documentation.",
        action="store",
        dest="quality_model",
        default="L100-Q70",
        )

    # coverage model parameters
    cov_group = parser.add_argument_group("Coverage Model Parameters")
    cov_group.add_argument(
        "--coverage-model",
        help="Model to choose coverage values. Can be either 'poisson' or 'betabinomial'. The Betabinomial model is the default as it can be easily adapted to different coverage profiles using the --BBD-alpha and --BBD-beta parameters.",
        action="store",
        dest="coverage_model",
        default="betabinomial",
        )

    cov_group.add_argument(
        "--BBD-alpha",
        help="Alpha parameter of the Beta-binomial distribution. Higher values increase the left tailing of the coverage distribution, if the BBD model is used. Default: 6",
        action="store",
        dest="bbd_alpha",
        type=float,
        default=6,
        )

    cov_group.add_argument(
        "--BBD-beta",
        help="Beta parameter of the Beta-binomial distribution. Higher values increase the right tailing of the coverage distribution, if the BBD model is used. Default: 2",
        action="store",
        dest="bbd_beta",
        type=float,
        default=2,
        )

    cov_group.add_argument(
        "--max-pcr-copies",
        help="Maximum number of PCR copies that can be created for each finalized (potentially mutated and multiplied) read. Default: 3",
        action="store",
        dest="max_pcr_copy_nr",
        type=int,
        default=3,
        )

    cov_group.add_argument(
        "--hrl-max-cov", "--hrl-max-coverage",
        help="Maximum coverage for Highly Repetitive Loci (HRLs) (per individual). The minimum coverage is determined as mean + 2 standard deviations (μ + 2σ) of the main coverage generating function. Default: 1000",
        action="store",
        dest="hrl_max_cov",
        default=1000,
        )

    # Sequence Infos
    seqs_group = parser.add_argument_group("Read Sequences")
    seqs_group.add_argument(
        "-d", "--dbr",
        help="Sequence of the degenerate base region (DBR) in IUPAC ambiguity code. Default: 'NNNNNNMMGGACG'. To not include a DBR sequence use --dbr ''",
        action="store",
        type=str,
        dest="dbr",
        default="NNNNNNMMGGACG",
        )

    seqs_group.add_argument(
        "--p5-overhang",
        help="Sequence of the p5 overhang. Default: 'TGCAT'",
        action="store",
        type=str,
        dest="p5_overhang",
        default="TGCAT",
        )

    seqs_group.add_argument(
        "--p7-overhang",
        help="Sequence of the p7 overhang. Default: 'TAC'",
        action="store",
        type=str,
        dest="p7_overhang",
        default="TAC",
        )

    seqs_group.add_argument(
        "--p5-rec-site",
        help="Sequence of the p5 recognition site. Default: 'ATGCAT'",
        action="store",
        type=str,
        dest="p5_rec_site",
        default="ATGCAT",
        )

    seqs_group.add_argument(
        "--p7-rec-site",
        help="Sequence of the p7 recognition site. Default: 'GTCA'",
        action="store",
        type=str,
        dest="p7_rec_site",
        default="GTAC",
        )

    seqs_group.add_argument(
        "-b", "--barcodes",
        help="Path to barcodes file or predefined barcode set like 'barcodes', 'small' or 'full'. Default: 'barcodes', a generic population. Take a look at the rage/barcode_handler/barcodes folder for more information.",
        action="store",
        type=str,
        dest="barcode_set",
        default="barcodes",
        )

    # probabilities
    probs_group = parser.add_argument_group("Simulation Probabilities")
    probs_group.add_argument(
        "--event-probabilities",
        help="Probability profile for the distribution of event types (common, dropout, mutation; in this order), given as list of floats.\
              Example: ``python rage.py --event-probabilities 0.9 0.05 0.05`` -> common 90%%, dropout 5%%, mutation 5%% (Default).",
        action="store",
        dest="event_prob_profile",
        metavar=("PROB_COMMON", "PROB_DROPOUT", "PROB_MUTATION"),
        nargs=3,
        default=None,
        )

    probs_group.add_argument(
        "--mutation-type-probabilities",
        help="Probability profile for the distribution of mutation types (snp, insertion, deletion, na; in this order), given as list of floats.\
              Example: ``python rage.py --mutation-type-probabilities 0.8999 0.05 0.05 0.0001`` -> snp 89.99%%, insertion 5%%, deletion 5%%, na 0.01%% (Default).",
        action="store",
        dest="mutation_type_prob_profile",
        metavar=("PROB_SNP", "PROB_INSERTION", "PROB_DELETION", "PROB_NA"),
        nargs=4,
        default=None,
        )

    probs_group.add_argument(
        "--prob-heterozygous",
        help="Probability of mutations beeing heterozygous. Default: 0.5",
        action="store",
        dest="prob_heterozygocity",
        type=float,
        default=0.5,
        )

    probs_group.add_argument(
        "--prob-incomplete-digestion",
        help="Probability of incomplete digestion for an individual at a locus. Default: 0.1",
        action="store",
        dest="prob_incomplete_digestion",
        type=float,
        default=0.1,
        )

    probs_group.add_argument(
        "--rate-incomplete-digestion",
        help="Expected fraction of reads that are being lost in the event of Incomplete Digestion. Default: 0.2",
        action="store",
        dest="rate_incomplete_digestion",
        type=float,
        default=0.2,
        )

    probs_group.add_argument(
        "--prob-pcr-copy",
        help="Probability that a (potentially mutated and multiplied) read will recieve pcr copies. This influences the simulated pcr copy rate. Default: 0.2",
        action="store",
        dest="prob_pcr_copy",
        type=float,
        default=0.2,
        )

    probs_group.add_argument(
        "-e", "--prob-seq-error",
        help="Probability of sequencing substitution errors. Default: 0.01",
        action="store",
        dest="prob_seq_error",
        default=0.01,
        )

    # debug and output
    parser.add_argument(
        "-v", "--verbose",
        help="Increase verbosity of output.\n-v: Show progress of simulation.\n-vv: Print used parameters after simulation.\n-vvv: Show details for each simulated locus.",
        action="count",
        dest="verbosity",
        default=0,
        )

    parser.add_argument(
        "--DEBUG",
        help="Set debug-friendly values for the dataset, i.e. all mutation events and mutation types are equally probable.",
        action="store_true",
        dest="debug_run",
        default=False,
        )

    return parser



if __name__ == "__main__":
    main()
