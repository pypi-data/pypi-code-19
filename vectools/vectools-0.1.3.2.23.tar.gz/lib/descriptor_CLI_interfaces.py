import argparse
import sys
import numpy as np
from lib.inputoutput import ParseVectors
from lib.inputoutput import outputvector
from lib.inputoutput import ParseFasta
from lib.inputoutput import VectorFormats
from lib.inputoutput import _shared_params
from lib.inputoutput import COLUMN_TITLE_FOR_OUTPUT_MATRICES

# -*- coding: utf-8 -*-
"""
##########################################################################################
This module is used for computing the Autocorrelation descriptors based different
 properties of AADs.You can also input your properties of AADs, then it can help you
to compute Autocorrelation descriptors based on the property of AADs. Currently, You
can get 720 descriptors for a given protein sequence based on our provided physicochemical
properties of AADs. You can freely use and distribute it. If you hava  any problem,
you could contact with us timely!
References:
[1]: http://www.genome.ad.jp/dbget/aaindex.html
[2]: Feng, Z.P. and Zhang, C.T. (2000) Prediction of membrane protein types based on
the hydrophobic index of amino acids. J Protein Chem, 19, 269-275.
[3]: Horne, D.S. (1988) Prediction of protein helix content from an autocorrelation
analysis of sequence hydrophobicities. Biopolymers, 27, 451-477.
[4]: Sokal, R.R. and Thomson, B.A. (2006) Population structure inferred by local
spatial autocorrelation: an Usage from an Amerindian tribal population. Am J
Phys Anthropol, 129, 121-131.
Authors: Dongsheng Cao and Yizeng Liang.
Date: 2010.11.22
Email: oriental-cds@163.com

#import lib.descriptors as descriptors

"""

STD_AMINO_ACIDS = [
    "A", "R", "N", "D", "C",
    "E", "Q", "G", "H", "I",
    "L", "K", "M", "F", "P",
    "S", "T", "W", "Y", "V"
]

'''
Additional papers.
propy: a tool to generate various modes of Chou's PseAAC.
http://bioinformatics.oxfordjournals.org/content/31/8/1307.short
repDNA: a Python package to generate various modes of feature vectors for DNA sequences by incorporating
user-defined physicochemical properties and sequence-order effects
Protein remote homology detection by combining Chou's distance-pair pseudo amino acid
composition and principal component analysis
Rcpi: R/Bioconductor package to generate various descriptors of proteins, compounds, and their interactions
ProFET: Feature engineering captures high-level protein functions
class AminoAcidProperty:
    def __init__(self, name, properties):
        self.name = name
        self.properties = properties
'''


def _handlefastanametorowname(fasta_name, delim):
    """This function is meant to prevent errors cause by using complicated fasta names as row names.
    For example if the matrix delimiter is commas and a fasta name contains a comma this would
    throw off the column naming.
    The initial split is meant to keep the sizes down.
    :param fasta_name:
    :param delim:
    :return:
    """
    return fasta_name.strip().split()[0].split(delim)[0].lstrip(">")


def _input_fasta_params(parser):
    """
    Handle the common tasks needed for vectorization

    I am a bit conflicted about the best design style for creating vecotrs. It would be more efficeint
    to make a composite vector as i.e. AACOMP-DIPEP but this kind of goes against the rest of the
    design scheme.

    At the moment I will plan for users to make composite vectors with the zip function
    can use the zip function to combine the vectors.

    :param vector_types:
    :return:


    @TODO Make a format output object. Can handel which formats are available and their descriptions.
    """

    inputfast_handler_obj = ParseFasta()
    vec_format_obj = VectorFormats()

    parser.add_argument('infiles',
                        nargs='?',
                        type=argparse.FileType('r'),
                        default=sys.stdin)

    parser.add_argument('-o', '--output_format', type=str, required=False,
                        choices=vec_format_obj.getavailableformats(),
                        default=vec_format_obj.getdefaultformat(),
                        help='')

    parser.add_argument('-f', '--input_format', dest="input_format", type=str, required=False,
                        choices=inputfast_handler_obj.getavailableformats(),
                        default=inputfast_handler_obj.getdefaultformat(),
                        help='')

    parser.add_argument("--standard_chars_only",
                        #default=True,
                        action="store_false",
                        help="Fail if a non-standard char is found")


# ======================================================================================================================
#   Amino Acid Descriptors
# ======================================================================================================================


def fasta_to_fasta_vec(parser):
    """

    :return:
    """


