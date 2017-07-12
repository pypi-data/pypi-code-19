"""
Script for plotting loss and accuracy from chainer logs

usage:
	> python -m chainer_addon.utils.plot <logfile> [-k <key1> <key2> ... <keyn> ]
"""

import sys, argparse

parser = argparse.ArgumentParser(description = "Plot loss and accuracy from chainer logs")
parser.add_argument("logfile", type=str, help="chainer log file to parse")
parser.add_argument("--key","-k", type=str, default=["main/accuracy", "main/loss"], nargs="+", help="key of the loss and accuracy values")
parser.add_argument("--fit", action="store_true", help="plot fitted graphs")
parser.add_argument("--all_in_one", "-aio", action="store_true", help="plot all graphs in one")

from os.path import join
from scipy.optimize import curve_fit
import simplejson as json, numpy as np
import matplotlib.pyplot as plt

def func(x, a, b, c):
	return a * np.exp(-b * x) + c

def non_zero(idxs, values):
	return list(zip(*[(idx, val) for idx, val in zip(idxs, values) if val != 0]))

def main(args):
	log_file = json.load(open(args.logfile))#[:200]
	data = {key: [] for key in args.key}
	validation_data = {key: [] for key in args.key}
	for log in log_file:
		for key in args.key:
			data[key].append(log.get(key, 0))
			if "validation" in key: continue
			val_key = "validation/{}".format(key)
			if val_key in log:
				validation_data[key].append(log.get(val_key, 0))


	for i, (key, values) in enumerate(data.items()):
		X = np.arange(len(values))

		if i == 0 or not args.all_in_one:
			fig = plt.figure(i)
			fig.canvas.set_window_title("{} - {}".format(args.logfile, key))
			ax = fig.add_subplot(1,1,1)
			ax.set_title(key if not args.all_in_one else "graphs")

		if (np.array(values) != 0).any():
			ax.plot(X, values, label=key)

		if args.fit:
			coefs = curve_fit(func, X, data)[0]
			ax.plot(X, [func(x, *coefs) for x in X], "r--")

		if validation_data[key]:
			ax.plot(X, validation_data[key], label=key + " val")

		ax.legend()

	plt.show()



main(parser.parse_args())


