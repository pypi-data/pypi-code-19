
import tempfile
from glob import glob
import pandas as pd
import numpy as np
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
# import matplotlib.pyplot as plt  # Delay.
from PyPDF2 import PdfFileWriter, PdfFileReader
try:
	from StringIO import StringIO
except ImportError:
	from io import StringIO

import os

from random import randint
import sys

def build_report(student, data, template, pages, output_dir):
	print(student['name'])
	template_vars = dict(student)
	template_vars.update(data)
	html_out = template.render(template_vars)
	output = StringIO()
	HTML(string=html_out).write_pdf(output)
	
	output_pdf = PdfFileWriter()
	output_pdf.addPage(PdfFileReader(output).getPage(0))
	
	for pdf in pages:
		with open(pdf, 'rb') as input_file:
			pdf_input = PdfFileReader(StringIO(input_file.read()))
			
			for page in pdf_input.pages:
				output_pdf.addPage(page)
	
	with open(os.path.join(output_dir, '%s.pdf' % student.netid), 'wb') as output_file:
		output_pdf.write(output_file)

def helper(X):
	return build_report(*X)

def main(results, template_path, output_dir):
	if not os.path.exists(output_dir):
		os.makedirs(output_dir)
	
	env = Environment(loader=FileSystemLoader('.'))
	template = env.get_template(template_path)
	
	import matplotlib.pyplot as plt
	histogram = os.path.abspath('./histogram.png')  # tempfile.TemporaryFile()
	n, bins, patches = plt.hist(list(results.score), 10, normed=1, facecolor='blue', alpha=0.5)
	plt.xlabel('Score')
	plt.ylabel('Frequency')
	plt.axes().get_yaxis().set_ticks([])
	plt.savefig(histogram)
	
	data = {
		'mean': round(results.score.mean(), 2),
		'median': round(results.score.median(), 1),
		#'mode': results.score.mode()[0],  # Pandas is weird.
		'sd': round(results.score.std(), 2),
		'min': results.score.min(),
		'max': results.score.max(),
		'histogram': 'file://' + histogram
		}
	
	to_do = [(student, data, template, glob('./tmp/exams/%d/*.pdf' % student['exam']), output_dir) for _, student in results.iterrows()]
	
	for X in to_do:
		helper(X)
	
	os.remove(histogram)