def ncomposition_command_line(parser):
    """ Calculates the n-composition of a FASTA sequence (default: amino acid composition).
    # @TODO: Input file as row id. Should be added in

    This can be used to calculate the K-tuple nucleotide composition (PseKNC)

    #Examples:
    $ cat example.fasta
    >test1
    ATGC
    >test2
    CCGG
    >test3
    AAAA
    >test4
    GCGCGCGCGCCCGGCGCGCCGG

    $ vectortools.py ncomp -o TSV -f FASTA -crd , -l 1 -a <(echo "A,T,G,C") example.fasta
    row_title,A,C,G,T
    >test1,0.25,0.25,0.25,0.25
    >test2,0.0,0.5,0.5,0.0
    >test3,1.0,0.0,0.0,0.0
    >test4,0.0,0.5,0.5,0.0

    """

    # Parse input related to fasta files.
    _input_fasta_params(parser)

    # Get standard vector related arguments.
    _shared_params(
        parser,
        enable_column_titles="Generate column-titles in the output file",
        enable_row_titles="Generate row-titles in the output file"
    )

    # Function specific command line arguments.
    parser.add_argument(
        "-l", '--kmerlen',
        type=int,
        default=1,
        choices=range(1, 5),
        help="The length of peptide k-mer to use. 1 = amino acid composition, 2 = dipeptide ...etc.")

    parser.add_argument(
        "-a", '--alphabet',
        #type=file,
        default=None,
        help="Standard 20 amino acids, or a file with a vector containing the alphabet to use in each.")

    # Collect arguments.
    args = parser.parse_args()

    # Store the alphabet used to generate n-composition vectors.
    if args.alphabet is None:
        alphabet = STD_AMINO_ACIDS
    else:
        alphabet = open(args.alphabet).read().strip().split(args.delimiter)
        # alphabet = [i for i in open(args.alphabet).read().strip()]

    # This might help seed up execution.
    from lib.descriptors import NComposition

    # Create a descriptor generating object.
    ncomp_obj = NComposition(args.kmerlen, alphabet, args.roundto)

    # Handle row and column titles.
    out_column_titles = None
    if args.column_titles:
        # Return the column titles.
        out_column_titles = ncomp_obj.getcoltitles()
        if args.row_titles:
            # If we also have row titles offset add a row title to the column titles.
            out_column_titles = [COLUMN_TITLE_FOR_OUTPUT_MATRICES] + out_column_titles

    # @TODO: Add other vector format outputs, should be possible to outputvector.
    out_matrix_obj = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        col_titles=out_column_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=None
    )

    # Set the input format
    fasta_parser_obj = ParseFasta(input_format=args.input_format)

    # Iterate over the fasta entries in the fasta file.
    for fasta_title, fasta_seq in fasta_parser_obj.generatefastaobjects(args.infiles):
        # Calculate N composition of the added sequence.
        # @TODO: Add other vector format outputs, should be possible to output vector.
        out_matrix_obj.iterative_out(
            row_title=_handlefastanametorowname(fasta_title, args.delimiter),
            vector=ncomp_obj.calc(fasta_seq))


