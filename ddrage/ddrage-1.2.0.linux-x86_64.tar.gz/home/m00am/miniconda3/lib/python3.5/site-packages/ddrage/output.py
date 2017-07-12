# -*- Coding: utf-8 -*-
"""This module handles all textual output, including logfiles and FASTQ files.

Additionally FASTQ-specific information like CASAVA lines are created here.
"""
import os
import sys
import random
import datetime
from collections import defaultdict, Counter

import numpy as np
from yaml import dump
from yaml import CDumper as Dumper

from . import plotting


def format_args(args):
    """Fallback function to format args."""
    template = "{:<30}{:>30}{:>30}"
    headline = template.format("key", "value", "type")
    bar = 90*"-"
    out = [headline, bar]
    for key, value  in vars(args).items():
        out.append(template.format(key, repr(value), str(type(value)).split("'")[1]))
    return "\n".join(out)
    
def show_args(args, file=sys.stdout):
    """Fallback function to print the arguments if printargs is not installed."""
    print(format_args(args), file=sys.stdout)


class Paths(dict):
    """Class to allow attribute access to paths."""
    def __getattr__(self, attribute):
        return self.get(attribute)

    __setattr__ = dict.__setitem__

    __delattr__ = dict.__delitem__


class Stats(dict):
    """Class to allow attribute access to stats."""
    def __getattr__(self, attribute):
        return self.get(attribute)

    __setattr__ = dict.__setitem__

    __delattr__ = dict.__delitem__


def plot_order(x):
    """Sorting function to ensure the same order of counts.

    The order is:
    
        - 0: 'common'
        - 1: 'SNP homozygous'
        - 2: 'SNP heterozygous'
        - 3: 'indels homozygous'
        - 4: 'indels heterozygous'
        - 3: 'mutation homozygous'
        - 4: 'mutation heterozygous'
        - 5: 'dropout'

    Arguments:
        tuple(key, value): Name and counts.

    Returns:
        int: The sorting value for the key. See above.
    """
    key, _ = x
    if key == "common":
        return 0
    elif key == "SNP homozygous":
        return 1
    elif key == "SNP heterozygous":
        return 2
    elif key == "indels homozygous":
        return 3
    elif key == "indels heterozygous":
        return 4
    elif key == "mutation homozygous":
        return 5
    elif key == "mutation heterozygous":
        return 6
    elif key == "dropout":
        return 7
    else:
        raise ValueError("Unexpected key {}. ".format(key))


def assemble_casava_line(p7_bc, meta_info):
    """Return two casava-style name lines as bytes.

    These include all the information from meta info and the given p7 barcode.

    Arguments:
        p7_bc (str): The p7 barcode used in the file.
        meta_info (list): List of modifications added to the read in the
            modification / mutation step. Has to be joinable by ', '

    Returns:
        tuple(bytes, bytes): A p5 and a p7 name line for the read.
    """
    # prepare a template for a casava line
    casava_line = "{}:{}:{}:{}:{}:{}:{} {}:{}:{}:{} " + " ".join(meta_info)
    # randomize run and lane numbers
    run = random.randint(0, 100)
    lane = random.randint(0, 100)
    # fill the line template
    p5_line = casava_line.format("instrument", run, 42, lane, 23, 0, 0, 1, "N", 4711, p7_bc.decode())
    p7_line = casava_line.format("instrument", run, 42, lane, 23, 0, 0, 2, "N", 4711, p7_bc.decode())
    return p5_line.encode(), p7_line.encode()


