'''
Reading off the UIN from the coversheets.
Assumes a 400dpi images.
'''

import numpy as np
from examscan.scan import image_utils
from examscan.scan.errors import ScoreReadError

NUM_DIGITS = 9
CHARS = '0123456789'

def extract_uin_box(image):
	# Slice off the bottom of the page and rotate to make horizontal
	return image_utils.extract_box(image[720:2400, 1700:3300], align='vertical')

def read_uin(page_image):
	# Get the UIN box.
	image = extract_uin_box(page_image)
	
	height, width = image.shape
	dy = height / 10.75  # Should change.
	dx = width / (NUM_DIGITS + 1)
	vertlines = [int(p) for p in np.arange(0.5 * dx, width, dx)]
	horlines = [int(p) for p in np.arange(0.25 * dy, height, dy)]  # Should change.
	
	densities = [sorted([(image_utils.black_density(box), char) for char, box in zip(CHARS, np.vsplit(column, horlines)[1:-1])], reverse=True) for column in np.hsplit(image, vertlines)[1:-1]]
	
	uin = [column[0][1] for column in densities]
	lightest = min(column[0][0] for column in densities)
	worst_ratio = max(column[0][0] / column[1][0] for column in densities)
	
	if worst_ratio < 1.1 or (lightest < 0.10 and worst_ratio < 2):
		raise ScoreReadError('UIN ambiguous (%f, %f)' % (worst_ratio, lightest))
	
	return ''.join(uin)

