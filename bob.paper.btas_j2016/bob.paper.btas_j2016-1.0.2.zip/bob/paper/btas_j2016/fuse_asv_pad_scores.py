#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Mon 8 Oct 14:09:22 CEST 2015
#

from __future__ import print_function

"""This script fuses the scores of an Automatic Speaker Verification System (ASV)
    with scores from a Presentation Attack Detection (PAD) system"""

import bob.measure
import bob.io.base

from ..utils import scores

import argparse
import numpy
import os
import os.path
import sys

from antispoofing.fusion import score_fusion
from antispoofing.utils.ml import ScoreNormalization

import bob.core
logger = bob.core.log.setup("bob.spoof.speech")


def command_line_arguments(command_line_parameters):
    """Parse the program options"""

    basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
    OUTPUT_DIR = os.path.join(basedir, 'fused_scores')

    # set up command line parser
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('-p', '--pad-scores-dir', metavar='DIR', type=str, required=True,
                        help="The directory with all scores (train, dev, and eval sets) by anti-spoofing system.")
    parser.add_argument('-e', '--asv-scores-dir', metavar='DIR', type=str, required=True,
                        help="The directory with all scores (train, dev, and eval sets) by verification system.")
    parser.add_argument('-a', '--attack-type', type=str, default='all',
                        help="The types of attack  file with attacks scores (defaults to '%defaults)s'.")
    parser.add_argument('-o', '--out-directory', metavar='DIR', type=str, default=OUTPUT_DIR,
                        help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
    parser.add_argument('-s', '--support', required=False, type=str, default="all", help="Type of attack.")
    parser.add_argument('-k', '--attackdevice', required=False, type=str, default="all", help="Attack device.")
    parser.add_argument('-r', '--device', required=False, type=str, default="all", help="Recording device.")
    parser.add_argument('-n', '--session', required=False, type=str, default="all", help="Recording session.")


    # add verbose option
    bob.core.log.add_command_line_option(parser)

    # parse arguments
    args = parser.parse_args(command_line_parameters)

    # set verbosity level
    bob.core.log.set_verbosity_level(logger, args.verbose)

    return args


def main(command_line_parameters=None):
    """Reads score files, computes error measures and plots curves."""

    args = command_line_arguments(command_line_parameters)

    if not os.path.exists(args.out_directory):
        os.makedirs(args.out_directory)

    groups = ['train', 'dev', 'eval']

    # read all scores into a single dictionary structure
    all_scores = scores.accumulate_scores(args.pad_scores_dir, args.asv_scores_dir, args.support, args.attackdevice, args.device)

    if not all_scores:
        return

    ####################
    ## Train Model ###
    ####################

    # PAD system scores first
    # all train scores for PAD (there are no zero imposter here)
    pad_train = numpy.append(numpy.asarray(all_scores['pad']['train']['attack'].values(), dtype=numpy.float64),
                             numpy.asarray(all_scores['pad']['train']['real'].values(), dtype=numpy.float64))

    pad_train_norm_stats = ScoreNormalization(pad_train)
    # print ("pad_train_norm_stats ", str(pad_train_norm_stats))

    # asv system scores first
    # all train attack and zero imposter scores
    asv_train = numpy.append(numpy.asarray(all_scores['asv']['train']['attack'].values(), dtype=numpy.float64),
                             numpy.asarray(all_scores['asv']['train']['zimp'].values(), dtype=numpy.float64))
    asv_train = numpy.append(asv_train, numpy.asarray(all_scores['asv']['train']['real'].values(), dtype=numpy.float64))

    asv_train_norm_stats = ScoreNormalization(asv_train)
    # print ("asv_train_norm_stats ", str(asv_train_norm_stats))

    scores_mean = numpy.asarray([asv_train_norm_stats.avg, pad_train_norm_stats.avg], dtype=numpy.float64)
    scores_std = numpy.asarray([asv_train_norm_stats.std, pad_train_norm_stats.std], dtype=numpy.float64)

    # asv_train_pos_norm = numpy.asarray(asv_train_norm_stats.calculateZNorm(asv_train_pos), dtype=numpy.float64)
    # asv_train_neg_norm = numpy.asarray(asv_train_norm_stats.calculateZNorm(asv_train), dtype=numpy.float64)

    # prepare training scores for fusion
    # a single feature vector for LLR machine will be a pair of values (asv, pad), one an asv score and one pad score

    # our keys in dictionaries are of a form id_client+id_probe+file_name, and for each asv pair
    # we need to find value in pad scores that corresponds the filename of prob_id - it's complicated
    # also, we normalize the scores using stats found earlier
    # [print(asvkey,asvval) for asvkey,asvval in all_scores['asv']['train']['real'].items()]
    train_real = [(asvval, all_scores['pad']['train']['real'][asvkey[3:6] + asvkey[3:]])
                  for asvkey, asvval in all_scores['asv']['train']['real'].items()]
    train_real = numpy.asarray(train_real, dtype=numpy.float64)
    train_real -= scores_mean
    train_real = numpy.divide(train_real, scores_std)
    # print ("train_real shape: %s, max: %s, min: %s" %(train_real.shape, str(train_real.min(axis=0)), str(train_real.max(axis=0))))

    # for zero-imposters it is similar but in PAD, there are no zero-imposters - they are basically real scores
    train_zimp = [(asvval, all_scores['pad']['train']['real'][asvkey[3:6] + asvkey[3:]])
                  for asvkey, asvval in all_scores['asv']['train']['zimp'].items()]
    train_zimp = numpy.asarray(train_zimp, dtype=numpy.float64)
    train_zimp -= scores_mean
    train_zimp = numpy.divide(train_zimp, scores_std)
    # print ("train_zimp ", train_zimp.shape)

    # for attack scores, it is the same as for real scores
    train_attack = [(asvval, all_scores['pad']['train']['attack'][asvkey[3:6] + asvkey[3:]])
                    for asvkey, asvval in all_scores['asv']['train']['attack'].items()]
    train_attack = numpy.asarray(train_attack, dtype=numpy.float64)
    train_attack -= scores_mean
    train_attack = numpy.divide(train_attack, scores_std)
    # print ("train_attack ", train_attack.shape)

    # negative features are all attacks and zero-imposters scores, while positive - all genuine scores

    fusion_machine = score_fusion.LLRFusion()
    fusion_machine.train(trainer_scores=(train_real, numpy.concatenate((train_zimp, train_attack), axis=0)))

    fusion_machine.get_machine().input_subtract = scores_mean
    fusion_machine.get_machine().input_divide = scores_std
    # print ("fusion_machine weights: ", fusion_machine.get_machine().weights)

    # save trained machine
    outfile = bob.io.base.HDF5File(os.path.join(args.out_directory, 'llr_fusion_machine.hdf5'), 'w')
    fusion_machine.get_machine().save(outfile)

    # training is done, compute and save scores for the dev and eval groups now
    for group in groups:
        scores_real = [{asvkey: (asvval, all_scores['pad'][group]['real'][asvkey[3:6] + asvkey[3:]])}
                       for asvkey, asvval in all_scores['asv'][group]['real'].items()]
        scores_zimp = [{asvkey: (asvval, all_scores['pad'][group]['real'][asvkey[3:6] + asvkey[3:]])}
                       for asvkey, asvval in all_scores['asv'][group]['zimp'].items()]  # only asv has zimp scores
        scores_attack = [{asvkey: (asvval, all_scores['pad'][group]['attack'][asvkey[3:6] + asvkey[3:]])}
                         for asvkey, asvval in all_scores['asv'][group]['attack'].items()]

        scores_licit = scores_real + scores_zimp

        f = open(os.path.join(args.out_directory, 'scores-' + group + '-fused-real'), 'w')
        for item in scores_licit:
            projection = fusion_machine(item.values()[0])
            key = item.keys()[0]
            f.write("%s %s %s %f\n" % (key[0:3], key[3:6], key[6:], projection))
        f.close()
        f = open(os.path.join(args.out_directory, 'scores-' + group + '-fused-attack'), 'w')
        for item in scores_real:
            projection = fusion_machine(item.values()[0])
            key = item.keys()[0]
            f.write("%s %s %s %f\n" % (key[0:3], key[3:6], key[6:], projection))
        for item in scores_attack:
            projection = fusion_machine(item.values()[0])
            key = item.keys()[0]
            f.write("%s %s %s %f\n" % (key[0:3], 'attack', key[6:], projection))
        f.close()


if __name__ == '__main__':
    main()