def generate_file_name(p7_bc, output_path_prefix, name):
    """Generate a useful filename and create the necessary folders.

    Arguments:
        p7_bc (str): p7 barcode used to create the reads.
        output_path_prefix (str): Prefix for output folders. Default: rage base folder
        name (str): name for the test dataset.

    Returns:
        tuple: Paths object (dict with attribute access) containing paths for
        the fastq files, the tsv files, the gt file
        and the annotation and log files as well as the path for the annotation folder.
    """
    # save the date and time for automatics naming of the data set    
    now = datetime.datetime.now().isoformat().rsplit(".", 1)[0]  # this is ISO compliant 
    paths = Paths()

    # make sure a useful default name is there
    if name == None:
        name = "RAGEdataset"


    if not output_path_prefix:
        # if no prefix has been given, use the default
        paths.base_folder = "{}_{}".format(now, name)
    else:
        # use the given prefix
        prefix = output_path_prefix.rstrip(os.path.sep)
        paths.base_folder = prefix

    paths.basename = os.path.join(paths.base_folder, "{}_{}".format(name, p7_bc))
    paths.annotation_folder = os.path.join(paths.base_folder, "logs")

    paths.p5 = paths.basename + "_1.fastq"
    paths.p7 = paths.basename + "_2.fastq"
    paths.ground_truth = paths.basename + "_gt.yaml"
    paths.annotation = os.path.join(paths.annotation_folder, "{}_{}_annotation.txt".format(name, p7_bc))
    paths.statistics = os.path.join(paths.annotation_folder, "{}_{}_statstics.pdf".format(name, p7_bc))

    # create folders if necessary
    for folder in (paths.base_folder, paths.annotation_folder):
        if folder and not os.path.exists(folder):
            os.makedirs(folder)

    return paths


