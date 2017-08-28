#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Pavel Korshunov <pavel.korshunov@idiap.ch>
# Mon  7 Sep 15:19:22 CEST 2015
#

from __future__ import print_function

"""This script reads given score files (four column format), computes error rates, and plots DET curves"""

import bob.measure

import argparse
import numpy, math
import os
import os.path
import sys

import matplotlib.pyplot as mpl
import matplotlib.font_manager as fm

import bob.core
logger = bob.core.log.setup("bob.spoof.speech")


def load_attack_scores(filename, support="all", adevice="all", recdevice="all"):
  # split in positives and negatives
  positives = []
  negatives = []

  # read four column list line by line
  for (client_id, probe_id, filename, score) in bob.measure.load.four_column(filename):
      if client_id == probe_id:
          if (support in filename or support == "all") and \
                (adevice in filename or adevice == "all") and \
                (recdevice in filename or recdevice == "all"):
              positives.append(score)
      else:
          negatives.append(score)

  return (numpy.array(negatives, numpy.float64), numpy.array(positives, numpy.float64))


def plot_det_curves(scores_dev, scores_eval, outname):
    from matplotlib.backends.backend_pdf import PdfPages
    pdf_name = outname+'_det_curves.pdf'
    pp = PdfPages(pdf_name)

    fig = mpl.figure()
    ax1 = mpl.subplot(111)

    bob.measure.plot.det(scores_dev[0], scores_dev[1], 100,
                                            color='blue', linestyle='-', label='Dev set', linewidth=2)
    bob.measure.plot.det(scores_eval[0], scores_eval[1], 100,
                                            color='red', linestyle='--', label='Eval set', linewidth=2)

    bob.measure.plot.det_axis([0.1, 99, 0.1, 99])
    mpl.xlabel('FRR (%)')
    mpl.ylabel('FAR (%)')
    mpl.legend()
    mpl.grid()
    pp.savefig()
    pp.close()

def plot_histograms(settype, scores, threshold, outname, histbins_real=100, histbins_attacks=100, attack_scores=None, impostor_scores=None, attacktype="all", realtype="all"):

  from matplotlib.backends.backend_pdf import PdfPages

  pdf_name = outname + '_distributions_' + settype + '.pdf'
  pp = PdfPages(pdf_name)

  negatives = attack_scores
  positives = scores

  fig = mpl.figure()
  ax1 = mpl.subplot(111)

  mpl.rcParams.update({'font.size': 18})
  if attack_scores is not None:
    mpl.hist(attack_scores, bins=histbins_attacks, color='black', alpha=0.4, label="Spoofing Attacks", normed=True)
  mpl.hist(scores, bins=histbins_real, color='blue', alpha=0.6, label="Genuine Accesses", normed=True)

  # plot the line
  mpl.axvline(x=threshold, ymin=0, ymax=1, linewidth=2, color='black', linestyle='--', label="EER threshold")

  mpl.xlabel("Scores")
  mpl.ylabel("Normalized Count")

  # mpl.ylim([0, 0.10])
  # mpl.xlim([-80, 40])
  mpl.legend(loc='upper left', prop=fm.FontProperties(size=16))

  mpl.title("Score distributions and EER, %s set" % (settype))
  mpl.grid()
  pp.savefig()
  pp.close()