def split_ncomposition_command_line(parser):
    """ Calculates the split-n-composition of a FASTA sequence (default: split amino acid composition).
    This function will open and read a amino acid contaning fasta file (.faa)

    Based on "Combining machine learning and homology-based approaches to
    accurately predict subcellular localization in Arabidopsis"
    http://www.ncbi.nlm.nih.gov/pubmed/20647376

    This basically calculates the average of the first X number of aas
    the last x number of aas and the remaining middle portion.
    """
    # The default length to divide the start and stop positions.
    terminal_len = 25
    # Parse input related to fasta files.
    _input_fasta_params(parser)
    # Get standard vector related arguments.
    _shared_params(parser)
    # Function specific command line arguments.

    parser.add_argument("-l", '--kmerlen',
                        type=int,
                        default=1,
                        choices=range(1, 5),
                        help="The number of chars to consider for one feature.")

    parser.add_argument("-a", '--alphabet',
                        default=None,
                        help="A file describing the characters to describe with features. (Default) standard 20 amino acids")

    parser.add_argument("-s", '--start-len',
                        type=int,
                        default=terminal_len,
                        help="N-composition of the first n bases of a fasta.")

    parser.add_argument("-e", '--end-len',
                        type=int,
                        default=terminal_len,
                        help="N-composition of the last n bases of a fasta.")

    args = parser.parse_known_args()[0]

    # Store the alphabet used to generate n-composition vectors.
    if args.alphabet is None:
        alphabet = STD_AMINO_ACIDS
    else:
        alphabet = open(args.alphabet).read().strip().split(args.delimiter)

    from lib.descriptors import SplitNComposition

    split_comp_obj = SplitNComposition(args.kmerlen, alphabet, args.roundto, args.standard_chars_only)

    # Handle row and column titles.
    out_column_titles = None
    if args.column_titles:
        # Return the column titles.
        out_column_titles = split_comp_obj.getcoltitles()
        if args.row_titles:
            # If we also have row titles offset add a row title to the column titles.
            out_column_titles = [COLUMN_TITLE_FOR_OUTPUT_MATRICES] + out_column_titles

    # @TODO: Add other vector format outputs, should be possible to outputvector.
    out_matrix_obj = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        col_titles=out_column_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=None
    )

    # Set the input format
    # @TODO: Add other vector format outputs, should be possible to outputvector.
    fasta_parser_obj = ParseFasta(input_format=args.input_format)
    # Iterate over the fasta entries in the fasta file.
    for fasta_title, fasta_seq in fasta_parser_obj.generatefastaobjects(args.infiles):
        # Calculate split n composition of the added sequence.
        out_matrix_obj.iterative_out(
            row_title=_handlefastanametorowname(fasta_title, args.delimiter),
            vector=split_comp_obj.calc(fasta_seq, args.start_len, args.end_len))

# ======================================================================================================================
#                                               Descriptor Calculators
# ======================================================================================================================
# http://www.ncbi.nlm.nih.gov/pubmed/23426256
# http://code.google.com/p/protpy/
'''
def get_residue_percentate(residue_str, ProteinSequence, entry_len):
    """
    This function takes a string of letters, a dictonary with single letter aa abreviateion keys
    mapping to their occurence in a fasta entry and entry_len - an integer counting the total number of entires.
    in the fasta file.
    """
    residue_count = 0
    for aa in residue_str:
        residue_count += ProteinSequence.count(aa)
    return float(residue_count)/float(entry_len)
'''


# @TODO: Use this in testing http://www.ebi.ac.uk/Tools/seqstats/emboss_pepstats/
def physicochemical_properties_ncomposition_command_line(parser):
    """ Calculates the physico-chemical properties of an amino acid sequence.

    There are two types of features in this descriptor.
        1. % of physicochemical groups, such as % charged_residues. These make up the majority of the descriptor.
        2. Calculation of some physical property such as weight, length, or isoelectric point.

    :param parser:
    :return:
    """
    out_row_titles = None
    out_column_titles = None

    # These data structures define the operations and order to perform them in,
    # It is important to preserve this,  especially when adding column titles.
    # Therefore, this are use to produce column titles and to calculate each feature.
    # defines the physicochemical groups' names and member amino acids.

    # Parse input.
    _input_fasta_params(parser)
    # Handle standard parameters.
    _shared_params(parser)

    args = parser.parse_args()

    from lib.descriptors import PhysicoChemicalProperties

    phys_chem_obj = PhysicoChemicalProperties(args.roundto)

    # Handle row and column titles.
    out_column_titles = None
    if args.column_titles:
        # Return the column titles.
        out_column_titles = phys_chem_obj.getcoltitles()
        if args.row_titles:
            # If we also have row titles offset add a row title to the column titles.
            out_column_titles = [COLUMN_TITLE_FOR_OUTPUT_MATRICES] + out_column_titles

    out_matrix_obj = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        col_titles=out_column_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=None
    )

    # @TODO: Add other vector format outputs, should be possible to outputvector.
    # Instantiate and set the input format
    fasta_parser_obj = ParseFasta(input_format=args.input_format)
    # Start iterating over the fasta file contents.
    for fasta_title, fasta_seq in fasta_parser_obj.generatefastaobjects(args.infiles):

        # Calculate N composition of the added sequence.
        # @TODO: Add other vector format outputs, should be possible to outputvector.
        out_matrix_obj.iterative_out(
            row_title=_handlefastanametorowname(fasta_title, args.delimiter),
            vector=phys_chem_obj.calc(fasta_seq))