def assemble_statistic_data(stats, conf, args, loci):
    """Compute statistics for the data set that will later be plotted and written to file.

    Arguments:
        stats (Stats, Namespace like dict): Statistics will be saved to this object in place.
        conf (Conf, Namespace like dict): Configuration used to create the initial read. Ruturned by the ``create_perfect_reads`` function.
        args (Argparse Namespace): User defined parameters.
        loci (iterable of Locus): The created valid loci.

    Returns:
        None: All results are added to the stats dict.
    """
    ####################################################
    # data collection phase
    ####################################################
    stats.total_pcr_copies = stats.nr_valid_pcr_copies + stats.singleton_pcr_copies + stats.hrl_pcr_copies
    # small datasets can be created without valid reads.
    # this is an unlikely edge case, but a dataset without valid
    # reads can be created. This results in divison by zero and has to be corrected
    try:
        stats.total_pcr_copy_rate = stats.total_pcr_copies / stats.nr_total_reads
    except ZeroDivisionError:
        stats.total_pcr_copy_rate = 0.0
    try:
        stats.valid_pcr_copy_rate = stats.nr_valid_pcr_copies / stats.nr_total_valid_reads
    except ZeroDivisionError:
        stats.valid_pcr_copy_rate = 0.0
    # Handle cases with no singleton. prevent division by zero
    try:
        stats.singleton_pcr_copy_rate = stats.singleton_pcr_copies/stats.total_singleton_reads
    except ZeroDivisionError:
        stats.singleton_pcr_copy_rate = 0.0
    # Handle cases with no HRL. prevent division by zero
    try:
        stats.hrl_pcr_copy_rate = stats.hrl_pcr_copies/stats.total_hrl_reads
    except ZeroDivisionError:
        stats.hrl_pcr_copy_rate = 0.0

    # collect individual and dataset wide information
    stats.all_individual_names = sorted(loci[0].get_individual_names())
    stats.nr_individuals = len(stats.all_individual_names)
    stats.nr_loci = args.nr_loci
    stats.valid_coverage_distribution = Counter()

    # initialize dict for the collection of locus types per individual
    assigned_types = defaultdict(lambda: Counter({"common": 0, "mutation heterozygous": 0, "mutation homozygous": 0, "dropout": 0}))
    # initialize tallies for many types of events to be counted in the created data
    stats.mutation_count_total_tally = Counter()
    mutation_event_individual_tally = Counter()
    mutation_count_individual_tally = Counter()
    na_by_mut_individual_tally = Counter()
    alleles_per_locus = Counter()
    allele_frequencies = []
    max_allele_number = 0
    
    # collect counts and assigned types from each locus
    for locus in loci:
        # transfer results into dictionary for easier access in later steps
        for individual, locus_type in locus.assigned_types.items():
            assigned_types[individual][locus_type] += 1
    

        stats.valid_coverage_distribution.update(locus.get_individual_coverage())
        # add locus tally for type by individual to total tally
        na_by_mut_tally = locus.get_null_allele_counts()
        na_by_mut_individual_tally.update(na_by_mut_tally)
        
        # if at least one individual has a mutation at this locus
        # count events (Ind_n has mutations at Locus_m)
        # and number of the mutations (Ind_n has x deviating bases)
        # at the locus, summing up to a total of y for all loci)
        if locus.mutations_added:
            nr_of_mutations_per_individual = locus.get_number_of_mutations_per_ind()
            stats.mutation_count_total_tally.update(nr_of_mutations_per_individual)
            for name, count in nr_of_mutations_per_individual.items():
                if count:
                    mutation_event_individual_tally[name] += 1
                    mutation_count_individual_tally[name] += count

        allele_frequency, _ = locus.get_allele_frequency()
        allele_frequencies.append(allele_frequency)
        if locus.mutation_model:
            max_allele_number = max(max_allele_number, len(locus.mutation_model.alleles))
        
        if locus.mutations_added:
            nr_alleles = len(allele_frequency.keys())
            alleles_per_locus[nr_alleles] += 1
        else:
            alleles_per_locus[1] += 1
    stats.alleles_per_locus = alleles_per_locus
    normalized_frequencies = np.zeros((max_allele_number, len(loci)))
    for locus_index, freq in enumerate(allele_frequencies):
        for allele_index in range(max_allele_number):
            try:
                frequency = freq[allele_index][2]
            except KeyError:
                frequency = 0
            normalized_frequencies[allele_index][locus_index] = frequency
    stats.allele_frequencies = normalized_frequencies

    # add missing individual names to the mutation counter
    for name in sorted(stats.all_individual_names):
        if name not in stats.mutation_count_total_tally:
            stats.mutation_count_total_tally[name] = 0
    # compute mean nr of mutations per individual
    stats.mean_mutations_per_individual = dict()
    for name in sorted(stats.all_individual_names):
        try:
            events = mutation_event_individual_tally[name]
            total_mutations = mutation_count_individual_tally[name]
            mean = total_mutations / events
            stats.mean_mutations_per_individual[name] = mean
        except KeyError:
            # catch cases where an individual has no entries 
            # in either counter
            stats.mean_mutations_per_individual[name] = 0
        except ZeroDivisionError:
            # catch cases in which there are entries, but the
            # total events are zero.
            stats.mean_mutations_per_individual[name] = 0
    # compute total mean mutation number
    total_mutation_events = sum(mutation_event_individual_tally.values())
    total_mutation_mutations = sum(mutation_count_individual_tally.values())
    if total_mutation_events:
        stats.total_mutations_mean = total_mutation_mutations / total_mutation_events
    else:
        stats.total_mutations_mean = 0

    ####################################################
    # processing phase
    ####################################################
    # sort counts for all individuals by individual name
    sorted_assigned_types = sorted(assigned_types.items(), key=lambda x: x[0])
    individual_names, individual_type_counts = zip(*[(name, counts) for name, counts in sorted_assigned_types])
    # transposed information for hbar plotting
    all_common_counts = []
    all_mutation_counts_homozygous = []
    all_mutation_counts_heterozygous = []
    all_dropout_counts = []
    # group all counts together for easier handling
    # this variable is never accessed, but the contained 
    # lists are used for the plotting
    stats.transposed_type_counts = {
        "common": all_common_counts,
        "mutation homozygous": all_mutation_counts_homozygous,
        "mutation heterozygous": all_mutation_counts_heterozygous,
        "dropout": all_dropout_counts,
    }
    
    stats.locus_type_labels = individual_names
    # transpose the counts so that they can be used in a hbar plot
    # this requires a list of all counts of the same type for all individuals
    for counts in individual_type_counts:
        for locus_type, count in sorted(counts.items(), key=plot_order):
            stats.transposed_type_counts[locus_type].append(count)

    # assemble total counts
    # save as reversed list for more intuitive ordering of results
    stats.total_type_count_labels = list(reversed(["common", "mutation homozygous", "mutation heterozygous", "dropout"]))
    stats.total_type_counts = list(reversed([sum(all_common_counts), sum(all_mutation_counts_homozygous), sum(all_mutation_counts_heterozygous), sum(all_dropout_counts)]))

    # compute pcr copy numbers
    stats.pcr_copy_rates = [stats.singleton_pcr_copy_rate, stats.hrl_pcr_copy_rate, stats.valid_pcr_copy_rate, stats.total_pcr_copy_rate]
    stats.valid_read_rates = [1 - pcr_copy_rate for pcr_copy_rate in stats.pcr_copy_rates]

    # compute read origin breakdown
    # save as reversed list for more intuitive ordering of results
    # stats.read_origin_labels = list(reversed(["Valid Reads", "PCR Duplicates\nof Valid Reads", "Singletons", "PCR Duplicates\nof Singletons", "HRL Reads", "PCR Duplicates\nof HRL Reads"])) 
    stats.read_origin_labels = list(reversed(["Valid Reads", "PCR Duplicates of Valid Reads", "Singletons", "PCR Duplicates of Singletons", "HRL Reads", "PCR Duplicates of HRL Reads"])) 
    stats.read_origin_counts = list(reversed([stats.nr_total_valid_reads, stats.nr_valid_pcr_copies, stats.total_singleton_reads, stats.singleton_pcr_copies, stats.total_hrl_reads, stats.hrl_pcr_copies]))

    # Compute total number of mutations per individual
    # sort counts for all individuals by individual name
    # and retireve individual names as tick labels
    # If no mutations occured, set 0 as a sentinel value and use names
    # from an earlier step as labels.
    if stats.mutation_count_total_tally:
        sorted_mutation_tally = sorted(stats.mutation_count_total_tally.items(), key=lambda x: x[0])
        stats.individual_total_mutations_labels, stats.individual_total_mutations = zip(*[(name, counts) for name, counts in sorted_mutation_tally])
    else:
        stats.individual_total_mutations_labels, stats.individual_total_mutations = (stats.all_individual_names, [0 for _ in stats.all_individual_names])

    # compute mean number of mutations per mutation event
    # If no mutations occured, set 0 as a sentinel value and use names
    # from an earlier step as labels.
    if stats.mean_mutations_per_individual:
        sorted_mean_sizes = sorted(stats.mean_mutations_per_individual.items(), key=lambda x: x[0])
        stats.mean_mutations_labels, stats.mean_mutations_per_event = zip(*[(name, mean) for name, mean in sorted_mean_sizes])
    else:
        stats.mean_mutations_labels, stats.mean_mutations_per_event = (stats.all_individual_names, [0 for _ in stats.all_individual_names])
    # Note: stats.total_mutations_mean has already been set above

    # compute number of null alleles
    sorted_mut_tally = sorted(na_by_mut_individual_tally.items(), key=lambda x: x[0])
    stats.null_allele_labels, stats.na_mut_individual_tally = zip(*[(name, counts) for name, counts in sorted_mut_tally])


