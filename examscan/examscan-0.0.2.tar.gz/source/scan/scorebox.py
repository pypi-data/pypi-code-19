
import image_utils
import constants

def extract_scorebox(image):
	# Slice off the bottom of the page and rotate to make horizontal
	return image_utils.extract_box(image[-520: , 350:750], sides='NEW')

