'''
Reading the graders tickboxes at the bottom of the page.
Assumes a 400dpi images.
'''

import numpy as np
from examscan.scan import image_utils
from examscan.scan.errors import ScoreReadError
from examscan.scan.constants import PAPER

def extract_tickbox(image):
	# Slice off the bottom of the page and rotate to make horizontal
	return image_utils.extract_box(image[-480:-90, 650:3050])

def tick_box_locations(image):
	'''
	Estimate the locations of the tick boxes given the overall tickbox container.
	No image analysis is done here, just copying over the locations from the TikZ code.
	'''
	h, w = image.shape
	ys = [int(0.25*h), int(0.75*h)]
	
	start = w / 41.4285
	boxwidth = w / 18.125
	boxspacing = w / 11.1538
	xs = [(int(x), int(x+boxwidth)) for x in np.arange(start, w, boxspacing)]
	
	return xs, ys

def raw_read_tickboxes(score_area, show=True):
	''' Return a list of (black density of center box, black density of full box, tickbox number). '''
	xs, (y0, y1) = tick_box_locations(score_area)
	boxes = [score_area[y0:y1, x0:x1] for x0, x1 in xs]
	
	def center_box(x0, x1):
		y2 = int(0.75*y0 + 0.25*y1)
		y3 = int(0.25*y0 + 0.75*y1)
		x2 = int(0.75*x0 + 0.25*x1)
		x3 = int(0.25*x0 + 0.75*x1)
		return score_area[y2:y3, x2:x3]
	
	small_boxes = [center_box(x0, x1) for x0, x1 in xs]
	return [(image_utils.black_density(small_boxes[i]), image_utils.black_density(boxes[i]), i) for i in range(len(boxes))]

def winner(densities, column):
	data = sorted(densities, key=lambda x: x[column], reverse=True)
	return data[0][-1], data[0][column], data[0][column] / data[1][column]

def most_solid_big(densities):
	return max([(d[1] / d[0], d[-1]) for d in densities if d[0] > 0.25])

def read_tickbox(image):
	tb = extract_tickbox(image)
	densities = raw_read_tickboxes(tb)
	
	score_small, density_small, ratio_small = winner(densities, 0)
	score_big, density_big, ratio_big = winner(densities, 1)
	max_ratio = max(ratio_small, ratio_big)
	
	if density_small < 0.25:
		raise ScoreReadError('Boxes nearly blank')
	
	most_solid, score_solid = most_solid_big(densities)
	
	if most_solid > 0.7 and score_solid == score_big and ratio_big > 1.2:
		return score_big, ratio_big
	if score_small == score_big and max_ratio > 1.2:
		return score_small, max_ratio
	if ratio_small > 1.2:
		return score_small, ratio_small
	if ratio_big > 1.3:
		return score_big, ratio_big
	if ratio_small > 1.1 and density_small > 0.5:
		return score_small, ratio_small
	raise ScoreReadError('Ambiguous')