def assemble_annotation(stats, conf, args):
    """Aggregate information for annotation file.

    Arguments:
        stats (dict): Containing statistics like total nr of reads etc.
        conf (dict): Containing the configuration used to create the reads.
        args (Argparse Namespace): User parameters.

    Returns:
        list: containing a string for each line in the annotation file.
    """
    annotation = ["Configuration"]
    for key, value in sorted(conf.items()):
        if key == "individual names":
            annotation.append("{:<25}{:>20}".format(key, value[0]))
            annotation.extend(["{:>45}".format(individual) for individual in value[1:] ])
        elif key in ("individuals matrix", "individuals"):
            pass
        elif isinstance(value, bytes):
            annotation.append("{:<25}{:>20}".format(key, value.decode()))
        else:
            annotation.append("{:<25}{:>20}".format(key, str(value)))
    annotation += ["\n\nStatistics:"]
    # compile total read info
    annotation += ["\nTotal:"]
    annotation += ["{:<25}{:>20}".format("total reads", stats.nr_total_reads)]
    annotation += ["{:<25}{:>20}".format("pcr copies", stats.total_pcr_copies)]
    annotation += ["{:<25}{:>20.2f}".format("pcr copy rate", stats.total_pcr_copy_rate)]
    # compile read info for valid reads (Singletons, HRL)
    annotation += ["\nOnly Valid Reads (Without Singletons and HRL reads):"]
    annotation += ["{:<25}{:>20}".format("locus reads", stats.nr_total_valid_reads)]
    annotation += ["{:<25}{:>20}".format("pcr copies", stats.nr_valid_pcr_copies)]
    annotation += ["{:<25}{:>20.2f}".format("pcr copy rate", stats.valid_pcr_copy_rate)]
    # compile read info singletons only
    annotation += ["\nOnly Singletons:"]
    annotation += ["{:<25}{:>20}".format("singletons", stats.total_singleton_reads)]
    annotation += ["{:<25}{:>20}".format("pcr copies", stats.singleton_pcr_copies)]
    annotation += ["{:<25}{:>20.2f}".format("pcr copy rate", stats.singleton_pcr_copy_rate)]
    # compile read info HRL reads only
    annotation += ["\nOnly HRL Reads:"]
    annotation += ["{:<25}{:>20}".format("HRL reads", stats.total_hrl_reads)]
    annotation += ["{:<25}{:>20}".format("pcr copies", stats.hrl_pcr_copies)]
    annotation += ["{:<25}{:>20.2f}".format("pcr copy rate", stats.hrl_pcr_copy_rate)]
    # add matrix of all possible individuals
    annotation += "\n"
    annotation.append(conf["individuals matrix"])

    annotation += "\n"
    annotation.append(format_args(args))
    return annotation


