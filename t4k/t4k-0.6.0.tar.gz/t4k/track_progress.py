def pc(fraction, decimals=2):
    formatter = '%%.%df %%%%' % decimals
    return formatter % (fraction*100)

def progress(i, total, period=1000, prefix=''):
	'''
	Prints a string representing the % completion when starting the
	`i`th step out of `total` steps, but only prints every `period` steps.
	'''
	if i % period == 0:
		print '%s%2.1f %%' % (prefix, i/float(total) * 100)
