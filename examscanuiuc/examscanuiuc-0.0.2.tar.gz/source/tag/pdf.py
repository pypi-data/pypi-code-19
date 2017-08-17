
# Requires: pdftoppm

import tempfile
import shutil
import subprocess
import os
import glob
from PIL import Image

def images_from_pdf(file_path):
	directory = tempfile.mkdtemp()
	subprocess.call(['pdftoppm', '-tiff', file_path, os.path.join(directory, 'im')])
	images = [Image.open(file) for file in glob.glob(os.path.join(directory, 'im*.tif'))]
	shutil.rmtree(directory)
	return images