def print_annotation(stats, conf, args):
    """Print the assembled annotation."""
    conf_file = assemble_annotation(stats, conf, args)
    print("\n".join(conf_file))


def write_annotation_file(stats, conf, args, path_annotation):
    """Create and write an annotation file for this run of RAGE.

    Arguments:
        stats (dict): Containing statistics like total nr of reads etc.
        conf (dict): Containing overhangs, rec sites, dbr, etc.
        args (Argparse Namespace):
        path_annotation (str): Path where the annotation file
            will be written to.
    """
    conf_file = assemble_annotation(stats, conf, args)
    with open(path_annotation, 'w') as annotation_file:
        annotation_file.write("\n".join(conf_file))
        annotation_file.write("\n")


def write_ground_truth(loci, paths, args):
    """Write a ground truth yaml file from the genrated loci.

    Arguments:
        loci (iterable of RADLocus): Generated (and burned) loci.
        paths (argparse.Namespace like): Paths to all output files.
    """
    try:
        chunksize = args.yaml_chunksize  
    except AttributeError:
        chunksize = 1000

    with open(paths.ground_truth, 'a') as gt_file:
        # initialize output dict
        outdata = dict()
        chunk_ticks = 0
        
        # assemble list of individual info
        # like auxiliary seqeunces,and add the to the dataset
        meta_info = dict()
        for (barcode_p5, barcode_p7), (spacer_p5, spacer_p7, individual_name, *_) in loci[0].individuals:
            ind_name = individual_name
            meta_info[ind_name] = dict()
            meta_info[ind_name]["p5 bc"] = barcode_p5.decode()
            meta_info[ind_name]["p7 bc"] = barcode_p7.decode()
            meta_info[ind_name]["p5 spacer"] = spacer_p5.decode()
            meta_info[ind_name]["p7 spacer"] = spacer_p7.decode()
            meta_info[ind_name]["dbr"] = args.dbr.decode()
            meta_info[ind_name]["p5 overhang"] = args.p5_overhang.decode()
            meta_info[ind_name]["p7 overhang"] = args.p7_overhang.decode()
        outdata["Individual Information"] = meta_info
        gt_file.write(dump(outdata, default_flow_style=False, Dumper=Dumper, explicit_start=True))

        chunk_nr = 0
        outdata = dict()
        for locus in loci:
            # add output data to the dict for the active chunk
            # this could all happen in one big dict but is chunked
            # to avoid memory overflow
            outdata["Locus {}".format(locus.locus_name)] = locus.yaml_entry()
            # handle chunked writing,
            # check if the chunk is full, if so write
            # and reset the output dictionary
            # if not, continue
            chunk_ticks += 1
            if chunk_ticks == chunksize:
                if chunk_nr != 0:
                    gt_file.write(dump(outdata, default_flow_style=False, Dumper=Dumper))
                else:
                    gt_file.write(dump(outdata, default_flow_style=False, Dumper=Dumper, explicit_start=True))
                outdata = dict()

        # write the remaining entries to file that did 
        # not fit into a full chunk
        if chunk_ticks != 0:
            if chunk_nr != 0:
                gt_file.write(dump(outdata, default_flow_style=False, Dumper=Dumper))
            else:
                gt_file.write(dump(outdata, default_flow_style=False, Dumper=Dumper, explicit_start=True))