def geary_autocorrelation_command_line(parser):
    """ Calculates the Geary Auto Correlation for given amino acid sequences.

    :param parser:
    :return:
    """
    # Parse input.
    _input_fasta_params(parser)

    _shared_params(parser)

    args = parser.parse_args()

    from lib.descriptors import GearyAutocorrelation

    desc_obj = GearyAutocorrelation(args.roundto)

    # Handle row and column titles.
    out_column_titles = None
    if args.column_titles:
        # Return the column titles.
        out_column_titles = desc_obj.getcoltitles()
        if args.row_titles:
            # If we also have row titles offset add a row title to the column titles.
            out_column_titles = [COLUMN_TITLE_FOR_OUTPUT_MATRICES] + out_column_titles

    out_matrix_obj = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        col_titles=out_column_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=None
    )

    # @TODO: Add other vector format outputs, should be possible to outputvector.
    # Instantiate and set the input format
    fasta_parser_obj = ParseFasta(input_format=args.input_format)
    # Start iterating over the fasta file contents.
    for fasta_title, fasta_seq in fasta_parser_obj.generatefastaobjects(args.infiles):
        # Calculate N composition of the added sequence.
        # @TODO: Add other vector format outputs, should be possible to outputvector.
        out_matrix_obj.iterative_out(
            row_title=_handlefastanametorowname(fasta_title, args.delimiter),
            vector=desc_obj.calc(fasta_seq))


def normalized_moreaubroto_autocorrelation_command_line(parser):
    """ Produces features describing Moreau-Broto Auto Correlation of an amino acid sequence.
    :param parser:
    :return:
    """
    # Parse input.
    _input_fasta_params(parser)
    _shared_params(parser)
    args = parser.parse_args()

    from lib.descriptors import NormalizedMoreauBrotoAutocorrelation as DescriptorObj
    desc_obj = DescriptorObj(args.roundto)

    # Handle row and column titles.
    out_column_titles = None
    if args.column_titles:
        # Return the column titles.
        out_column_titles = desc_obj.getcoltitles()
        if args.row_titles:
            # If we also have row titles offset add a row title to the column titles.
            out_column_titles = [COLUMN_TITLE_FOR_OUTPUT_MATRICES] + out_column_titles

    out_matrix_obj = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        col_titles=out_column_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=None
    )

    # @TODO: Add other vector format outputs, should be possible to outputvector.
    # Instantiate and set the input format
    fasta_parser_obj = ParseFasta(input_format=args.input_format)
    # Start iterating over the fasta file contents.
    for fasta_title, fasta_seq in fasta_parser_obj.generatefastaobjects(args.infiles):
        # Calculate N composition of the added sequence.
        # @TODO: Add other vector format outputs, should be possible to outputvector.
        out_matrix_obj.iterative_out(
            row_title=_handlefastanametorowname(fasta_title, args.delimiter),
            vector=desc_obj.calc(fasta_seq))


def moran_autocorrelation_command_line(parser):
    """ Produces features describing Geary Auto Correlation of an amino acid sequence.
    :param parser:
    :return:
    """
    # Parse input.
    _input_fasta_params(parser)
    _shared_params(parser)
    args = parser.parse_args()

    from lib.descriptors import MoranAutocorrelation as DescriptorObj
    desc_obj = DescriptorObj(args.roundto)

    # Handle row and column titles.
    out_column_titles = None
    if args.column_titles:
        # Return the column titles.
        out_column_titles = desc_obj.getcoltitles()
        if args.row_titles:
            # If we also have row titles offset add a row title to the column titles.
            out_column_titles = [COLUMN_TITLE_FOR_OUTPUT_MATRICES] + out_column_titles

    out_matrix_obj = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        col_titles=out_column_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=None
    )

    # @TODO: Add other vector format outputs, should be possible to outputvector.
    # Instantiate and set the input format
    fasta_parser_obj = ParseFasta(input_format=args.input_format)
    # Start iterating over the fasta file contents.
    for fasta_title, fasta_seq in fasta_parser_obj.generatefastaobjects(args.infiles):
        # Calculate N composition of the added sequence.
        # @TODO: Add other vector format outputs, should be possible to outputvector.
        out_matrix_obj.iterative_out(
            row_title=_handlefastanametorowname(fasta_title, args.delimiter),
            vector=desc_obj.calc(fasta_seq))