def command_line_arguments(command_line_parameters):
  """Parse the program options"""

  basedir = os.path.dirname(os.path.dirname(os.path.realpath(sys.argv[0])))
  OUTPUT_DIR = os.path.join(basedir, 'plots')

  # set up command line parser
  parser = argparse.ArgumentParser(description=__doc__,
      formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument('-d', '--real-dev-file', required=True, help = "The score file of the development set.")
  parser.add_argument('-e', '--real-eval-file', required=True, help = "The score files of the evaluation set.")
  parser.add_argument('-f', '--attacks-eval-file', type=str, required=True, help = "The score file with attacks scores.")
  parser.add_argument('-t', '--attacks-dev-file', type=str, required=True, help = "The score file with attacks scores.")
  parser.add_argument('-n', '--histogram-bins-real', required=False, type=int, default=20, help = "The number of bins in computed histogram of score distribution for real data.")
  parser.add_argument('-m', '--histogram-bins-attacks', required=False, type=int, default=20, help = "The number of bins in computed histogram of score distribution for spoof data.")
  parser.add_argument('-o', '--out-directory', dest="directory", default=OUTPUT_DIR, help="This path will be prepended to every file output by this procedure (defaults to '%(default)s')")
  parser.add_argument('-s', '--support', required=False, type=str, default="all", help = "Type of attack.")
  parser.add_argument('-k', '--attackdevice', required=False, type=str, default="all", help = "Attack device.")
  parser.add_argument('-r', '--device', required=False, type=str, default="all", help = "Recording device.")
  parser.add_argument('-b', '--session', required=False, type=str, default="all", help = "Recording session.")
  parser.add_argument('-p', '--pretty-title', required=False, type=str, help = "Title of the results. Default is the auto-generated file name.")

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

  if not os.path.exists(args.directory):
    os.makedirs(args.directory)

  histbins_real = int(args.histogram_bins_real)
  histbins_attacks = int(args.histogram_bins_attacks)

  ####################
  ## Read scores ###
  ####################
  print("Loading %s real score file of the development set" % (args.real_dev_file))
  scores_dev_zimp, scores_dev  = bob.measure.load.split_four_column(args.real_dev_file)
  print("Loading %s real score file of the evaluation set" % (args.real_eval_file))
  scores_eval_zimp, scores_eval = bob.measure.load.split_four_column(args.real_eval_file)


  support=args.support
  adevice=args.attackdevice
  recdevice=args.device

  attacktype = 'a:' + support+ ', ad:' + adevice # + ', rd:' + recdevice
  outname = 'attack_%s_adevice_%s' % (support, adevice)

  print("Loading %s score file of the development set with attacks" % (args.attacks_dev_file))
  scores_dev_attacks  = load_attack_scores(args.attacks_dev_file)[1] # only positive values

  print("Loading %s score file of the evaluation set with attacks" % (args.attacks_eval_file))
  scores_eval_attacks = load_attack_scores(args.attacks_eval_file, support, adevice, recdevice)[1]

  ####################
  ## Compute Stats ###
  ####################
  resfile = open(os.path.join(args.directory, outname+'_results.txt'), "w")
  # print the title of the experiment
  results_title = outname
  if args.pretty_title:
    results_title = args.pretty_title
  print (results_title)
  resfile.write(results_title + "\n")

  eer_threshold = bob.measure.eer_threshold(scores_dev_attacks, scores_dev)
  far, frr = bob.measure.farfrr(scores_dev_attacks, scores_dev, eer_threshold)
  print("Development set: FAR = %2.12f \t FRR = %2.12f \t HTER = %2.12f \t EER threshold = %2.12f" % (far, frr, (far+frr)/2, eer_threshold))
  resfile.write("Development set: FAR = %2.12f \t FRR = %2.12f \t EER threshold = %2.12f\n" % (far, frr, eer_threshold))

  sfar, sfrr = bob.measure.farfrr(scores_eval_attacks, scores_eval, eer_threshold)
  print("Evaluation set with attacks: %s, SFAR = %2.12f, SFRR = %2.12f, HTER = %2.12f \t " % (attacktype, sfar, sfrr, (sfar+sfrr)/2))
  resfile.write("Evaluation set with attacks: %s, SFAR = %2.12f, SFRR = %2.12f" % (attacktype, sfar, sfrr))
  resfile.close()

  ####################
  ## Plot graphs ###
  ####################

  outname = os.path.join(args.directory, outname)
  plot_histograms("Dev", scores_dev, eer_threshold, outname, histbins_real, histbins_attacks, scores_dev_attacks, scores_dev_zimp, attacktype=attacktype)
  plot_histograms("Eval", scores_eval, eer_threshold, outname, histbins_real, histbins_attacks, scores_eval_attacks, scores_eval_zimp, attacktype=attacktype)

  plot_det_curves([scores_dev_attacks, scores_dev], [scores_eval_attacks, scores_eval], outname)


if __name__ == '__main__':
    main()