def append_hrls_to_ground_truth(hrl_gen, paths):
    """Write the coverages of HRL loci to yaml file.

    Arguments:
        hrl_gen (postprpcessing.HRLGenerator): HRL generator that has been depleted of reads.
        paths (argparse.Namespace like): Paths to all output files.
    """
    with open(paths.ground_truth, 'a') as gt_file:
        hrls = hrl_gen.hrl_coverages
        # Only write hrl coverages if HRL loci are actually in there.
        # Otherwise this might create invalid YAML files.
        if hrls:
            gt_file.write(dump(hrls, default_flow_style=False, Dumper=Dumper, explicit_start=True))


def write_fastq_files(read_pairs, path_p5, path_p7):
    """Write read pairs to fastq_files.
    
    Arguments:
        read_pairs (list): Containing read pairs as tuples of FASTQ entries.
        path_p5 (str): Path where the p5 file will be written to.
        path_p7 (str): Path where the p7 file will be written to.
    """
    with open(path_p5, "wb") as fqw_p5, open(path_p7, "wb") as fqw_p7:
        for p5_read, p7_read in read_pairs:
            seq, name, qual = p5_read
            line = b'@' + name + b'\n' + seq + b'\n+\n' + qual + b'\n'
            fqw_p5.write(line)
            seq, name, qual = p7_read
            line = b'@' + name + b'\n' + seq + b'\n+\n' + qual + b'\n'
            fqw_p7.write(line)


def append_to_fastq_files(read_pairs, path_p5, path_p7):
    """Write read pairs to fastq_files.
    
    Arguments:
        read_pairs (list): Containing read pairs as tuples of FASTQ entries.
        path_p5 (str): Path where the p5 file will be written to.
        path_p7 (str): Path where the p7 file will be written to.
    """
    with open(path_p5, "ab") as fqw_p5, open(path_p7, "ab") as fqw_p7:
        for p5_read, p7_read in read_pairs:
            seq, name, qual = p5_read
            line = b'@' + name + b'\n' + seq + b'\n+\n' + qual + b'\n'
            fqw_p5.write(line)
            seq, name, qual = p7_read
            line = b'@' + name + b'\n' + seq + b'\n+\n' + qual + b'\n'
            fqw_p7.write(line)


def write_user_output(stats, conf, args, paths):
    """Print output for user.

    Arguments:
        stats (dict): Containing statistics like total nr of reads etc.
        conf (dict): Containing the configuration used to create the reads.
        args (Argparse Namespace): User defined parameters.
        paths (Paths): Dictlike object containing all target paths for the output files.
    """
    if args.verbosity >= 2:
        print("\nParameters:")
        print_annotation(stats, conf, args)
    print("\nCreated output files:")
    print("    {:<25}".format("p5 reads"), paths.p5)
    print("    {:<25}".format("p7 reads"), paths.p7)
    print("    {:<25}".format("ground truth"), paths.ground_truth)
    print("    {:<25}".format("annotation file"), paths.annotation)
    print("    {:<25}".format("statistics file"), paths.statistics)


def assemble_overview_data(stats, conf, args, paths, loci):
    plotting.plot_statistics(stats, conf, args, paths, loci)