def pseudo_amino_acid_composition_command_line(parser):
    """ Produces features describing Geary Auto Correlation of an amino acid sequence.
    :param parser:
    :return:
    """
    # Parse input.
    _input_fasta_params(parser)
    _shared_params(parser)
    args = parser.parse_args()

    from lib.descriptors import PseudoAminoAcidComposition as DescriptorObj
    desc_obj = DescriptorObj(args.roundto)

    # Handle row and column titles.
    out_column_titles = None
    if args.column_titles:
        # Return the column titles.
        out_column_titles = desc_obj.getcoltitles()
        if args.row_titles:
            # If we also have row titles offset add a row title to the column titles.
            out_column_titles = [COLUMN_TITLE_FOR_OUTPUT_MATRICES] + out_column_titles

    out_matrix_obj = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        col_titles=out_column_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=None
    )

    # @TODO: Add other vector format outputs, should be possible to outputvector.
    # Instantiate and set the input format
    fasta_parser_obj = ParseFasta(input_format=args.input_format)
    # Start iterating over the fasta file contents.
    for fasta_title, fasta_seq in fasta_parser_obj.generatefastaobjects(args.infiles):
        # Calculate N composition of the added sequence.
        # @TODO: Add other vector format outputs, should be possible to outputvector.
        out_matrix_obj.iterative_out(
            row_title=_handlefastanametorowname(fasta_title, args.delimiter),
            vector=desc_obj.calc(fasta_seq))


def sequence_order_coupling_number_total_command_line(parser):
    """ Calculates the sequence order coupling number of an amino acid sequence.

    :param parser:
    :return:
    """

    # Parse input.
    _input_fasta_params(parser)
    _shared_params(parser)
    args = parser.parse_args()

    from lib.descriptors import SequenceOrderCouplingNumberTotal as DescriptorObj
    desc_obj = DescriptorObj(args.roundto)

    # Handle row and column titles.
    out_column_titles = None
    if args.column_titles:
        # Return the column titles.
        out_column_titles = desc_obj.getcoltitles()
        if args.row_titles:
            # If we also have row titles offset add a row title to the column titles.
            out_column_titles = [COLUMN_TITLE_FOR_OUTPUT_MATRICES] + out_column_titles

    out_matrix_obj = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        col_titles=out_column_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=None
    )

    # @TODO: Add other vector format outputs, should be possible to outputvector.
    # Instantiate and set the input format
    fasta_parser_obj = ParseFasta(input_format=args.input_format)
    # Start iterating over the fasta file contents.
    for fasta_title, fasta_seq in fasta_parser_obj.generatefastaobjects(args.infiles):
        # Calculate N composition of the added sequence.
        # @TODO: Add other vector format outputs, should be possible to outputvector.
        out_matrix_obj.iterative_out(
            row_title=_handlefastanametorowname(fasta_title, args.delimiter),
            vector=desc_obj.calc(fasta_seq))


def quasi_sequence_order_command_line(parser):
    """ Calculates the quasi sequence order coupling number of an amino acid sequence.

    :param parser:
    :return:
    """
    """ Produces features describing Geary Auto Correlation of an amino acid sequence.
    :param parser:
    :return:
    """
    # Parse input.
    _input_fasta_params(parser)
    _shared_params(parser)
    args = parser.parse_args()

    from lib.descriptors import QuasiSequenceOrder as DescriptorObj
    desc_obj = DescriptorObj(args.roundto)

    # Handle row and column titles.
    out_column_titles = None
    if args.column_titles:
        # Return the column titles.
        out_column_titles = desc_obj.getcoltitles()
        if args.row_titles:
            # If we also have row titles offset add a row title to the column titles.
            out_column_titles = [COLUMN_TITLE_FOR_OUTPUT_MATRICES] + out_column_titles

    out_matrix_obj = ParseVectors(
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        col_titles=out_column_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=None
    )

    # @TODO: Add other vector format outputs, should be possible to outputvector.
    # Instantiate and set the input format
    fasta_parser_obj = ParseFasta(input_format=args.input_format)
    # Start iterating over the fasta file contents.
    for fasta_title, fasta_seq in fasta_parser_obj.generatefastaobjects(args.infiles):
        # Calculate N composition of the added sequence.
        # @TODO: Add other vector format outputs, should be possible to outputvector.
        out_matrix_obj.iterative_out(
            row_title=_handlefastanametorowname(fasta_title, args.delimiter),
            vector=desc_obj.calc(fasta_seq))


# ======================================================================================================================
# Nucleic Acid Descriptors.
# ======================================================================================================================
# http://bioinformatics.oxfordjournals.org/content/early/2015/01/12/bioinformatics.btu857.short


def bilinearindices(parse):
    # @TODO: Implement this...
    # This might work for nucleic acids too.
    # http://onlinelibrary.wiley.com/doi/10.1111/j.1742-4658.2010.07711.x/full
    x = 0

